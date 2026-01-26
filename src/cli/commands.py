from __future__ import annotations
import os
import logging
from typing import Any, Optional

from sqlalchemy.exc import SQLAlchemyError
from search import search_prompt, search_with_sources
from database import get_vector_store
from ingest import ingest_pdf
from config import Config
from cli.ui import SECTION_LINE, HEADER_LINE, display_help

logger = logging.getLogger(__name__)

def check_database_status() -> tuple[int, int]:
    """
    Verifica quantos registros e arquivos existem no banco de dados vetorial.
    
    Returns:
        tuple: (num_chunks, num_sources)
    """
    try:
        from database import VectorStoreRepository
        repo = VectorStoreRepository()
        num_chunks = repo.count()
        num_sources = repo.count_sources()
        
        if num_chunks > 0:
            logger.info(f"Banco contém {num_chunks} chunks de {num_sources} arquivos")
        
        return num_chunks, num_sources
    except (ImportError, ModuleNotFoundError) as e:
        logger.error(f"Erro de dependência ao verificar status: {e}")
        return 0, 0
    except SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao verificar status: {e}")
        return 0, 0
    except Exception as e:
        logger.warning(f"Erro inesperado ao verificar o status do banco: {e}")
        return 0, 0

def handle_add_command(
    user_input: str,
    quiet: bool = False,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> bool:
    """
    Processa comando de adição de PDF ao banco.
    
    Args:
        user_input: Entrada completa do usuário (ex: "add document.pdf")
        quiet: Se True, oculta mensagens de progresso
        chunk_size: Tamanho do chunk (opcional)
        chunk_overlap: Sobreposição do chunk (opcional)
        
    Returns:
        bool: True se processado com sucesso, False caso contrário
    """
    parts = user_input.strip().split(maxsplit=1)
    
    if len(parts) < 2:
        if not quiet:
            print("❌ Erro: Você deve especificar o caminho do PDF.")
            print("   Uso: add <caminho_pdf>")
            print("   Exemplo: add document.pdf\n")
        return False
    
    pdf_path = parts[1].strip()
    
    # Validar se arquivo existe
    if not os.path.exists(pdf_path):
        if not quiet:
            print(f"❌ Erro: Arquivo não encontrado: {pdf_path}\n")
        return False
    
    # Validar extensão
    if not pdf_path.lower().endswith('.pdf'):
        if not quiet:
            print(f"❌ Erro: O arquivo deve ser um PDF (.pdf)\n")
        return False
    
    if not quiet:
        print(f"\n📄 Iniciando ingestão do PDF: {pdf_path}")
        print(SECTION_LINE)
    
    try:
        # 1. Inicializar Repositório para verificar existência
        from database import VectorStoreRepository
        repo = VectorStoreRepository()
        
        # 2. Verificar se o arquivo já foi ingerido
        if repo.source_exists(pdf_path):
            if not quiet:
                print(f"⚠️  O arquivo '{pdf_path}' já existe na base de dados.")
                confirm = input("Deseja sobrescrever os dados existentes? (sim/n): ").strip().lower()
                if confirm != 'sim':
                    print("Operação cancelada pelo usuário.\n")
                    return False
                print("Limpando dados antigos e re-ingerindo...\n")
            # Se quiet=True, prossegue sem perguntar (sobrescreve por padrão)

        # 3. Reutilizar lógica do ingest.py
        success = ingest_pdf(pdf_path, quiet=quiet, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        if success:
            if not quiet:
                print(SECTION_LINE)
                print("✅ PDF adicionado com sucesso ao banco de dados!\n")
            return True
        else:
            if not quiet:
                print(SECTION_LINE)
                print("❌ Falha ao adicionar PDF ao banco de dados.\n")
            return False
            
    except (IOError, OSError) as e:
        if not quiet:
            print(SECTION_LINE)
            print(f"❌ Erro de sistema/arquivo ao processar PDF: {e}\n")
        return False
    except SQLAlchemyError as e:
        if not quiet:
            print(SECTION_LINE)
            print(f"❌ Erro de banco de dados ao salvar PDF: {e}\n")
        return False
    except Exception as e:
        if not quiet:
            print(SECTION_LINE)
            print(f"❌ Erro inesperado ao processar PDF: {e}\n")
        logger.error(f"Erro inesperado na ingestão: {e}", exc_info=True)
        return False

def handle_remove_command(user_input: str) -> None:
    """
    Processa a remoção de um arquivo específico da base.
    
    Args:
        user_input: Entrada do usuário (ex: 'remove document.pdf')
    """
    parts = user_input.strip().split(maxsplit=1)
    
    if len(parts) < 2:
        print("❌ Erro: Você deve especificar o nome do arquivo a ser removido.")
        print("   Uso: remove <nome_arquivo>")
        return
    
    source_name = parts[1].strip()
    
    from database import VectorStoreRepository
    repo = VectorStoreRepository()
    
    # Verificar se o arquivo existe na base
    # O source no metadados pode ser o caminho completo ou apenas o nome
    # Vamos listar as fontes para validar
    sources = repo.list_sources()
    
    # Tentar encontrar correspondência exata ou pelo nome do arquivo
    target_source = None
    for src in sources:
        if src == source_name or os.path.basename(src) == source_name:
            target_source = src
            break
            
    if not target_source:
        print(f"⚠️  Arquivo '{source_name}' não encontrado na base de dados.")
        print("💡 Use o comando 'stats' para ver a lista de arquivos disponíveis.")
        return

    print(f"\n⚠️  Você está prestes a remover TODOS os dados relacionados a: {target_source}")
    confirm = input("Tem certeza que deseja continuar? (sim/n): ").strip().lower()
    
    if confirm == 'sim':
        if repo.delete_by_source(target_source):
            print(f"✅ Arquivo '{source_name}' removido com sucesso!\n")
        else:
            print(f"❌ Erro ao remover o arquivo '{source_name}'.\n")
    else:
        print("Operação cancelada.\n")

def handle_stats_command() -> None:
    """
    Exibe estatísticas detalhadas do banco de dados.
    """
    from database import VectorStoreRepository
    repo = VectorStoreRepository()
    
    num_chunks = repo.count()
    sources = repo.list_sources()
    num_sources = len(sources)
    
    print("\n" + HEADER_LINE)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print(HEADER_LINE)
    
    if num_chunks == 0:
        print("A base de dados está vazia.")
    else:
        print(f"🔹 Total de trechos (chunks): {num_chunks}")
        print(f"🔹 Total de arquivos:        {num_sources}")
        
        if sources:
            print("\n📄 Arquivos na base:")
            for i, src in enumerate(sources, 1):
                # Tentar extrair apenas o nome do arquivo se for um caminho
                filename = os.path.basename(src)
                print(f"   {i}. {filename} ({src})")
    
    print(HEADER_LINE + "\n")

def handle_clear_command() -> bool:
    """
    Processa o comando de limpeza da base de dados com confirmação.
    
    Returns:
        bool: True se a base foi limpa, False caso contrário
    """
    from database import VectorStoreRepository
    repo = VectorStoreRepository()
    
    # Verificar se já não está vazio para evitar confirmação desnecessária
    if repo.count() == 0:
        print("💡 O banco de dados já está vazio. Nada para limpar.\n")
        return False

    confirm = input("⚠️  CERTEZA que deseja limpar toda a base? (sim/n): ").strip().lower()
    if confirm == 'sim':
        if repo.clear():
            print("✅ Base de dados limpa com sucesso!\n")
            return True
        else:
            print("❌ Erro ao limpar a base.\n")
            return False
    else:
        print("Operação cancelada.\n")
        return False

def process_question(
    chain: Any,
    question: str,
    quiet: bool = False,
    verbose: bool = False,
    top_k: Optional[int] = None,
    temperature: Optional[float] = None,
) -> None:
    """
    Processa uma pergunta usando a chain do RAG.
    
    Args:
        chain: Chain do LangChain configurada
        question: Pergunta do usuário
        quiet: Se True, oculta indicadores de progresso
        verbose: Se True, mostra estatísticas detalhadas da resposta
        top_k: Número de documentos a recuperar (opcional)
        temperature: Temperatura para geração (opcional)
    """
    try:
        import time
        start_time = time.time()
        
        if not quiet:
            # Mostrar etapas do processo
            print("🔍 Recuperando informações relevantes...")
            print("🧠 Gerando resposta baseada nos documentos...\n")
        
        if verbose:
            # Usar search_with_sources para obter detalhes dos chunks
            # Passar top_k e temperature se fornecidos, senão usar os do Config via default da função
            kwargs: dict[str, Any] = {}
            if top_k is not None: kwargs['top_k'] = top_k
            if temperature is not None: kwargs['temperature'] = temperature
            
            result = search_with_sources(question, **kwargs)
            response = result["answer"]
            sources = result["sources"]
            end_time = time.time()
            elapsed_time = end_time - start_time
        else:
            response = chain.invoke(question)
            end_time = time.time()
            elapsed_time = end_time - start_time
            sources = []
        
        if not quiet:
            print(SECTION_LINE)
            print(f"PERGUNTA: {question}")
            print(SECTION_LINE)
            print(f"RESPOSTA: {response}")
            
            if verbose:
                print(SECTION_LINE)
                print(f"📊 ESTATÍSTICAS DA RESPOSTA:")
                print(f"⏱️  Tempo de execução: {elapsed_time:.2f}s")
                if sources:
                    print(f"📚 Fontes utilizadas ({len(sources)}):")
                    for spec in sources:
                        page_info = f", pág. {spec['page']}" if spec['page'] is not None else ""
                        print(f"   • {spec['filename']}{page_info}")
            
            print(SECTION_LINE + "\n")
        else:
            # Em modo quieto, mostra apenas a resposta pura para facilitar automação
            print(response)
            if verbose:
                # Se for verbose E quiet, mostra estatísticas mínimas
                print(f"--- Stats: {elapsed_time:.2f}s | {len(sources)} sources ---")
        
    except (KeyboardInterrupt, EOFError):
        # Captura interrupção voluntária (Ctrl+C ou Ctrl+D) sem explodir o log
        raise
    except SQLAlchemyError as e:
        print(f"❌ Erro crítico de banco de dados: {e}\n")
        logger.error(f"Erro de banco no processamento: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao processar pergunta: {e}\n")
        logger.error(f"Erro detalhado ao processar pergunta: {e}", exc_info=True)
