import os
from dotenv import load_dotenv
from langchain_postgres.vectorstores import PGVector

load_dotenv()

# Variáveis de Conexão
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")

def get_vector_store(embeddings):
    """
    Retorna uma instância configurada do PGVector (Vector Store).
    
    Args:
        embeddings: O modelo de embeddings a ser utilizado.
        
    Returns:
        PGVector: Instância do Vector Store do LangChain.
    """
    if not all([DATABASE_URL, COLLECTION_NAME]):
        raise ValueError("Configurações de banco (DATABASE_URL ou COLLECTION_NAME) não encontradas no .env")

    # Inicialização do Vector Store usando langchain-postgres
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True,
    )
