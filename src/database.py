from __future__ import annotations

from typing import Any, Optional, Sequence

from langchain_postgres.vectorstores import PGVector
from config import Config
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import Engine
from logger import get_logger

logger = get_logger(__name__)

class VectorStoreRepository:
    """
    Repositório centralizado para operações no banco de dados vetorial (PGVector).
    Implementa o padrão Repository para abstrair o acesso aos dados.
    """
    
    def __init__(self, embeddings: Optional[Any] = None) -> None:
        """
        Inicializa o repositório.
        
        Args:
            embeddings: O modelo de embeddings a ser utilizado. 
                       Se None, algumas operações que não exigem embeddings (como count) 
                       ainda funcionarão.
        """
        self.embeddings: Optional[Any] = embeddings
        self._vector_store: Optional[PGVector] = None
        self._engine: Optional[Engine] = None

    @property
    def vector_store(self) -> PGVector:
        """Retorna a instância do PGVector, inicializando-a se necessário."""
        if self._vector_store is None:
            if self.embeddings is None:
                raise ValueError("Embeddings não fornecidos. Necessário para operações de Vector Store.")
            
            if not all([Config.DATABASE_URL, Config.PG_VECTOR_COLLECTION_NAME]):
                raise ValueError("Configurações de banco não encontradas no .env")

            logger.info(f"Conectando ao banco de dados: {Config.PG_VECTOR_COLLECTION_NAME}")
            self._vector_store = PGVector(
                embeddings=self.embeddings,
                collection_name=Config.PG_VECTOR_COLLECTION_NAME,
                connection=Config.DATABASE_URL,
                use_jsonb=True,
            )
        return self._vector_store

    @property
    def engine(self) -> Engine:
        """Retorna o engine do SQLAlchemy, inicializando-o se necessário."""
        if self._engine is None:
            # Config.DATABASE_URL é Optional[str]; em runtime isso deve estar configurado.
            self._engine = sa.create_engine(Config.DATABASE_URL)  # type: ignore[arg-type]
        return self._engine

    def count(self) -> int:
        """
        Conta o número de documentos na coleção atual de forma eficiente via SQL.
        
        Returns:
            int: Número de documentos (0 se vazio ou erro)
        """
        query = text("""
            SELECT COUNT(*) 
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :collection
        """)
        
        try:
            with self.engine.connect() as conn:
                logger.debug(f"Consultando contagem de documentos para a coleção: {Config.PG_VECTOR_COLLECTION_NAME}")
                result = conn.execute(query, {"collection": Config.PG_VECTOR_COLLECTION_NAME})
                count = result.scalar()
                logger.info(f"Contagem de documentos finalizada: {count} documentos encontrados")
                return count if count else 0
        except sa.exc.OperationalError as e:
            logger.error(f"Falha de conexão com o banco de dados: {e}")
            return 0
        except sa.exc.ProgrammingError as e:
            logger.warning(f"Tabelas não encontradas (banco inicializado mas vazio). Detalhe: {e}")
            return 0
        except Exception as e:
            logger.error(f"Erro inesperado ao contar documentos: {e}")
            return 0

    def count_sources(self) -> int:
        """
        Conta o número de fontes únicas (arquivos) na coleção.
        
        Returns:
            int: Número de fontes (0 se vazio ou erro)
        """
        query = text("""
            SELECT COUNT(DISTINCT e.cmetadata->>'source') 
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :collection
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"collection": Config.PG_VECTOR_COLLECTION_NAME})
                count = result.scalar()
                return count if count else 0
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao contar fontes: {e}")
            return 0
        except Exception as e:
            logger.error(f"Erro inesperado ao contar fontes: {e}")
            return 0

    def list_sources(self) -> list[str]:
        """
        Lista todas as fontes únicas (arquivos) na coleção.
        
        Returns:
            list: Lista de nomes de arquivos/fontes
        """
        query = text("""
            SELECT DISTINCT e.cmetadata->>'source'
            FROM langchain_pg_embedding e
            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
            WHERE c.name = :collection
            ORDER BY e.cmetadata->>'source'
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"collection": Config.PG_VECTOR_COLLECTION_NAME})
                return [row[0] for row in result if row[0]]
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao listar fontes: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao listar fontes: {e}")
            return []

    def exists(self) -> bool:
        """Verifica se existem documentos na coleção."""
        return self.count() > 0

    def clear(self) -> bool:
        """
        Remove todos os documentos da coleção atual.
        
        Returns:
            bool: True se removido com sucesso, False caso contrário
        """
        try:
            # O PGVector tem um método para deletar a coleção, mas aqui queremos 
            # limpar apenas os documentos da coleção específica.
            # No langchain-postgres/PGVector, podemos usar o delete() se tivermos os IDs,
            # ou recriar a coleção se quisermos limpar tudo.
            
            # Uma forma segura via SQL de limpar apenas a coleção atual:
            query_find_id = text("SELECT uuid FROM langchain_pg_collection WHERE name = :name")
            query_delete = text("DELETE FROM langchain_pg_embedding WHERE collection_id = :uuid")
            
            with self.engine.connect() as conn:
                with conn.begin():
                    result = conn.execute(query_find_id, {"name": Config.PG_VECTOR_COLLECTION_NAME})
                    collection_uuid = result.scalar()
                    if collection_uuid:
                        conn.execute(query_delete, {"uuid": collection_uuid})
                        logger.info(f"Coleção '{Config.PG_VECTOR_COLLECTION_NAME}' limpa com sucesso.")
                        return True
            return False
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao limpar banco: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao limpar banco: {e}")
            return False

    def delete_by_source(self, source: str) -> bool:
        """
        Remove todos os chunks que tenham o mesmo 'source' no metadados.
        
        Args:
            source (str): O caminho/nome do arquivo (metadata['source'])
            
        Returns:
            bool: True se a operação foi concluída (mesmo que nada tenha sido deletado)
        """
        query = text("""
            DELETE FROM langchain_pg_embedding 
            WHERE cmetadata->>'source' = :source
            AND collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = :collection)
        """)
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    logger.info(f"Removendo documentos antigos da fonte: {source}")
                    result = conn.execute(query, {
                        "source": source,
                        "collection": Config.PG_VECTOR_COLLECTION_NAME
                    })
                    logger.info(f"Removidos {result.rowcount} chunks antigos de '{source}'.")
                    return True
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao deletar por fonte ({source}): {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao deletar por fonte ({source}): {e}")
            return False

    def source_exists(self, source: str) -> bool:
        """
        Verifica se já existem documentos de uma fonte específica.
        
        Args:
            source (str): O caminho/nome do arquivo (metadata['source'])
            
        Returns:
            bool: True se existirem documentos, False caso contrário
        """
        query = text("""
            SELECT EXISTS (
                SELECT 1 FROM langchain_pg_embedding 
                WHERE cmetadata->>'source' = :source
                AND collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = :collection)
            )
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {
                    "source": source,
                    "collection": Config.PG_VECTOR_COLLECTION_NAME
                })
                return bool(result.scalar())
        except sa.exc.SQLAlchemyError as e:
            logger.error(f"Erro de banco de dados ao verificar existência ({source}): {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar existência ({source}): {e}")
            return False

    def add_documents(self, documents: Sequence[Any], ids: Optional[Sequence[str]] = None) -> Any:
        """Adiciona documentos ao vector store."""
        return self.vector_store.as_upsert().add_documents(documents, ids=ids) if hasattr(self.vector_store, 'as_upsert') else self.vector_store.add_documents(documents, ids=ids)

    def as_retriever(self, **kwargs: Any) -> Any:
        """Retorna o vector store como um retriever."""
        return self.vector_store.as_retriever(**kwargs)

# Funções de compatibilidade (Legacy) para não quebrar o código existente imediatamente
def get_vector_store(embeddings: Any) -> PGVector:
    repo = VectorStoreRepository(embeddings)
    return repo.vector_store

def count_documents() -> int:
    repo = VectorStoreRepository()
    return repo.count()
