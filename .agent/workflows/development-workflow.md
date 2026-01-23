---
description: Workflow de desenvolvimento do projeto RAG
---

# 🚀 Workflow de Desenvolvimento

- Escreva seu pensamento sempre em português do brasil

## 📋 Regras Fundamentais

### Git Workflow
- **1 Subtask = 1 Branch** separada (ex: A.1.1 → `feature/config-module`, A.1.2 → `feature/config-database`)
- **1 Subtask = 1 Commit** principal (podem haver commits de ajuste)
- **Commits**: Frase única, em inglês, conventional commits (feat:, fix:, refactor:, etc)
- **Exemplo**: `feat: add centralized config module`
- **Branch Naming**: Usar nomes descritivos baseados no que a subtask faz, não apenas o número

### Ciclo de Desenvolvimento

#### Para CADA Subtask (ex: A.1.1):
1. **Criar branch** específica (ex: `feature/config-module`)
2. Implementar a subtask
3. **DEVOLVER CONTROLE** ao usuário para testar
4. Usuário testa e valida
5. **PERGUNTAR**: "Posso fazer o commit e merge desta subtask?"
6. Se OK → Commit → Merge para main → Atualizar TODOs.md → Próxima subtask
7. Se NOK → Ajustar → Repetir ciclo

#### Para CADA Grupo de Subtasks (ex: A.1):
1. Concluir TODAS as subtasks do grupo (A.1.1, A.1.2, A.1.3, etc)
2. **DEVOLVER CONTROLE** ao usuário para teste completo do grupo
3. Usuário testa aplicação completa
4. Se OK → Próximo grupo
5. Se NOK → Ajustar subtask específica → Repetir ciclo

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