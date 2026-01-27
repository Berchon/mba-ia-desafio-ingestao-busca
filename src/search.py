from __future__ import annotations

import os
from typing import Any, Optional, TypedDict

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from sqlalchemy.exc import SQLAlchemyError
from database import get_vector_store
from config import Config
from embeddings_manager import get_embeddings
from llm_manager import get_llm
from logger import get_logger

logger = get_logger(__name__)

# Template do Prompt padrão (conforme requisitos.md)
DEFAULT_PROMPT_TEMPLATE: str = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def load_prompt_template(template_path: Optional[str] = None) -> str:
    """
    Carrega um template de prompt de um arquivo externo ou retorna o padrão.
    
    Args:
        template_path: Caminho para o arquivo de template (opcional)
        
    Returns:
        String do template de prompt
        
    Raises:
        FileNotFoundError: Se o arquivo especificado não existir
        
    Examples:
        >>> template = load_prompt_template()  # Usa padrão
        >>> template = load_prompt_template("prompts/custom.txt")  # Usa customizado
    """
    if template_path:
        if not os.path.exists(template_path):
            logger.error(f"Template não encontrado: {template_path}")
            raise FileNotFoundError(f"Arquivo de template não encontrado: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
                logger.info(f"Template customizado carregado: {template_path}")
                
                # Validar que o template contém as variáveis necessárias
                if '{contexto}' not in template or '{pergunta}' not in template:
                    logger.warning(f"Template pode estar incompleto. Certifique-se de incluir {{contexto}} e {{pergunta}}")
                
                return template
        except (IOError, OSError) as e:
            logger.error(f"Erro ao ler template: {e}")
            raise
    
    logger.info("Usando template padrão")
    return DEFAULT_PROMPT_TEMPLATE


class SourceSpec(TypedDict):
    filename: Optional[str]
    page: Optional[int]
    source: Optional[str]


class SearchWithSourcesResult(TypedDict):
    answer: str
    sources: list[SourceSpec]


def search_prompt(
    top_k: int = Config.TOP_K,
    temperature: Optional[float] = None,
    template_path: Optional[str] = None
) -> Optional[Any]:
    """
    Cria e retorna uma chain LangChain configurada para realizar busca semântica 
    e responder perguntas baseadas no contexto recuperado do banco vetorial.
    
    Args:
        top_k: Número de documentos a recuperar (default: Config.TOP_K)
        temperature: Temperatura para geração do LLM (opcional)
        template_path: Caminho para template customizado (opcional)
        
    Returns:
        Chain configurada do LangChain (pronta para `.invoke()`), ou None em caso de erro.

    Examples:
        >>> from search import search_prompt
        >>> chain = search_prompt(top_k=10, temperature=0)
        >>> chain is not None
        True
    """
    try:
        # 1. Inicializar Embeddings
        embeddings = get_embeddings()
        
        # 2. Conectar ao Repositório
        from database import VectorStoreRepository
        repo = VectorStoreRepository(embeddings)
        
        # 3. Criar Retriever
        retriever = repo.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
        
        # 4. Inicializar LLM
        llm = get_llm(temperature=temperature)
        
        # 5. Carregar template de prompt
        prompt_template_str = load_prompt_template(template_path)
        
        # 6. Criar o Prompt Template
        prompt = PromptTemplate(
            template=prompt_template_str,
            input_variables=["contexto", "pergunta"]
        )
        
        # 7. Função para formatar documentos recuperados
        def format_docs(docs: list[Document]) -> str:
            """Concatena o conteúdo dos documentos recuperados"""
            return "\n\n".join(doc.page_content for doc in docs)
        
        # 8. Criar a Chain (Retriever → Format → Prompt → LLM → Parser)
        chain = (
            {
                "contexto": retriever | format_docs,
                "pergunta": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        logger.info("Chain de busca criada com sucesso!")
        return chain
    
    except FileNotFoundError as e:
        logger.error(f"Erro ao carregar template: {e}")
        return None
    except ValueError as e:
        logger.error(f"Erro de configuração ou parâmetros na busca: {e}")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao criar chain: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao criar a chain de busca: {e}", exc_info=True)
        return None

def search_with_sources(
    question: str,
    top_k: int = Config.TOP_K,
    temperature: Optional[float] = None,
    template_path: Optional[str] = None,
) -> SearchWithSourcesResult:
    """
    Realiza a busca, gera a resposta e retorna também as fontes utilizadas.
    
    Args:
        question: Pergunta do usuário
        top_k: Número de documentos a recuperar
        temperature: Temperatura da LLM
        template_path: Caminho para template customizado (opcional)
        
    Returns:
        Dicionário contendo:
        - `answer`: resposta gerada
        - `sources`: lista de metadados das fontes utilizadas (arquivo/página)

    Examples:
        >>> from search import search_with_sources
        >>> result = search_with_sources("Qual o faturamento?", top_k=10, temperature=0)
        >>> "answer" in result and "sources" in result
        True
    """
    try:
        # 1. Inicializar Embeddings
        embeddings = get_embeddings()
        
        # 2. Conectar ao Repositório
        from database import VectorStoreRepository
        repo = VectorStoreRepository(embeddings)
        
        # 3. Recuperar documentos
        # 3. Recuperar documentos
        try:
            docs: list[Document] = repo.vector_store.similarity_search(question, k=top_k)
        except Exception as e:
            # Se falhar na busca (ex: API key inválida para embeddings), não há documentos para fallback.
            error_str = str(e)
            if "API key not valid" in error_str or "400" in error_str:
                logger.warning(f"Falha de autenticação na busca: {e}")  # Warning em vez de Error para não alarmar no console
                return {
                    "answer": "❌ **Erro de Autenticação**: Sua API KEY parece inválida ou expirada. Verifique seu arquivo .env.",
                    "sources": []
                }
            
            logger.error(f"Erro na etapa de busca (Retrieval): {e}")
            raise e # Relança outros erros para o except geral abaixo
        
        # 4. Formatar contexto
        def format_docs(docs: list[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)
        
        contexto = format_docs(docs)
        
        # 5. Tentar Gerar resposta com LLM (com Fallback)
        try:
            # Inicializar LLM
            llm = get_llm(temperature=temperature)
            
            # Carregar template de prompt
            prompt_template_str = load_prompt_template(template_path)
            
            # Criar o Prompt Template
            prompt = PromptTemplate(
                template=prompt_template_str,
                input_variables=["contexto", "pergunta"]
            )
            
            # Gerar resposta
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({"contexto": contexto, "pergunta": question})
            
        except Exception as e:
            logger.warning(f"Falha na execução da LLM: {e}. Ativando Fallback.")
            
            # Construir resposta de fallback
            answer = (
                "⚠️ **Aviso: O serviço de IA está instável ou indisponível no momento.**\n\n"
                "Abaixo estão os trechos mais relevantes encontrados nos documentos que podem ajudar:\n\n"
                "--- Contexto Recuperado ---\n\n"
            )
            answer += contexto
        
        # 9. Extrair fontes (metadados únicos)
        sources: list[SourceSpec] = []
        seen_sources: set[str] = set()
        for doc in docs:
            # Criar identificador único para a fonte (arquivo + página)
            source_id = f"{doc.metadata.get('source', 'desconhecido')}_p{doc.metadata.get('page', '??')}"
            if source_id not in seen_sources:
                sources.append({
                    "filename": doc.metadata.get("filename", doc.metadata.get("source")),
                    "page": doc.metadata.get("page") if isinstance(doc.metadata.get("page"), int) else None,
                    "source": doc.metadata.get("source")
                })
                seen_sources.add(source_id)
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except ValueError as e:
        logger.error(f"Erro de parâmetros na busca com fontes: {e}")
        return {
            "answer": f"Lamento, erro de configuração: {str(e)}",
            "sources": []
        }
    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados na busca: {e}")
        return {
            "answer": "Lamento, ocorreu um erro ao consultar o banco de dados.",
            "sources": []
        }
    except Exception as e:
        logger.error(f"Erro inesperado na busca com fontes: {e}", exc_info=True)
        return {
            "answer": f"Lamento, ocorreu um erro inesperado ao processar sua pergunta.",
            "sources": []
        }