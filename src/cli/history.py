from __future__ import annotations
from typing import List, Optional

from cli.ui import HEADER_LINE, SECTION_LINE

class ChatHistory:
    """
    Gerencia o histórico de comandos e interações do chat.
    """
    def __init__(self):
        self._history: List[str] = []

    def add(self, command: str) -> None:
        """
        Adiciona um comando ao histórico.
        Ignora comandos vazios ou duplicatas consecutivas.
        """
        cleaned = command.strip()
        if not cleaned:
            return
            
        # Evitar duplicatas consecutivas
        if self._history and self._history[-1] == cleaned:
            return
            
        self._history.append(cleaned)

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
        
        # Mostrar os últimos N comandos (ex: 20) ou todos? Todos por enquanto.
        for i, cmd in enumerate(self._history, 1):
            print(f" {i:3}. {cmd}")
            
        print(HEADER_LINE)
        print("💡 Dica: Use '!N' para repetir um comando (ex: !3)")
        print(HEADER_LINE + "\n")

    def __len__(self) -> int:
        return len(self._history)
