import sys
import argparse
import logging
from search import search_prompt
from database import get_vector_store
from ingest import ingest_pdf
from config import Config
from embeddings_manager import get_embeddings

# Configuração de Logs
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_database_status():
    """
    Verifica quantos documentos existem no banco de dados vetorial.
    
    Returns:
        int: Número de documentos no banco (0 se vazio ou erro)
    """
    try:
        embeddings = get_embeddings()
        vector_store = get_vector_store(embeddings)
        
        # Tenta buscar 1 documento para verificar se há dados
        # (não há método direto .count() no PGVector)
        test_results = vector_store.similarity_search("test", k=1)
        
        if test_results:
            logger.info(f"Banco contém documentos")
            return len(test_results)  # Retorna pelo menos 1
        return 0
    except Exception as e:
        logger.warning(f"Não foi possível verificar o status do banco: {e}")
        return 0


def display_welcome(doc_count):
    """
    Exibe mensagem de boas-vindas com status do banco.
    
    Args:
        doc_count: Número de documentos no banco
    """
    print("\n" + "="*70)
    print("🤖 CHAT RAG - Sistema de Busca Semântica com LangChain")
    print("="*70)
    
    if doc_count > 0:
        print("✅ Status: Banco de dados conectado com documentos disponíveis")
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
        # Reutilizar lógica do ingest.py
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
            
            else:
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
        '-file', '--file',
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
    doc_count = check_database_status()
    
    # Exibir boas-vindas
    display_welcome(doc_count)
    
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
    main()