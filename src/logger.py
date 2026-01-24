"""
Módulo de Logging Centralizado

Configura o sistema de logging de forma consistente para toda a aplicação.
"""

import logging
import sys


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configura e retorna um logger com formatação consistente.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo). Se None, retorna o root logger.
        level: Nível de logging (default: INFO)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicação de handlers se já configurado
    if logger.handlers:
        return logger
    
    # Configurar nível
    logger.setLevel(level)
    
    # Criar handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Criar formatador
    formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Adicionar formatador ao handler
    console_handler.setFormatter(formatter)
    
    # Adicionar handler ao logger
    logger.addHandler(console_handler)
    
    # Evitar propagação para o root logger (evita duplicação)
    logger.propagate = False
    
    return logger


def get_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Função de conveniência para obter um logger.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        level: Nível de logging (default: INFO)
        
    Returns:
        logging.Logger: Logger configurado
    """
    return setup_logger(name, level)


def set_global_log_level(level: int):
    """
    Define o nível de log para todos os loggers já criados e para o root logger.
    Útil para implementar o modo silencioso.
    
    Args:
        level: Nível de logging (ex: logging.WARNING)
    """
    # 1. Ajustar o root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    # 2. Ajustar todos os loggers criados via get_logger
    # O logger manager mantém um dicionário de todos os loggers
    for logger_name in logging.root.manager.loggerDict:
        # Pular entradas que não são loggers (Placeholders)
        if isinstance(logging.root.manager.loggerDict[logger_name], logging.Logger):
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)
