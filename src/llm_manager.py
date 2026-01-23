"""
Módulo Manager de LLM

Implementa o padrão Singleton para garantir que o modelo de linguagem (LLM)
seja instanciado apenas uma vez e fornece abstração de provedor (Google/OpenAI).
"""

from config import Config
from logger import get_logger

logger = get_logger(__name__)

class LLMManager:
    """
    Gerencia a instância do modelo LLM.
    """
    _instance = None

    @classmethod
    def get_llm(cls):
        """
        Retorna a instância do modelo LLM, criando-a se necessário.
        A escolha do provedor é baseada na configuração disponível no Config.
        """
        if cls._instance is None:
            # Tentar Google primeiro (prioridade conforme Config.API_KEY)
            if Config.GOOGLE_API_KEY:
                try:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    logger.info(f"Inicializando LLM Google: {Config.GOOGLE_LLM_MODEL}")
                    cls._instance = ChatGoogleGenerativeAI(
                        model=Config.GOOGLE_LLM_MODEL,
                        google_api_key=Config.GOOGLE_API_KEY,
                        temperature=Config.RETRIEVAL_TEMPERATURE
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar LLM Google: {e}")
                    raise
            
            # Senão, tentar OpenAI
            elif Config.OPENAI_API_KEY:
                try:
                    from langchain_openai import ChatOpenAI
                    logger.info(f"Inicializando LLM OpenAI: {Config.OPENAI_LLM_MODEL}")
                    cls._instance = ChatOpenAI(
                        model=Config.OPENAI_LLM_MODEL,
                        api_key=Config.OPENAI_API_KEY,
                        temperature=Config.RETRIEVAL_TEMPERATURE
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar LLM OpenAI: {e}")
                    raise
            
            else:
                raise ValueError(
                    "Nenhuma API Key configurada. Defina GOOGLE_API_KEY ou OPENAI_API_KEY no .env"
                )
                
        return cls._instance


def get_llm():
    """
    Função de conveniência para obter o modelo LLM seguindo o padrão Singleton.
    """
    return LLMManager.get_llm()
