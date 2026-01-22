import os
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from database import get_vector_store

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Variáveis de Ambiente
PDF_PATH = os.getenv("PDF_PATH")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004")

def ingest_pdf(pdf_path: str = None):
    # Fallback para variável de ambiente se não for passado parâmetro
    target_pdf = pdf_path or PDF_PATH
    
    if not all([target_pdf, GOOGLE_API_KEY]):
        raise ValueError("Configurações insuficientes. Verifique o arquivo .env (PDF_PATH e GOOGLE_API_KEY) ou passe o caminho do PDF.")

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
        chunk_size=1000,
        chunk_overlap=150
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
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Inicialização via camada de banco
    db = get_vector_store(embeddings)

    # 6. Inserção ou Atualização no Banco
    logger.info(f"Enviando {len(enriched_docs)} fragmentos para o PGVector...")
    db.add_documents(enriched_docs, ids=ids)
    logger.info("PROCESSO DE INGESTÃO CONCLUÍDO COM SUCESSO! ✅")
    return True

if __name__ == "__main__":
    ingest_pdf()