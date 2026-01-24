import sys
import os
import argparse
import logging
from search import search_prompt
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
    except Exception as e:
        logger.warning(f"Não foi possível verificar o status do banco: {e}")
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
    print("   add <caminho_pdf>      Adicionar novo PDF ao banco de dados")
    print("   ingest <caminho_pdf>   (Mesmo que 'add')")
    print("   Exemplo: add document.pdf")
    
    print("\n❓ AJUDA:")
    print("   help                   Mostrar esta mensagem de ajuda")
    print("   ajuda                  (Mesmo que 'help')")
    print("   ?                      (Mesmo que 'help')")
    
    print("\n🚪 SAIR:")
    print("   sair                   Encerrar o chat")
    print("   exit                   (Mesmo que 'sair')")
    print("   quit                   (Mesmo que 'sair')")
    print("   q                      (Mesmo que 'sair')")
    
    print("\n🧹 LIMPAR BASE (ADMIN):")
    print("   clear                  Remove todos os documentos do banco")
    
    print("\n📊 ESTATÍSTICAS:")
    print("   stats                  Mostra estatísticas detalhadas do banco")
    
    print("="*70 + "\n")


def handle_add_command(user_input):
    """
    Processa comando de adição de PDF ao banco.
    
    Args:
        user_input: Entrada completa do usuário (ex: "add document.pdf")
        
    Returns:
        bool: True se processado com sucesso, False caso contrário
    """
    parts = user_input.strip().split(maxsplit=1)
    
    if len(parts) < 2:
        print("❌ Erro: Você deve especificar o caminho do PDF.")
        print("   Uso: add <caminho_pdf>")
        print("   Exemplo: add document.pdf\n")
        return False
    
    pdf_path = parts[1].strip()
    
    # Validar se arquivo existe
    if not os.path.exists(pdf_path):
        print(f"❌ Erro: Arquivo não encontrado: {pdf_path}\n")
        return False
    
    # Validar extensão
    if not pdf_path.lower().endswith('.pdf'):
        print(f"❌ Erro: O arquivo deve ser um PDF (.pdf)\n")
        return False
    
    print(f"\n📄 Iniciando ingestão do PDF: {pdf_path}")
    print("-" * 70)
    
    try:
        # 1. Inicializar Repositório para verificar existência
        from database import VectorStoreRepository
        repo = VectorStoreRepository()
        
        # 2. Verificar se o arquivo já foi ingerido
        if repo.source_exists(pdf_path):
            print(f"⚠️  O arquivo '{pdf_path}' já existe na base de dados.")
            confirm = input("Deseja sobrescrever os dados existentes? (sim/n): ").strip().lower()
            if confirm != 'sim':
                print("Operação cancelada pelo usuário.\n")
                return False
            print("Limpando dados antigos e re-ingerindo...\n")

        # 3. Reutilizar lógica do ingest.py
        success = ingest_pdf(pdf_path)
        
        if success:
            print("-" * 70)
            print("✅ PDF adicionado com sucesso ao banco de dados!\n")
            return True
        else:
            print("-" * 70)
            print("❌ Falha ao adicionar PDF ao banco de dados.\n")
            return False
            
    except Exception as e:
        print("-" * 70)
        print(f"❌ Erro ao processar PDF: {e}\n")
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
    return text.lower().strip() in ['help', 'ajuda', '?']


def is_add_command(text):
    """
    Verifica se o comando é de adicionar PDF.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de adição
    """
    return text.lower().strip().startswith(('add ', 'ingest '))


def is_clear_command(text):
    """
    Verifica se o comando é de limpar a base.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de limpeza
    """
    return text.lower().strip() == 'clear'


def is_stats_command(text):
    """
    Verifica se o comando é de estatísticas.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de estatísticas
    """
    return text.lower().strip() == 'stats'


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


def process_question(chain, question):
    """
    Processa uma pergunta usando a chain do RAG.
    
    Args:
        chain: Chain do LangChain configurada
        question: Pergunta do usuário
    """
    try:
        print("🔍 Buscando resposta...\n")
        response = chain.invoke(question)
        
        print("-" * 70)
        print(f"PERGUNTA: {question}")
        print("-" * 70)
        print(f"RESPOSTA: {response}")
        print("-" * 70 + "\n")
        
    except Exception as e:
        print(f"❌ Erro ao processar pergunta: {e}\n")
        logger.error(f"Erro detalhado: {e}", exc_info=True)


def chat_loop(chain):
    """
    Loop principal do chat interativo.
    
    Args:
        chain: Chain do LangChain configurada
    """
    try:
        while True:
            # Solicitar entrada do usuário
            user_input = input("Faça sua pergunta (ou 'help' para ajuda): ").strip()
            
            # Ignorar entradas vazias
            if not user_input:
                continue
            
            # Verificar comandos especiais
            if is_exit_command(user_input):
                print("\n👋 Até logo! Chat encerrado.\n")
                break
            
            elif is_help_command(user_input):
                display_help()
            
            elif is_add_command(user_input):
                handle_add_command(user_input)
            
            elif is_clear_command(user_input):
                handle_clear_command()
            
            elif is_stats_command(user_input):
                handle_stats_command()
            
            else:
                # Verificar se há documentos antes de perguntar
                num_chunks, _ = check_database_status()
                if num_chunks == 0:
                    print("⚠️  O banco de dados está vazio!")
                    print("💡 Adicione um PDF primeiro usando 'add <caminho_pdf>'.\n")
                    continue
                
                # Processar como pergunta normal
                process_question(chain, user_input)
    
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
    
    args = parser.parse_args()
    
    # Se foi especificado um arquivo, processar ingestão primeiro
    if args.file:
        print(f"\n📄 Arquivo especificado via argumento: {args.file}")
        if not handle_add_command(f"add {args.file}"):
            print("⚠️  Continuando mesmo com falha na ingestão...\n")
    
    # Verificar status do banco
    counts = check_database_status()
    
    # Exibir boas-vindas
    display_welcome(counts)
    
    # Inicializar chain de busca
    print("🔧 Inicializando sistema de busca...\n")
    chain = search_prompt()
    
    if not chain:
        print("❌ Não foi possível iniciar o chat. Verifique as configurações no .env\n")
        sys.exit(1)
    
    print("✅ Sistema pronto!\n")
    
    # Iniciar loop de chat
    chat_loop(chain)


if __name__ == "__main__":
    try:
        main()
        os._exit(0)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
