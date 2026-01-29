from __future__ import annotations

import os
from typing import Any, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import get_vector_store
from config import Config
from embeddings_manager import get_embeddings
from logger import get_logger

import logging

logger = get_logger(__name__)

DISPLAY_WIDTH = 70
DEFAULT_BATCH_SIZE = 16

def normalize_pdf_path(path: str) -> str:
    """
    Normaliza o caminho do PDF para persistência consistente no banco.
    Favoriza caminhos relativos à raiz do projeto se o arquivo estiver dentro dele.
    """
    if not path:
        return path
    
    # Obter caminho absoluto real (resolve symlinks e ..)
    abs_path = os.path.realpath(path)
    
    try:
        # Tentar calcular caminho relativo à raiz do projeto
        rel_path = os.path.relpath(abs_path, Config.PROJECT_ROOT)
        
        # Se não subir níveis (não começar com ..), usamos o relativo
        if not rel_path.startswith('..'):
            return rel_path
    except (ValueError, AttributeError):
        pass
    
    return abs_path

def ingest_pdf(
    pdf_path: Optional[str] = None,
    quiet: bool = False,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> bool:
    """
    Ingere um arquivo PDF, dividindo em chunks e persistindo embeddings no PGVector.

    Este fluxo executa:
    - carregamento do PDF
    - chunking (tamanho e overlap configuráveis)
    - enriquecimento de metadados por chunk
    - limpeza de dados antigos da mesma fonte (source)
    - persistência no banco vetorial em lotes

    Args:
        pdf_path: Caminho do PDF para ingestão. Se None, usa `Config.PDF_PATH`.
        quiet: Se True, reduz logs e desabilita barras de progresso.
        chunk_size: Sobrescreve `Config.CHUNK_SIZE` (em caracteres) se informado.
        chunk_overlap: Sobrescreve `Config.CHUNK_OVERLAP` (em caracteres) se informado.

    Returns:
        True se o processo concluir com sucesso.

    Raises:
        ValueError: Se `pdf_path` e `Config.PDF_PATH` estiverem ausentes, ou se nenhum texto for extraído.
        FileNotFoundError: Se o arquivo não existir no caminho informado.

    Examples:
        Ingestão padrão usando PDF do `.env`:

        >>> from ingest import ingest_pdf
        >>> ingest_pdf()
        True

        Ingestão com parâmetros customizados:

        >>> ingest_pdf("document.pdf", chunk_size=1000, chunk_overlap=150)
        True
    """
    # Validar configuração
    Config.validate_config()

    # Validar parâmetros de chunking
    c_size = chunk_size or Config.CHUNK_SIZE
    c_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    if c_size <= 0:
        raise ValueError(f"Tamanho do chunk inválido: {c_size}. Deve ser maior que 0.")
    if c_overlap < 0:
        raise ValueError(f"Sobreposição do chunk inválida: {c_overlap}. Não pode ser negativa.")
    if c_overlap >= c_size:
        raise ValueError(f"Sobreposição ({c_overlap}) deve ser menor que o tamanho do chunk ({c_size}).")
    
    # Se modo silencioso, ajustar nível de log globalmente
    if quiet:
        from logger import set_global_log_level
        set_global_log_level(logging.WARNING)
    
    # Fallback para variável de ambiente se não for passado parâmetro
    input_pdf = pdf_path or Config.PDF_PATH
    
    if not input_pdf:
        raise ValueError("Caminho do PDF não especificado. Passe como parâmetro ou configure PDF_PATH no .env")

    # Caminho absoluto para todas as operações de arquivo
    abs_pdf_path = os.path.abspath(input_pdf)
    
    # Caminho normalizado (preferencialmente relativo ao projeto) para metadados e logs
    storage_pdf_path = normalize_pdf_path(abs_pdf_path)

    # 1. Carregamento do PDF
    logger.info(f"Iniciando carregamento do PDF: {storage_pdf_path}")
    if not os.path.exists(abs_pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {storage_pdf_path}")
    
    # Validar extensão
    if not abs_pdf_path.lower().endswith('.pdf'):
        raise TypeError(f"O arquivo deve ter extensão .pdf: {storage_pdf_path}")
        
    loader = PyPDFLoader(abs_pdf_path)
    docs: list[Document] = loader.load()
    logger.info(f"PDF carregado com sucesso. Total de páginas: {len(docs)}")

    # 2. Chunking do texto
    logger.info("Dividindo o texto em fragmentos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or Config.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or Config.CHUNK_OVERLAP
    )
    splits: list[Document] = text_splitter.split_documents(docs)
    
    if not splits:
        raise ValueError("Nenhum texto pôde ser extraído do PDF. O arquivo pode estar vazio ou protegido.")
    
    logger.info(f"Texto dividido em {len(splits)} fragmentos.")

    # 3. Enriquecimento e Limpeza de Metadados
    filename = os.path.basename(abs_pdf_path)
    total_chunks = len(splits)
    logger.info(f"Enriquecendo metadados para {total_chunks} fragmentos...")
    
    from tqdm import tqdm
    
    enriched_docs: list[Document] = []
    ids: list[str] = []
    
    # Usando tqdm para mostrar progresso no processamento de metadados
    for i, doc in enumerate(tqdm(splits, desc="Processando fragmentos", unit="chunk", disable=quiet)):
        # Limpar metadados nulos/vazios
        meta: dict[str, Any] = {k: v for k, v in doc.metadata.items() if v not in ("", None)}
        
        # Adicionar novos metadados
        chunk_id = f"{filename}-{i}"
        meta["chunk_id"] = chunk_id
        meta["chunk_index"] = i
        meta["total_chunks"] = total_chunks
        meta["filename"] = filename
        meta["source"] = storage_pdf_path
        
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
    logger.info(f"Limpando dados antigos da fonte: {storage_pdf_path}...")
    repo.delete_by_source(storage_pdf_path)

    # 7. Inserção ou Atualização no Banco (com barra de progresso e batching)
    batch_size = DEFAULT_BATCH_SIZE  # Tamanho do lote para enviar ao banco/embedding
    
    # Forçar inicialização do vector_store fora do loop para não quebrar o visual da barra de progresso
    _ = repo.vector_store
    
    logger.info(f"Enviando {len(enriched_docs)} fragmentos para o PGVector em lotes de {batch_size}...")
    
    for i in tqdm(range(0, len(enriched_docs), batch_size), desc="Gerando embeddings e salvando", unit="batch", disable=quiet):
        batch_docs = enriched_docs[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        repo.add_documents(batch_docs, ids=batch_ids)

    logger.info("PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ✅")
    
    # Exibir estatísticas finais (apenas se não estiver em modo silencioso)
    if not quiet:
        avg_chunk_size = sum(len(d.page_content) for d in enriched_docs) / total_chunks if total_chunks > 0 else 0
        
        print("\n" + "=" * DISPLAY_WIDTH)
        print("📊 ESTATÍSTICAS DE INGESTÃO")
        print("=" * DISPLAY_WIDTH)
        print(f"📄 Arquivo:           {filename}")
        print(f"📑 Total de Páginas:   {len(docs)}")
        print(f"🧱 Total de Chunks:    {total_chunks}")
        print(f"📏 Tamanho Médio:      {avg_chunk_size:.1f} caracteres")
        print(f"🆔 Chunks IDs:         {filename}-0 até {filename}-{total_chunks-1}")
        print(f"🔗 Banco de Dados:     {Config.PG_VECTOR_COLLECTION_NAME}")
        print("=" * DISPLAY_WIDTH + "\n")
    
    return True

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Ingestão de PDFs no PGVector')
    parser.add_argument('pdf_path', nargs='?', help='Caminho do PDF para ingestão', default=Config.PDF_PATH)
    parser.add_argument('-q', '--quiet', action='store_true', help='Modo silencioso: oculta logs e progresso')
    parser.add_argument('--chunk-size', type=int, help=f'Tamanho do chunk (default: {Config.CHUNK_SIZE})')
    parser.add_argument('--chunk-overlap', type=int, help=f'Sobreposição do chunk (default: {Config.CHUNK_OVERLAP})')
    
    args = parser.parse_args()
    
    pdf_to_ingest = args.pdf_path
    
    try:
        if pdf_to_ingest:
            from database import VectorStoreRepository
            repo = VectorStoreRepository()
            
            # Normalizar apenas para a busca de existência no banco
            pdf_normalized = normalize_pdf_path(pdf_to_ingest)
            
            if repo.source_exists(pdf_normalized):
                if not args.quiet:
                    print(f"\n⚠️  O arquivo '{pdf_normalized}' já existe na base de dados.")
                    try:
                        confirm = input("Deseja sobrescrever os dados existentes? (sim/n): ").strip().lower()
                        if confirm != 'sim':
                            print("Operação cancelada pelo usuário.")
                            sys.exit(0)
                    except EOFError:
                        pass
        
        ingest_pdf(pdf_to_ingest, quiet=args.quiet, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    except FileNotFoundError as e:
        print(f"❌ Erro: {e}")
        sys.exit(2)
    except ValueError as e:
        print(f"❌ Erro de validação: {e}")
        sys.exit(2)
    except TypeError as e:
        print(f"❌ Erro de formato: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)