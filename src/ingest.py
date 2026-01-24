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
    # Garantimos que não existam metadados nulos ou vazios que possam quebrar o banco
    enriched_docs = [
        type(doc)(
            page_content=doc.page_content,
            metadata={k: v for k, v in doc.metadata.items() if v not in ("", None)},
        )
        for doc in splits
    ]
    
    # 4. Geração de IDs Determinísticos (Cenário A: Nome do Arquivo + Índice)
    # Isso garante que documentos de arquivos diferentes não colidam mesmo que tenham o mesmo índice.
    filename = os.path.basename(target_pdf)
    ids = [f"{filename}-{i}" for i in range(len(enriched_docs))]
    logger.info(f"Gerados {len(ids)} IDs únicos para o arquivo {filename}.")

    # 5. Embeddings e Vetorização
    logger.info("Preparando inserção no banco de dados vetorial...")
    embeddings = get_embeddings()

    # Inicialização via Repositório
    from database import VectorStoreRepository
    repo = VectorStoreRepository(embeddings)

    # 6. Limpeza de dados antigos para esta fonte (Evita chunks órfãos se o número de chunks mudar)
    logger.info(f"Limpando dados antigos da fonte: {target_pdf}...")
    repo.delete_by_source(target_pdf)

    # 7. Inserção ou Atualização no Banco
    logger.info(f"Enviando {len(enriched_docs)} fragmentos para o PGVector...")
    repo.add_documents(enriched_docs, ids=ids)
    logger.info("PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ✅")
    return True

if __name__ == "__main__":
    ingest_pdf()