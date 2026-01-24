import sys
import os
import argparse
import logging
from search import search_prompt, search_with_sources
from database import get_vector_store
from ingest import ingest_pdf
from config import Config
from embeddings_manager import get_embeddings
from logger import get_logger

logger = get_logger(__name__, level=logging.WARNING)


def check_database_status():
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
    except sa.exc.SQLAlchemyError as e:
        logger.error(f"Erro de banco de dados ao verificar status: {e}")
        return 0, 0
    except Exception as e:
        logger.warning(f"Erro inesperado ao verificar o status do banco: {e}")
        return 0, 0


def display_welcome(counts):
    """
    Exibe mensagem de boas-vindas com status do banco.
    
    Args:
        counts: Tupla (num_chunks, num_sources)
    """
    num_chunks, num_sources = counts
    print("\n" + "="*70)
    print("🤖 CHAT RAG - Sistema de Busca Semântica com LangChain")
    print("="*70)
    
    if num_chunks > 0:
        plural_files = "arquivos" if num_sources > 1 else "arquivo"
        print(f"✅ Status: Banco conectado com {num_chunks} trechos de {num_sources} {plural_files}")
    else:
        print("⚠️  Status: Banco de dados vazio")
        print("💡 Dica: Use o comando 'add <caminho_pdf>' para adicionar documentos")
    
    print("\nDigite 'help' para ver os comandos disponíveis.")
    print("="*70 + "\n")


def display_help():
    """
    Exibe a lista de comandos disponíveis.
    """
    print("\n" + "="*70)
    print("📚 COMANDOS DISPONÍVEIS")
    print("="*70)
    print("\n🔍 FAZER PERGUNTAS:")
    print("   Digite sua pergunta diretamente (ex: 'Qual o faturamento?')")
    print("   O sistema buscará respostas baseadas nos PDFs ingeridos.")
    
    print("\n📄 GERENCIAR DOCUMENTOS:")
    print("   add <caminho_pdf>      Adicionar novo PDF ao banco de dados (atalho: 'a')")
    print("   ingest <caminho_pdf>   (Mesmo que 'add')")
    print("   remove <nome_arquivo>  Remove um arquivo específico da base (atalho: 'r')")
    print("   Exemplo: remove document.pdf")
    
    print("\n❓ AJUDA:")
    print("   help                   Mostrar esta mensagem de ajuda (atalho: 'h')")
    print("   ajuda                  (Mesmo que 'help')")
    print("   ?                      (Mesmo que 'help')")
    
    print("\n🚪 SAIR:")
    print("   sair                   Encerrar o chat (atalho: 'q')")
    print("   exit                   (Mesmo que 'sair')")
    print("   quit                   (Mesmo que 'sair')")
    print("   q                      (Mesmo que 'sair')")
    
    print("\n🧹 LIMPAR BASE (ADMIN):")
    print("   clear                  Remove todos os documentos do banco (atalho: 'c')")
    
    print("\n📊 ESTATÍSTICAS:")
    print("   stats                  Mostra estatísticas detalhadas do banco (atalho: 's')")
    
    print("="*70 + "\n")


def handle_add_command(user_input, quiet=False, chunk_size=None, chunk_overlap=None):
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
        print("-" * 70)
    
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
                print("-" * 70)
                print("✅ PDF adicionado com sucesso ao banco de dados!\n")
            return True
        else:
            if not quiet:
                print("-" * 70)
                print("❌ Falha ao adicionar PDF ao banco de dados.\n")
            return False
            
    except (IOError, OSError) as e:
        if not quiet:
            print("-" * 70)
            print(f"❌ Erro de sistema/arquivo ao processar PDF: {e}\n")
        return False
    except sa.exc.SQLAlchemyError as e:
        if not quiet:
            print("-" * 70)
            print(f"❌ Erro de banco de dados ao salvar PDF: {e}\n")
        return False
    except Exception as e:
        if not quiet:
            print("-" * 70)
            print(f"❌ Erro inesperado ao processar PDF: {e}\n")
        logger.error(f"Erro inesperado na ingestão: {e}", exc_info=True)
        return False


