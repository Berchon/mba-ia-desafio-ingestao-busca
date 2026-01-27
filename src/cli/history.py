from __future__ import annotations
import os
from typing import List, Optional
try:
    import readline
except ImportError:
    readline = None

from cli.ui import HEADER_LINE, SECTION_LINE

class ChatHistory:
    """
    Gerencia o histórico de comandos e interações do chat.
    Suporta navegação com setas (via readline) e persistência em arquivo.
    """
    def __init__(self, history_file: str = ".chat_history"):
        self._history: List[str] = []
        self._history_file = os.path.abspath(history_file)
        self._setup_readline()
        
    def _setup_readline(self) -> None:
        """
        Configura o readline para suporte a navegação com setas e persistência.
        """
        if not readline:
            return

        # Tentar carregar histórico existente
        if os.path.exists(self._history_file):
            try:
                readline.read_history_file(self._history_file)
            except IOError:
                pass
                
        # Configurar salvamento automático ao sair (opcional, mas manual é mais seguro para controlar o que salva)
        import atexit
        atexit.register(self.save_history)

    def save_history(self) -> None:
        """Salva o histórico atual no arquivo."""
        if not readline:
            return
        try:
            readline.write_history_file(self._history_file)
        except IOError:
            pass

    def add(self, command: str) -> None:
        """
        Adiciona um comando ao histórico interno e do readline.
        Ignora comandos vazios ou duplicatas consecutivas.
        """
        cleaned = command.strip()
        if not cleaned:
            return
            
        # Evitar duplicatas consecutivas no histórico interno
        if self._history and self._history[-1] == cleaned:
            return
            
        self._history.append(cleaned)
        
        # O readline gerenciado pelo input() geralmente adiciona automaticamente,
        # mas adicionar explicitamente garante sincronia se usarmos configurações customizadas.
        # Porém, input() com readline já adiciona ao buffer. Se adicionarmos aqui, pode duplicar.
        # Vamos confiar no input() para o buffer de setas, e usar esta lista apenas para o comando 'history'.
        # Para persistência, o readline precisa saber.
        # Se o usuario digita, o readline pega. Se usamos add() via código, precisamos inserir?
        # Não, add() é chamado APÓS o input. Então o readline já tem.

    def get_by_index(self, index: int) -> Optional[str]:
        """
        Recupera um comando pelo índice (1-based).
        
        Args:
            index: Índice do comando (começando em 1)
            
        Returns:
            O comando correspondente ou None se inválido.
        """
        # Ajustar para 0-based
        idx_zero = index - 1
        
        if 0 <= idx_zero < len(self._history):
            return self._history[idx_zero]
        return None

    def display(self) -> None:
        """
        Exibe o histórico de comandos formatado.
        """
        if not self._history:
            print("\n📜 Histórico vazio.\n")
            return

        print("\n" + HEADER_LINE)
        print("📜 HISTÓRICO DE COMANDOS")
        print(HEADER_LINE)
        
        for i, cmd in enumerate(self._history, 1):
            print(f" {i:3}. {cmd}")
            
        print(HEADER_LINE)
        print("💡 Dica: Use '!N' para repetir um comando (ex: !3)")
        print("💡 Dica: Use as setas ↑ / ↓ para navegar nos comandos anteriores")
        print(HEADER_LINE + "\n")

    def __len__(self) -> int:
        return len(self._history)
