from __future__ import annotations

def is_exit_command(text: str) -> bool:
    """
    Verifica se o comando é de saída.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de saída
    """
    return text.lower().strip() in ['sair', 'exit', 'quit', 'q']


def is_help_command(text: str) -> bool:
    """
    Verifica se o comando é de ajuda.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de ajuda
    """
    return text.lower().strip() in ['help', 'ajuda', '?', 'h']


def is_add_command(text: str) -> bool:
    """
    Verifica se o comando é de adicionar PDF.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de adição
    """
    cleaned = text.lower().strip()
    return cleaned == 'add' or cleaned == 'ingest' or cleaned == 'a' or cleaned.startswith(('add ', 'ingest ', 'a '))


def is_clear_command(text: str) -> bool:
    """
    Verifica se o comando é de limpar a base.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de limpeza
    """
    return text.lower().strip() in ['clear', 'c']


def is_stats_command(text: str) -> bool:
    """
    Verifica se o comando é de estatísticas.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de estatísticas
    """
    return text.lower().strip() in ['stats', 's']


def is_remove_command(text: str) -> bool:
    """
    Verifica se o comando é de remover um arquivo.
    
    Args:
        text: Texto do usuário
        
    Returns:
        bool: True se for comando de remoção
    """
    cleaned = text.lower().strip()
    return cleaned == 'remove' or cleaned == 'delete' or cleaned == 'r' or cleaned.startswith(('remove ', 'delete ', 'r '))