def is_exit_command(text):
    """
    Verifica se o comando é de saída.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de saída
    """
    return text.lower().strip() in ['sair', 'exit', 'quit', 'q']


def is_help_command(text):
    """
    Verifica se o comando é de ajuda.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de ajuda
    """
    return text.lower().strip() in ['help', 'ajuda', '?', 'h']


def is_add_command(text):
    """
    Verifica se o comando é de adicionar PDF.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de adição
    """
    cleaned = text.lower().strip()
    return cleaned == 'add' or cleaned == 'ingest' or cleaned == 'a' or cleaned.startswith(('add ', 'ingest ', 'a '))


def is_clear_command(text):
    """
    Verifica se o comando é de limpar a base.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de limpeza
    """
    return text.lower().strip() in ['clear', 'c']


def is_stats_command(text):
    """
    Verifica se o comando é de estatísticas.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de estatísticas
    """
    return text.lower().strip() in ['stats', 's']


def is_remove_command(text):
    """
    Verifica se o comando é de remover um arquivo.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de remoção
    """
    cleaned = text.lower().strip()
    return cleaned == 'remove' or cleaned == 'delete' or cleaned == 'r' or cleaned.startswith(('remove ', 'delete ', 'r '))


def handle_remove_command(user_input):
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


def handle_stats_command():
    """
    Exibe estatísticas detalhadas do banco de dados.
    """
    from database import VectorStoreRepository
    repo = VectorStoreRepository()
    
    num_chunks = repo.count()
    sources = repo.list_sources()
    num_sources = len(sources)
    
    print("\n" + "="*70)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("="*70)
    
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
    
    print("="*70 + "\n")


def handle_clear_command():
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


def process_question(chain, question, quiet=False, verbose=False, top_k=None, temperature=None):
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
            kwargs = {}
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
            print("-" * 70)
            print(f"PERGUNTA: {question}")
            print("-" * 70)
            print(f"RESPOSTA: {response}")
            
            if verbose:
                print("-" * 70)
                print(f"📊 ESTATÍSTICAS DA RESPOSTA:")
                print(f"⏱️  Tempo de execução: {elapsed_time:.2f}s")
                if sources:
                    print(f"📚 Fontes utilizadas ({len(sources)}):")
                    for spec in sources:
                        page_info = f", pág. {spec['page']}" if spec['page'] is not None else ""
                        print(f"   • {spec['filename']}{page_info}")
            
            print("-" * 70 + "\n")
        else:
            # Em modo quieto, mostra apenas a resposta pura para facilitar automação
            print(response)
            if verbose:
                # Se for verbose E quiet, mostra estatísticas mínimas
                print(f"--- Stats: {elapsed_time:.2f}s | {len(sources)} sources ---")
        
    except (KeyboardInterrupt, EOFError):
        # Captura interrupção voluntária (Ctrl+C ou Ctrl+D) sem explodir o log
        raise
    except sa.exc.SQLAlchemyError as e:
        print(f"❌ Erro crítico de banco de dados: {e}\n")
        logger.error(f"Erro de banco no processamento: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao processar pergunta: {e}\n")
        logger.error(f"Erro detalhado ao processar pergunta: {e}", exc_info=True)


