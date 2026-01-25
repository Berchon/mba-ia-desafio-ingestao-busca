"""
Módulo de Configuração Centralizada

Este módulo centraliza todas as variáveis de ambiente e configurações do projeto RAG,
eliminando duplicação e facilitando manutenção.
"""

from __future__ import annotations

import os
from typing import ClassVar, Optional

from dotenv import load_dotenv

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
    
    # === Propriedades Agnósticas ao Provedor ===
    # Estas propriedades retornam automaticamente os valores corretos
    # baseados em qual provedor (Google ou OpenAI) está configurado
    
    @classmethod
    @property
    def API_KEY(cls) -> str:
        """
        Retorna a API key disponível (Google ou OpenAI).
        Prioriza Google se ambas estiverem configuradas.
        
        Raises:
            ValueError: Se nenhuma API key estiver configurada.
        """
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
        Retorna o modelo de embedding apropriado baseado na API key disponível.
        Se Google API key está configurada, retorna modelo Google.
        Caso contrário, retorna modelo OpenAI.
        
        Raises:
            ValueError: Se nenhuma API key estiver configurada.
        """
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
        Retorna o modelo LLM apropriado baseado na API key disponível.
        Se Google API key está configurada, retorna modelo Google.
        Caso contrário, retorna modelo OpenAI.
        
        Raises:
            ValueError: Se nenhuma API key estiver configurada.
        """
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
        print("\n" + "="*70)
        print("⚙️  CONFIGURAÇÕES DO SISTEMA")
        print("="*70)
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
        print("="*70 + "\n")
