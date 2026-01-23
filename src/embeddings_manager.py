"""
Módulo Manager de Embeddings

Implementa o padrão Singleton para garantir que o modelo de embeddings
seja instanciado apenas uma vez e fornece abstração de provedor (Google/OpenAI).
"""

from config import Config
from logger import get_logger

logger = get_logger(__name__)

class EmbeddingsManager:
    """
    Gerencia a instância do modelo de embeddings.
    """
    _instance = None

    @classmethod
    def get_embeddings(cls):
        """
        Retorna a instância do modelo de embeddings, criando-a se necessário.
        A escolha do provedor é baseada na configuração disponível no Config.
        """
        if cls._instance is None:
            # Tentar Google primeiro (prioridade conforme Config.API_KEY)
            if Config.GOOGLE_API_KEY:
                try:
                    from langchain_google_genai import GoogleGenerativeAIEmbeddings
                    logger.info(f"Inicializando embeddings Google: {Config.GOOGLE_EMBEDDING_MODEL}")
                    cls._instance = GoogleGenerativeAIEmbeddings(
                        model=Config.GOOGLE_EMBEDDING_MODEL,
                        google_api_key=Config.GOOGLE_API_KEY
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar embeddings Google: {e}")
                    raise
            
            # Senão, tentar OpenAI
            elif Config.OPENAI_API_KEY:
                try:
                    from langchain_openai import OpenAIEmbeddings
                    logger.info(f"Inicializando embeddings OpenAI: {Config.OPENAI_EMBEDDING_MODEL}")
                    cls._instance = OpenAIEmbeddings(
                        model=Config.OPENAI_EMBEDDING_MODEL,
                        api_key=Config.OPENAI_API_KEY
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar embeddings OpenAI: {e}")
                    raise
            
            else:
                raise ValueError(
                    "Nenhuma API Key configurada. Defina GOOGLE_API_KEY ou OPENAI_API_KEY no .env"
                )
                
        return cls._instance


def get_embeddings():
    """
    Função de conveniência para obter o modelo de embeddings seguindo o padrão Singleton.
    """
    return EmbeddingsManager.get_embeddings()