def chat_loop(chain, quiet=False, verbose=False, top_k=None, temperature=None, chunk_size=None, chunk_overlap=None):
    """
    Loop principal do chat interativo.
    
    Args:
        chain: Chain do LangChain configurada
        quiet: Se True, opera em modo silencioso
        verbose: Se True, mostra estatísticas detalhadas
        top_k: Número de documentos a recuperar (opcional)
        temperature: Temperatura para geração (opcional)
        chunk_size: Tamanho do chunk para novas ingestões (opcional)
        chunk_overlap: Sobreposição do chunk para novas ingestões (opcional)
    """
    try:
        first_prompt = True
        while True:
            # Solicitar entrada do usuário
            if quiet:
                prompt_text = "> "
            else:
                prompt_text = "Faça sua pergunta (ou 'help' para ajuda)\n> " if first_prompt else "> "
            
            user_input = input(prompt_text).strip()
            
            # Ignorar entradas vazias
            if not user_input:
                continue
            
            first_prompt = False
            
            # Verificar comandos especiais
            if is_exit_command(user_input):
                if not quiet:
                    print("\n👋 Até logo! Chat encerrado.\n")
                break
            
            elif is_help_command(user_input):
                display_help()
            
            elif is_add_command(user_input):
                handle_add_command(user_input, quiet=quiet, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            elif is_clear_command(user_input):
                handle_clear_command()
            
            elif is_stats_command(user_input):
                handle_stats_command()
            
            elif is_remove_command(user_input):
                handle_remove_command(user_input)
            
            else:
                # Verificar se há documentos antes de perguntar
                num_chunks, _ = check_database_status()
                if num_chunks == 0:
                    if not quiet:
                        print("⚠️  O banco de dados está vazio!")
                        print("💡 Adicione um PDF primeiro usando 'add <caminho_pdf>'.\n")
                    continue
                
                # Processar como pergunta normal
                process_question(chain, user_input, quiet=quiet, verbose=verbose, top_k=top_k, temperature=temperature)
    
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrompido pelo usuário. Até logo!\n")
    except Exception as e:
        print(f"\n❌ Erro inesperado no chat: {e}\n")
        logger.error(f"Erro fatal no loop: {e}", exc_info=True)


def main():
    """
    Função principal do CLI.
    """
    # Validar configuração
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {e}\n")
        sys.exit(1)
    
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='Chat RAG - Sistema de busca semântica em PDFs',
        epilog='Exemplo: python src/chat.py'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Caminho do PDF para usar como referência (opcional)',
        metavar='PDF_PATH'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Modo silencioso: oculta logs de inicialização e estatísticas iniciais'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo detalhado: mostra tempo de resposta e fontes utilizadas'
    )
    parser.add_argument('--top-k', type=int, help=f'Número de documentos a recuperar (default: {Config.TOP_K})')
    parser.add_argument('--temperature', type=float, help='Temperatura para geração (default: conforme Config)')
    parser.add_argument('--chunk-size', type=int, help=f'Tamanho do chunk para novas ingestões (default: {Config.CHUNK_SIZE})')
    parser.add_argument('--chunk-overlap', type=int, help=f'Sobreposição do chunk para novas ingestões (default: {Config.CHUNK_OVERLAP})')
    
    args = parser.parse_args()
    
    # Se modo silencioso, ajustar nível de log globalmente
    if args.quiet:
        from logger import set_global_log_level
        set_global_log_level(logging.WARNING)
    
    # Se foi especificado um arquivo, processar ingestão primeiro
    if args.file:
        if not args.quiet:
            print(f"\n📄 Arquivo especificado via argumento: {args.file}")
        if not handle_add_command(f"add {args.file}", quiet=args.quiet, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap):
            if not args.quiet:
                print("⚠️  Continuando mesmo com falha na ingestão...\n")
    
    # Verificar status do banco
    counts = check_database_status()
    
    # Exibir boas-vindas (apenas se não estiver em modo silencioso)
    if not args.quiet:
        display_welcome(counts)
    
    # Inicializar chain de busca
    if not args.quiet:
        print("🔧 Inicializando sistema de busca...\n")
    
    # Criar kwargs para search_prompt
    search_kwargs = {}
    if args.top_k is not None: search_kwargs['top_k'] = args.top_k
    if args.temperature is not None: search_kwargs['temperature'] = args.temperature
    
    chain = search_prompt(**search_kwargs)
    
    if not chain:
        print("❌ Não foi possível iniciar o chat. Verifique as configurações no .env\n")
        sys.exit(1)
    
    if not args.quiet:
        print("✅ Sistema pronto!\n")
    
    # Iniciar loop de chat
    chat_loop(
        chain, 
        quiet=args.quiet, 
        verbose=args.verbose, 
        top_k=args.top_k, 
        temperature=args.temperature,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )


if __name__ == "__main__":
    try:
        main()
        os._exit(0)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
