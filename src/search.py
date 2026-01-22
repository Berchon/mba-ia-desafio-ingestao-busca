import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from database import get_vector_store

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Variáveis de Ambiente
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/text-embedding-004")
LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")

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

def search_prompt(question=None):
    """
    Cria e retorna uma chain LangChain configurada para realizar busca semântica 
    e responder perguntas baseadas no contexto recuperado do banco vetorial.
    
    Args:
        question: A pergunta do usuário (opcional, usado para validação inicial)
        
    Returns:
        RunnableSequence: Chain configurada do LangChain (pronta para .invoke())
    """
    if not GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY não encontrada no arquivo .env")
        return None
    
    try:
        # 1. Inicializar Embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        # 2. Conectar ao Vector Store
        vector_store = get_vector_store(embeddings)
        
        # 3. Criar Retriever (k=10 conforme requisitos)
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )
        
        # 4. Inicializar LLM
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=0,  # Respostas determinísticas baseadas no contexto
        )
        
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
        
    except Exception as e:
        logger.error(f"Erro ao criar a chain de busca: {e}")
        return None