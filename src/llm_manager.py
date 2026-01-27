"""
Módulo Manager de LLM

Implementa o padrão Singleton para garantir que o modelo de linguagem (LLM)
seja instanciado apenas uma vez e fornece abstração de provedor (Google/OpenAI).
"""

from __future__ import annotations

from typing import Any, Optional

from config import Config
from logger import get_logger

logger = get_logger(__name__)

class LLMManager:
    """
    Gerencia a instância do modelo LLM.
    """
    _instance: Optional[Any] = None

    @classmethod
    def reset(cls) -> None:
        """
        Reseta a instância do singleton, forçando recreação na próxima chamada.
        Útil quando há troca dinâmica de provedor.
        """
        logger.debug("Resetando instância de LLMManager")
        cls._instance = None

    @classmethod
    def get_llm(cls, temperature: Optional[float] = None) -> Any:
        """
        Retorna a instância do modelo LLM, criando-a se necessário.
        A escolha do provedor é baseada na configuração disponível no Config.
        
        Args:
            temperature: Temperatura para geração (opcional). Se None, usa Config.RETRIEVAL_TEMPERATURE.

        Returns:
            Instância do modelo de chat do provedor selecionado (Google ou OpenAI).

        Raises:
            ValueError: Se nenhuma API key estiver configurada em `Config`.
            Exception: Se houver falha ao importar/inicializar o provider (propaga o erro).

        Examples:
            >>> from llm_manager import get_llm
            >>> llm = get_llm(temperature=0)
            >>> llm is not None
            True
        """
        target_temp = temperature if temperature is not None else Config.RETRIEVAL_TEMPERATURE
        
        # Se pedirem uma temperatura diferente da que já temos instanciada, resetamos para forçar a mudança
        if cls._instance is not None:
            current_temp = getattr(cls._instance, 'temperature', None)
            if temperature is not None and current_temp != temperature:
                logger.debug(f"Redefinindo LLM para nova temperatura: {temperature}")
                cls._instance = None

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

            if use_google:
                try:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    logger.info(f"Inicializando LLM Google: {Config.GOOGLE_LLM_MODEL} (temp={target_temp})")
                    cls._instance = ChatGoogleGenerativeAI(
                        model=Config.GOOGLE_LLM_MODEL,
                        google_api_key=Config.GOOGLE_API_KEY,
                        temperature=target_temp
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar LLM Google: {e}")
                    raise
            
            elif use_openai:
                try:
                    from langchain_openai import ChatOpenAI
                    logger.info(f"Inicializando LLM OpenAI: {Config.OPENAI_LLM_MODEL} (temp={target_temp})")
                    cls._instance = ChatOpenAI(
                        model=Config.OPENAI_LLM_MODEL,
                        api_key=Config.OPENAI_API_KEY,
                        temperature=target_temp
                    )
                except Exception as e:
                    logger.error(f"Erro ao inicializar LLM OpenAI: {e}")
                    raise
                
        return cls._instance


def get_llm(temperature: Optional[float] = None) -> Any:
    """
    Função de conveniência para obter o modelo LLM seguindo o padrão Singleton.
    
    Args:
        temperature: Temperatura para geração (opcional).

    Returns:
        Instância do modelo de chat do provedor selecionado.

    Raises:
        ValueError: Se nenhuma API key estiver configurada.
    """
    return LLMManager.get_llm(temperature=temperature)
