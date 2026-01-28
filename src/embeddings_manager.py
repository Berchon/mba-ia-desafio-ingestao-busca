"""
Módulo Manager de Embeddings

Implementa o padrão Singleton para garantir que o modelo de embeddings
seja instanciado apenas uma vez e fornece abstração de provedor (Google/OpenAI).
"""

from __future__ import annotations

from typing import Any, Optional

from config import Config
from logger import get_logger

logger = get_logger(__name__)

class EmbeddingsManager:
    """
    Gerencia a instância do modelo de embeddings.
    """
    _instance: Optional[Any] = None

    @classmethod
    def reset(cls) -> None:
        """
        Reseta a instância do singleton, forçando recreação na próxima chamada.
        Útil quando há troca dinâmica de provedor.
        """
        logger.debug("Resetando instância de EmbeddingsManager")
        cls._instance = None

    @classmethod
    def get_embeddings(cls) -> Any:
        """
        Retorna a instância do modelo de embeddings, criando-a se necessário.
        A escolha do provedor é baseada na configuração disponível no Config.

        Returns:
            Instância do modelo de embeddings do provedor selecionado (Google ou OpenAI).

        Raises:
            ValueError: Se nenhuma API key estiver configurada em `Config`.
            Exception: Se houver falha ao importar/inicializar o provider (propaga o erro).

        Examples:
            >>> from embeddings_manager import get_embeddings
            >>> emb = get_embeddings()
            >>> emb is not None
            True
        """
        if cls._instance is None:
            # Determinar qual provedor usar
            use_google = False
            use_openai = False
            
            # 1. Verificar se há provedor forçado
            if Config._FORCED_PROVIDER == 'google':
                use_google = True
            elif Config._FORCED_PROVIDER == 'openai':
                use_openai = True
            # 2. Detecção automática (Google > OpenAI)
            else:
                if Config.GOOGLE_API_KEY:
                    use_google = True
                elif Config.OPENAI_API_KEY:
                    use_openai = True
                else:
                    raise ValueError("Nenhuma API Key configurada. Defina GOOGLE_API_KEY ou OPENAI_API_KEY no .env")

            # Inicialização baseada na decisão acima
            if use_google:
                try:
                    from langchain_google_genai import GoogleGenerativeAIEmbeddings
                    model_name = Config.GOOGLE_EMBEDDING_MODEL
                    # Garantir o prefixo models/ se não estiver presente
                    if not model_name.startswith("models/"):
                        model_name = f"models/{model_name}"
                        
                    logger.info(f"Inicializando embeddings Google: {model_name}")
                    cls._instance = GoogleGenerativeAIEmbeddings(
                        model=model_name,
                        google_api_key=Config.GOOGLE_API_KEY
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar embeddings Google: {e}")
                    if "429" in str(e):
                        logger.error("DICA: Erro 429 indica que sua cota da API foi atingida ou o limite de requisições por minuto foi excedido.")
                    raise
            
            elif use_openai:
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
                
        return cls._instance


def get_embeddings() -> Any:
    """
    Função de conveniência para obter o modelo de embeddings seguindo o padrão Singleton.

    Returns:
        Instância do modelo de embeddings do provedor selecionado.

    Raises:
        ValueError: Se nenhuma API key estiver configurada.
    """
    return EmbeddingsManager.get_embeddings()
