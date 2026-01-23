from langchain_postgres.vectorstores import PGVector
from config import Config
import sqlalchemy as sa
from sqlalchemy import text
from logger import get_logger

logger = get_logger(__name__)

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
    logger.info(f"Conectando ao banco de dados: {Config.PG_VECTOR_COLLECTION_NAME}")
    return PGVector(
        embeddings=embeddings,
        collection_name=Config.PG_VECTOR_COLLECTION_NAME,
        connection=Config.DATABASE_URL,
        use_jsonb=True,
    )


def count_documents():
    """
    Conta o número de documentos no banco de dados vetorial de forma eficiente.
    
    Usa query SQL direta sem precisar gerar embeddings, tornando a operação
    muito mais rápida e econômica.
    
    Returns:
        int: Número de documentos no banco (0 se vazio ou erro)
    """
    try:
        # Criar engine do SQLAlchemy
        engine = sa.create_engine(Config.DATABASE_URL)
        
        # Query SQL com JOIN para filtrar por nome da coleção
        query = text("""
            SELECT COUNT(*) 
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :collection
        """)
        
        with engine.connect() as conn:
            logger.debug(f"Consultando contagem de documentos para a coleção: {Config.PG_VECTOR_COLLECTION_NAME}")
            result = conn.execute(query, {"collection": Config.PG_VECTOR_COLLECTION_NAME})
            count = result.scalar()
            logger.info(f"Contagem de documentos finalizada: {count} documentos encontrados")
            return count if count else 0
            
    except sa.exc.OperationalError as e:
        # Erro de conexão (ex: container desligado)
        logger.error(f"Falha de conexão com o banco de dados. Verifique se o container Postgres está rodando: {e}")
        return 0
    except sa.exc.ProgrammingError as e:
        # Erro de tabelas não encontradas (banco inicializado mas vazio/sem extensões)
        logger.warning(f"Tabelas não encontradas no banco de dados. Elas serão criadas na primeira ingestão. Detalhe: {e}")
        return 0
    except sa.exc.SQLAlchemyError as e:
        # Outros erros do SQLAlchemy
        logger.error(f"Erro inesperado do banco de dados: {e}")
        return 0
    except Exception as e:
        # Outros erros genéricos
        logger.error(f"Erro inesperado ao acessar o banco: {e}")
        return 0
    finally:
        if 'engine' in locals():
            engine.dispose()

