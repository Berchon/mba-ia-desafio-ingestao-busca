"""
Módulo de Configuração Centralizada

Este módulo centraliza todas as variáveis de ambiente e configurações do projeto RAG,
eliminando duplicação e facilitando manutenção.
"""

from __future__ import annotations

import os
from typing import ClassVar, Optional

from dotenv import load_dotenv

# Largura padrão de exibição para separadores no terminal
DISPLAY_WIDTH: int = 70

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """
    Classe centralizada de configuração do projeto.
    
    Todas as variáveis de ambiente são carregadas como atributos de classe,
    permitindo acesso consistente em todo o projeto via Config.NOME_VARIAVEL.
    """
    
    # === API Keys ===
    GOOGLE_API_KEY: ClassVar[Optional[str]] = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY: ClassVar[Optional[str]] = os.getenv("OPENAI_API_KEY")
    
    # === Modelos Google Gemini ===
    GOOGLE_EMBEDDING_MODEL: ClassVar[str] = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
    GOOGLE_LLM_MODEL: ClassVar[str] = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")
    
    # === Modelos OpenAI ===
    OPENAI_EMBEDDING_MODEL: ClassVar[str] = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_LLM_MODEL: ClassVar[str] = os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano")
    
    # === Configurações do Banco de Dados ===
    DATABASE_URL: ClassVar[Optional[str]] = os.getenv("DATABASE_URL")
    PG_VECTOR_COLLECTION_NAME: ClassVar[Optional[str]] = os.getenv("PG_VECTOR_COLLECTION_NAME")
    
    # === Configurações de Ingestão ===
    PDF_PATH: ClassVar[Optional[str]] = os.getenv("PDF_PATH")
    CHUNK_SIZE: ClassVar[int] = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: ClassVar[int] = int(os.getenv("CHUNK_OVERLAP", "150"))
    
    # === Configurações de Busca/Retrieval ===
    TOP_K: ClassVar[int] = int(os.getenv("TOP_K", "10"))
    RETRIEVAL_TEMPERATURE: ClassVar[float] = float(os.getenv("RETRIEVAL_TEMPERATURE", "0"))
    SEARCH_TIMEOUT: ClassVar[int] = int(os.getenv("SEARCH_TIMEOUT", "30"))  # Timeout em segundos
    
    # === Controle de Provedor ===
    _FORCED_PROVIDER: ClassVar[Optional[str]] = None

    @classmethod
    def set_provider(cls, provider: str) -> None:
        """
        Define forçadamente qual provedor usar ('google' ou 'openai').
        
        Args:
            provider: Nome do provedor ('google' ou 'openai')
        
        Raises:
            ValueError: Se o provedor for desconhecido ou se a chave dele não estiver configurada.
        """
        provider = provider.lower().strip()
        if provider not in ['google', 'openai']:
            raise ValueError(f"Provedor desconhecido: '{provider}'. Use 'google' ou 'openai'.")
            
        if provider == 'google' and not cls.GOOGLE_API_KEY:
            raise ValueError("Provedor 'google' selecionado, mas GOOGLE_API_KEY não está configurada no .env.")
            
        if provider == 'openai' and not cls.OPENAI_API_KEY:
            raise ValueError("Provedor 'openai' selecionado, mas OPENAI_API_KEY não está configurada no .env.")
            
        cls._FORCED_PROVIDER = provider

    @classmethod
    @property
    def API_KEY(cls) -> str:
        """
        Retorna a API key disponível (Google ou OpenAI).
        Prioriza provedor forçado via set_provider(), senão Google, senão OpenAI.
        
        Raises:
            ValueError: Se nenhuma API key estiver configurada.
        """
        # 1. Verificar provedor forçado
        if cls._FORCED_PROVIDER == 'google':
            return cls.GOOGLE_API_KEY
        if cls._FORCED_PROVIDER == 'openai':
            return cls.OPENAI_API_KEY
            
        # 2. Detecção automática (Google > OpenAI)
        key = cls.GOOGLE_API_KEY or cls.OPENAI_API_KEY
        if not key:
            raise ValueError(
                "Nenhuma API key configurada. Configure GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env"
            )
        return key
    
    @classmethod
    @property
    def EMBEDDING_MODEL(cls) -> str:
        """
        Retorna o modelo de embedding apropriado.
        """
        # 1. Verificar provedor forçado
        if cls._FORCED_PROVIDER == 'google':
            return cls.GOOGLE_EMBEDDING_MODEL
        if cls._FORCED_PROVIDER == 'openai':
            return cls.OPENAI_EMBEDDING_MODEL

        # 2. Detecção automática
        if cls.GOOGLE_API_KEY:
            return cls.GOOGLE_EMBEDDING_MODEL
        elif cls.OPENAI_API_KEY:
            return cls.OPENAI_EMBEDDING_MODEL
        else:
            raise ValueError(
                "Nenhuma API key configurada. Configure GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env"
            )
    
    @classmethod
    @property
    def LLM_MODEL(cls) -> str:
        """
        Retorna o modelo LLM apropriado.
        """
        # 1. Verificar provedor forçado
        if cls._FORCED_PROVIDER == 'google':
            return cls.GOOGLE_LLM_MODEL
        if cls._FORCED_PROVIDER == 'openai':
            return cls.OPENAI_LLM_MODEL
            
        # 2. Detecção automática
        if cls.GOOGLE_API_KEY:
            return cls.GOOGLE_LLM_MODEL
        elif cls.OPENAI_API_KEY:
            return cls.OPENAI_LLM_MODEL
        else:
            raise ValueError(
                "Nenhuma API key configurada. Configure GOOGLE_API_KEY ou OPENAI_API_KEY no arquivo .env"
            )
    
    @classmethod
    def validate_config(cls) -> None:
        """
        Valida se todas as variáveis de ambiente críticas estão configuradas.
        
        Raises:
            ValueError: Se alguma variável crítica estiver ausente ou vazia.
        """
        missing_vars = []
        
        # Validar API Keys - pelo menos uma deve estar presente
        if not cls.GOOGLE_API_KEY and not cls.OPENAI_API_KEY:
            missing_vars.append("GOOGLE_API_KEY ou OPENAI_API_KEY (pelo menos uma)")
        
        # Validar configurações do banco de dados
        if not cls.DATABASE_URL:
            missing_vars.append("DATABASE_URL")
        
        if not cls.PG_VECTOR_COLLECTION_NAME:
            missing_vars.append("PG_VECTOR_COLLECTION_NAME")
        
        # Se houver variáveis faltando, lançar erro com mensagem clara
        if missing_vars:
            raise ValueError(
                f"Configurações críticas ausentes no arquivo .env:\n"
                f"  - {', '.join(missing_vars)}\n\n"
                f"Por favor, configure estas variáveis no arquivo .env antes de continuar.\n"
                f"Veja o arquivo .env.example para referência."
            )
    
    @classmethod
    def display_config(cls) -> None:
        """
        Exibe as configurações atuais (útil para debug).
        Oculta valores sensíveis como API keys.
        """
        print("\n" + "=" * DISPLAY_WIDTH)
        print("⚙️  CONFIGURAÇÕES DO SISTEMA")
        print("=" * DISPLAY_WIDTH)
        print(f"Google Embedding Model: {cls.GOOGLE_EMBEDDING_MODEL}")
        print(f"Google LLM Model: {cls.GOOGLE_LLM_MODEL}")
        print(f"OpenAI Embedding Model: {cls.OPENAI_EMBEDDING_MODEL}")
        print(f"Database Collection: {cls.PG_VECTOR_COLLECTION_NAME}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"Top K Results: {cls.TOP_K}")
        print(f"Retrieval Temperature: {cls.RETRIEVAL_TEMPERATURE}")
        print(f"Google API Key: {'✅ Configurada' if cls.GOOGLE_API_KEY else '❌ Ausente'}")
        print(f"OpenAI API Key: {'✅ Configurada' if cls.OPENAI_API_KEY else '❌ Ausente'}")
        print(f"Database URL: {'✅ Configurada' if cls.DATABASE_URL else '❌ Ausente'}")
        print("=" * DISPLAY_WIDTH + "\n")
