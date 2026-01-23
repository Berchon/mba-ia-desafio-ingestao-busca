from langchain_postgres.vectorstores import PGVector
from config import Config

def get_vector_store(embeddings):
    """
    Retorna uma instância configurada do PGVector (Vector Store).
    
    Args:
        embeddings: O modelo de embeddings a ser utilizado.
        
    Returns:
        PGVector: Instância do Vector Store do LangChain.
    """
    if not all([Config.DATABASE_URL, Config.PG_VECTOR_COLLECTION_NAME]):
        raise ValueError("Configurações de banco (DATABASE_URL ou PG_VECTOR_COLLECTION_NAME) não encontradas no .env")

    # Inicialização do Vector Store usando langchain-postgres
    return PGVector(
        embeddings=embeddings,
        collection_name=Config.PG_VECTOR_COLLECTION_NAME,
        connection=Config.DATABASE_URL,
        use_jsonb=True,
    )

