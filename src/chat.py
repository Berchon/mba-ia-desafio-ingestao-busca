"""
CLI de chat para o sistema RAG (Refatorado).
"""

from __future__ import annotations

import sys
import os
import argparse
import logging
from typing import Any, Optional

from config import Config
from search import search_prompt
from logger import get_logger, set_global_log_level

# Importação dos novos módulos CLI
from cli.ui import display_welcome, display_help, HEADER_LINE, SECTION_LINE
from cli.validators import (
    is_exit_command,
    is_help_command,
    is_add_command,
    is_clear_command,
    is_stats_command,
    is_remove_command
)
from cli.commands import (
    check_database_status,
    handle_add_command,
    handle_clear_command,
    handle_stats_command,
    handle_remove_command,
    process_question
)

logger = get_logger(__name__, level=logging.WARNING)


def chat_loop(
    chain: Any,
    quiet: bool = False,
    verbose: bool = False,
    top_k: Optional[int] = None,
    temperature: Optional[float] = None,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> None:
    """
    Loop principal do chat interativo.
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


def main() -> None:
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
    search_kwargs: dict[str, Any] = {}
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
