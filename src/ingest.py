import os
import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database import get_vector_store
from config import Config
from embeddings_manager import get_embeddings

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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
    
    # 4. Geração de IDs Determinísticos
    # Isso permite que, se rodarmos o mesmo PDF, ele atualize os dados em vez de duplicar
    ids = [f"doc-{i}" for i in range(len(enriched_docs))]

    # 5. Embeddings e Vetorização
    logger.info("Preparando inserção no banco de dados vetorial...")
    embeddings = get_embeddings()

    # Inicialização via camada de banco
    db = get_vector_store(embeddings)

    # 6. Inserção ou Atualização no Banco
    logger.info(f"Enviando {len(enriched_docs)} fragmentos para o PGVector...")
    db.add_documents(enriched_docs, ids=ids)
    logger.info("PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ✅")
    return True

if __name__ == "__main__":
    ingest_pdf()