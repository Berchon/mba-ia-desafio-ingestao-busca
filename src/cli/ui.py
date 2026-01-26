from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

DISPLAY_WIDTH = 70
HEADER_LINE = "=" * DISPLAY_WIDTH
SECTION_LINE = "-" * DISPLAY_WIDTH

def display_welcome(counts: tuple[int, int]) -> None:
    """
    Exibe mensagem de boas-vindas com status do banco.
    
    Args:
        counts: Tupla (num_chunks, num_sources)
    """
    num_chunks, num_sources = counts
    print("\n" + HEADER_LINE)
    print("🤖 CHAT RAG - Sistema de Busca Semântica com LangChain")
    print(HEADER_LINE)
    
    if num_chunks > 0:
        plural_files = "arquivos" if num_sources > 1 else "arquivo"
        print(f"✅ Status: Banco conectado com {num_chunks} trechos de {num_sources} {plural_files}")
    else:
        print("⚠️  Status: Banco de dados vazio")
        print("💡 Dica: Use o comando 'add <caminho_pdf>' para adicionar documentos")
    
    print("\nDigite 'help' para ver os comandos disponíveis.")
    print(HEADER_LINE + "\n")


def display_help() -> None:
    """
    Exibe a lista de comandos disponíveis.
    """
    print("\n" + HEADER_LINE)
    print("📚 COMANDOS DISPONÍVEIS")
    print(HEADER_LINE)
    print("\n🔍 FAZER PERGUNTAS:")
    print("   Digite sua pergunta diretamente (ex: 'Qual o faturamento da Empresa SuperTechIABrazil?')")
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

    print("\n📜 HISTÓRICO:")
    print("   history                Mostra últimos comandos (atalho: 'hist')")
    print("   !N                     Repete o comando número N (ex: !3)")
    
    print(HEADER_LINE + "\n")
