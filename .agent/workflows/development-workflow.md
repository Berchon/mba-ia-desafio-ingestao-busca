---
description: Workflow de desenvolvimento do projeto RAG
---

# 🚀 Workflow de Desenvolvimento

## 📋 Regras Fundamentais

### Git Workflow
- **1 Task = 1 Branch** separada (ex: `feature/config-centralized`)
- **1 Subtask = 1 Commit** (quando possível)
- **Commits**: Frase única, em inglês, conventional commits (feat:, fix:, refactor:, etc)
- **Exemplo**: `feat: add centralized config module`

### Ciclo de Desenvolvimento

#### Para CADA Subtask:
1. Implementar a subtask
2. **DEVOLVER CONTROLE** ao usuário para testar
3. Usuário testa e valida
4. **PERGUNTAR**: "Posso fazer o commit desta subtask?"
5. Se OK → Commit → Atualizar o TODOs.md → Próxima subtask
6. Se NOK → Ajustar → Repetir ciclo

#### Para CADA Task:
1. Concluir TODAS as subtasks
2. **DEVOLVER CONTROLE** ao usuário para teste completo
3. Usuário testa aplicação completa
4. **PERGUNTAR**: "Posso fazer o merge com a main?"
5. Se OK → Merge → Atualizar o TODOs.md → Próxima task
6. Se NOK → Ajustar → Repetir ciclo

#### Entre Tasks:
- **SEMPRE PERGUNTAR**: "O que deseja fazer agora?"
  - Continuar próxima task?
  - Ajustar task atual?
  - Pausar?

### Comunicação com Usuário
- **NUNCA** avançar sem autorização
- **SEMPRE** devolver controle antes de commits/merges
- **SEMPRE** perguntar antes de próxima ação
- **SEMPRE** permitir debate em cada etapa

### Testes
- Antes de commit: teste de subtask
- Antes de merge: teste completo da task
- Aplicação deve funcionar após cada commit

## 🎯 Aplicar Este Workflow

Este workflow deve ser seguido:
- ✅ Em TODA nova conversa
- ✅ Para TODA task deste projeto
- ✅ Para TODA implementação de melhoria
- ✅ Para TODA correção de bug

**CRITICAL**: Não pule etapas. Não automatize sem permissão. Sempre consulte o usuário.