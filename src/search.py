from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from database import get_vector_store
from config import Config
from embeddings_manager import get_embeddings
from llm_manager import get_llm
from logger import get_logger

logger = get_logger(__name__)

# Template do Prompt (conforme requisitos.md)
PROMPT_TEMPLATE = """
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

def search_prompt(top_k=Config.TOP_K, temperature=None):
    """
    Cria e retorna uma chain LangChain configurada para realizar busca semântica 
    e responder perguntas baseadas no contexto recuperado do banco vetorial.
    
    Args:
        top_k: Número de documentos a recuperar (default: Config.TOP_K)
        temperature: Temperatura para geração do LLM (opcional)
        
    Returns:
        RunnableSequence: Chain configurada do LangChain (pronta para .invoke())
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
        
        # 5. Criar o Prompt Template
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["contexto", "pergunta"]
        )
        
        # 6. Função para formatar documentos recuperados
        def format_docs(docs):
            """Concatena o conteúdo dos documentos recuperados"""
            return "\n\n".join(doc.page_content for doc in docs)
        
        # 7. Criar a Chain (Retriever → Format → Prompt → LLM → Parser)
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
        
    except ValueError as e:
        logger.error(f"Erro de configuração ou parâmetros na busca: {e}")
        return None
    except sa.exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao criar chain: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao criar a chain de busca: {e}", exc_info=True)
        return None

def search_with_sources(question, top_k=Config.TOP_K, temperature=None):
    """
    Realiza a busca, gera a resposta e retorna também as fontes utilizadas.
    
    Args:
        question: Pergunta do usuário
        top_k: Número de documentos a recuperar
        temperature: Temperatura da LLM
        
    Returns:
        dict: Dicionário contendo 'answer' (str) e 'sources' (list)
    """
    try:
        # 1. Inicializar Embeddings
        embeddings = get_embeddings()
        
        # 2. Conectar ao Repositório
        from database import VectorStoreRepository
        repo = VectorStoreRepository(embeddings)
        
        # 3. Recuperar documentos
        docs = repo.vector_store.similarity_search(question, k=top_k)
        
        # 4. Formatar contexto
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        contexto = format_docs(docs)
        
        # 5. Inicializar LLM
        llm = get_llm(temperature=temperature)
        
        # 6. Criar o Prompt Template
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["contexto", "pergunta"]
        )
        
        # 7. Gerar resposta
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"contexto": contexto, "pergunta": question})
        
        # 8. Extrair fontes (metadados únicos)
        sources = []
        seen_sources = set()
        for doc in docs:
            # Criar identificador único para a fonte (arquivo + página)
            source_id = f"{doc.metadata.get('source', 'desconhecido')}_p{doc.metadata.get('page', '??')}"
            if source_id not in seen_sources:
                sources.append({
                    "filename": doc.metadata.get("filename", doc.metadata.get("source")),
                    "page": doc.metadata.get("page"),
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
    except sa.exc.SQLAlchemyError as e:
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