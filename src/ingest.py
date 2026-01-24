import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import get_vector_store
from config import Config
from embeddings_manager import get_embeddings
from logger import get_logger

logger = get_logger(__name__)

def ingest_pdf(pdf_path: str = None):
    # Validar configuração
    Config.validate_config()
    
    # Fallback para variável de ambiente se não for passado parâmetro
    target_pdf = pdf_path or Config.PDF_PATH
    
    if not target_pdf:
        raise ValueError("Caminho do PDF não especificado. Passe como parâmetro ou configure PDF_PATH no .env")

    # 1. Carregamento do PDF
    logger.info(f"Iniciando carregamento do PDF: {target_pdf}")
    if not os.path.exists(target_pdf):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {target_pdf}")
        
    loader = PyPDFLoader(target_pdf)
    docs = loader.load()
    logger.info(f"PDF carregado com sucesso. Total de páginas: {len(docs)}")

    # 2. Chunking do texto
    logger.info("Dividindo o texto em fragmentos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(docs)
    
    if not splits:
        raise ValueError("Nenhum texto pôde ser extraído do PDF. O arquivo pode estar vazio ou protegido.")
    
    logger.info(f"Texto dividido em {len(splits)} fragmentos.")

    # 3. Enriquecimento e Limpeza de Metadados
    filename = os.path.basename(target_pdf)
    total_chunks = len(splits)
    logger.info(f"Enriquecendo metadados para {total_chunks} fragmentos...")
    
    from tqdm import tqdm
    
    enriched_docs = []
    ids = []
    
    # Usando tqdm para mostrar progresso no processamento de metadados
    for i, doc in enumerate(tqdm(splits, desc="Processando fragmentos", unit="chunk")):
        # Limpar metadados nulos/vazios
        meta = {k: v for k, v in doc.metadata.items() if v not in ("", None)}
        
        # Adicionar novos metadados
        chunk_id = f"{filename}-{i}"
        meta["chunk_id"] = chunk_id
        meta["chunk_index"] = i
        meta["total_chunks"] = total_chunks
        meta["filename"] = filename
        
        # Criar novo objeto documento com metadados enriquecidos
        enriched_docs.append(type(doc)(
            page_content=doc.page_content,
            metadata=meta
        ))
        ids.append(chunk_id)

    logger.info(f"Gerados {len(ids)} IDs únicos e metadados enriquecidos para o arquivo {filename}.")

    # 5. Embeddings e Vetorização
    logger.info("Preparando inserção no banco de dados vetorial...")
    embeddings = get_embeddings()

    # Inicialização via Repositório
    from database import VectorStoreRepository
    repo = VectorStoreRepository(embeddings)

    # 6. Limpeza de dados antigos para esta fonte (Evita chunks órfãos se o número de chunks mudar)
    logger.info(f"Limpando dados antigos da fonte: {target_pdf}...")
    repo.delete_by_source(target_pdf)

    # 7. Inserção ou Atualização no Banco (com barra de progresso e batching)
    batch_size = 16  # Tamanho do lote para enviar ao banco/embedding
    
    # Forçar inicialização do vector_store fora do loop para não quebrar o visual da barra de progresso
    _ = repo.vector_store
    
    logger.info(f"Enviando {len(enriched_docs)} fragmentos para o PGVector em lotes de {batch_size}...")
    
    for i in tqdm(range(0, len(enriched_docs), batch_size), desc="Gerando embeddings e salvando", unit="batch"):
        batch_docs = enriched_docs[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        repo.add_documents(batch_docs, ids=batch_ids)

    logger.info("PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ✅")
    
    # Exibir estatísticas finais
    avg_chunk_size = sum(len(d.page_content) for d in enriched_docs) / total_chunks if total_chunks > 0 else 0
    
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DE INGESTÃO")
    print("="*70)
    print(f"📄 Arquivo:           {filename}")
    print(f"📑 Total de Páginas:   {len(docs)}")
    print(f"🧱 Total de Chunks:    {total_chunks}")
    print(f"📏 Tamanho Médio:      {avg_chunk_size:.1f} caracteres")
    print(f"🆔 Chunks IDs:         {filename}-0 até {filename}-{total_chunks-1}")
    print(f"🔗 Banco de Dados:     {Config.PG_VECTOR_COLLECTION_NAME}")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    import sys
    
    # Se houver argumento, usa ele, senão usa o do Config
    pdf_to_ingest = sys.argv[1] if len(sys.argv) > 1 else Config.PDF_PATH
    
    if pdf_to_ingest:
        from database import VectorStoreRepository
        repo = VectorStoreRepository()
        
        if repo.source_exists(pdf_to_ingest):
            print(f"\n⚠️  O arquivo '{pdf_to_ingest}' já existe na base de dados.")
            try:
                confirm = input("Deseja sobrescrever os dados existentes? (sim/n): ").strip().lower()
                if confirm != 'sim':
                    print("Operação cancelada pelo usuário.")
                    sys.exit(0)
            except EOFError:
                # Se não for interativo (ex: em um pipe), prossegue
                pass
                
    ingest_pdf(pdf_to_ingest)