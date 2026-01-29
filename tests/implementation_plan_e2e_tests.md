# Plano de Implementação: Suite de Testes E2E Completa

## Objetivo

Criar uma suite de testes End-to-End (E2E) abrangente que simule testes unitários para o sistema RAG, cobrindo todas as combinações possíveis de parâmetros CLI e comandos internos dos programas `ingest.py` e `chat.py`.

## Contexto

O sistema não possui testes unitários formais. Precisamos criar testes E2E que:
- Testem todas as opções de linha de comando (`--COMANDO`)
- Testem todas as combinações válidas de múltiplos parâmetros
- Testem todos os comandos internos do chat (add, remove, clear, stats, help, history, etc.)
- Testem variações de entrada com provedor Google Gemini
- Validem tratamento de erros e casos extremos

## Análise de Parâmetros CLI

### `ingest.py`
**Parâmetros:**
- `pdf_path` (posicional, opcional)
- `-q, --quiet` (flag)
- `--chunk-size INT`
- `--chunk-overlap INT`

**Combinações a testar:** 20+ cenários

### `chat.py`
**Parâmetros:**
- `-f, --file PDF_PATH`
- `--provider google`
- `-q, --quiet` (flag)
- `-v, --verbose` (flag)
- `--top-k INT`
- `--temperature FLOAT`
- `--chunk-size INT`
- `--chunk-overlap INT`
- `--search-timeout INT`
- `--prompt-template PATH`

**Comandos internos:**
- `help`, `h`, `ajuda`, `?`
- `add <caminho>`, `a <caminho>`, `ingest <caminho>`
- `remove <arquivo>`, `r <arquivo>`, `delete <arquivo>`
- `clear`, `c`
- `stats`, `s`
- `history`
- `!N` (repetir comando)
- `sair`, `exit`, `quit`, `q`
- Perguntas normais

**Combinações a testar:** 150+ cenários

## Estrutura de Diretórios

```
tests/
├── implementation_plan_e2e_tests.md  # Este arquivo
├── test_e2e_complete.sh              # Script principal de testes
├── test_helpers.sh                   # Funções auxiliares
├── test_data/                        # PDFs e arquivos de teste
│   ├── small.pdf
│   ├── medium.pdf
│   └── large.pdf
├── test_results/                     # Resultados dos testes
│   ├── test_e2e_results.md
│   └── logs/
└── temp/                             # Arquivos temporários (gitignored)
```

## Proposta de Mudanças

### Fase 1: Testes de Ingestão Básica (`ingest.py`)

**1.1 Ingestão com Parâmetros Padrão**
- [ ] Ingestão sem argumentos (usa PDF_PATH do .env)
- [ ] Ingestão com caminho explícito
- [ ] Ingestão de PDF pequeno (1 página)
- [ ] Ingestão de PDF médio (5 páginas)
- [ ] Ingestão de PDF grande (20 páginas)

**1.2 Ingestão com Modo Quiet**
- [ ] Ingestão quiet sem barra de progresso
- [ ] Ingestão quiet sem estatísticas finais
- [ ] Ingestão quiet com confirmação automática de sobrescrita

**1.3 Ingestão com Chunk Size Customizado**
- [ ] chunk-size=500 (menor que padrão)
- [ ] chunk-size=2000 (maior que padrão)
- [ ] chunk-size=100 (muito pequeno)
- [ ] chunk-size=5000 (muito grande)

**1.4 Ingestão com Chunk Overlap Customizado**
- [ ] chunk-overlap=0 (sem overlap)
- [ ] chunk-overlap=50 (pequeno overlap)
- [ ] chunk-overlap=300 (grande overlap)
- [ ] chunk-overlap=500 (overlap maior que chunk size - deve funcionar mas gerar chunks redundantes)

**1.5 Ingestão com Combinações de Parâmetros**
- [ ] chunk-size=1500 + chunk-overlap=200
- [ ] chunk-size=800 + chunk-overlap=100 + quiet
- [ ] Todos os parâmetros customizados juntos

**1.6 Ingestão com Sobrescrita**
- [ ] Ingerir PDF, depois ingerir novamente (confirmar sobrescrita)
- [ ] Ingerir PDF, depois ingerir novamente em modo quiet (auto-sobrescrita)
- [ ] Ingerir PDF, depois ingerir novamente e cancelar

### Fase 2: Testes de Ingestão - Casos de Erro

**2.1 Erros de Arquivo**
- [ ] Arquivo não encontrado
- [ ] Caminho vazio
- [ ] Arquivo sem extensão .pdf
- [ ] Arquivo .txt (formato não suportado)
- [ ] Arquivo .docx (formato não suportado)
- [ ] PDF corrompido (se possível criar)
- [ ] PDF vazio (0 páginas)

**2.2 Erros de Parâmetros**
- [ ] chunk-size negativo
- [ ] chunk-overlap negativo
- [ ] chunk-size=0
- [ ] chunk-size não numérico

**2.3 Erros de Configuração**
- [ ] DATABASE_URL inválido (temporariamente)
- [ ] API key ausente (temporariamente)

### Fase 3: Testes de Chat - Parâmetros CLI Básicos

**3.1 Inicialização Básica**
- [ ] Chat sem argumentos
- [ ] Chat com banco vazio (deve mostrar aviso)
- [ ] Chat com banco populado (deve mostrar contagem)

**3.2 Ingestão Inicial via -f**
- [ ] Chat com -f small.pdf
- [ ] Chat com -f medium.pdf
- [ ] Chat com -f arquivo_inexistente.pdf (deve continuar mesmo com erro)

**3.3 Modo Quiet**
- [ ] Chat --quiet (sem logs de inicialização)
- [ ] Chat --quiet (prompt simplificado)
- [ ] Chat --quiet com pergunta (apenas resposta)

**3.4 Modo Verbose**
- [ ] Chat --verbose (mostra fontes)
- [ ] Chat --verbose (mostra tempo de resposta)
- [ ] Chat --verbose (mostra estatísticas)

**3.5 Combinação Quiet + Verbose**
- [ ] Chat -q -v (quiet suprime logs, verbose mostra stats mínimas)
- [ ] Validar que stats aparecem em formato compacto

### Fase 4: Testes de Chat - Parâmetros Avançados

**4.1 Top-K Customizado**
- [ ] --top-k 5 (menos documentos)
- [ ] --top-k 20 (mais documentos)
- [ ] --top-k 1 (mínimo)
- [ ] --top-k 50 (muito alto)

**4.2 Temperature Customizada**
- [ ] --temperature 0.0 (determinístico)
- [ ] --temperature 0.5 (balanceado)
- [ ] --temperature 1.0 (criativo)
- [ ] --temperature 2.0 (muito criativo)

**4.3 Search Timeout**
- [ ] --search-timeout 5 (curto)
- [ ] --search-timeout 30 (médio)
- [ ] --search-timeout 60 (longo)
- [ ] --search-timeout 1 (muito curto - pode causar timeout)

**4.4 Chunk Parameters para Add**
- [ ] --chunk-size 1500 (afeta comandos add durante chat)
- [ ] --chunk-overlap 200 (afeta comandos add durante chat)
- [ ] Combinação de chunk parameters

**4.5 Prompt Template Customizado**
- [ ] --prompt-template com arquivo válido
- [ ] --prompt-template com arquivo inexistente
- [ ] --prompt-template com template inválido

**4.6 Provedor**
- [ ] --provider google (explícito)
- [ ] Sem --provider (usa detecção automática)

### Fase 5: Testes de Comandos Internos - Help e Info

**5.1 Comando Help**
- [ ] `help` (comando completo)
- [ ] `h` (atalho)
- [ ] `ajuda` (alias)
- [ ] `?` (alias)
- [ ] Validar que todos mostram mesma saída

**5.2 Comando Stats**
- [ ] `stats` com banco vazio
- [ ] `stats` com 1 documento
- [ ] `stats` com múltiplos documentos
- [ ] `s` (atalho)
- [ ] Validar contagem de chunks e fontes

**5.3 Comando History**
- [ ] `history` com histórico vazio
- [ ] `history` após 1 comando
- [ ] `history` após 5 comandos
- [ ] `history` após 20 comandos (validar limite)

### Fase 6: Testes de Comandos Internos - Gerenciamento de Documentos

**6.1 Comando Add**
- [ ] `add small.pdf`
- [ ] `a small.pdf` (atalho)
- [ ] `ingest small.pdf` (alias)
- [ ] `add` sem argumento (deve mostrar erro)
- [ ] `add arquivo_inexistente.pdf` (deve mostrar erro)
- [ ] `add arquivo.txt` (formato não suportado)
- [ ] `add` com arquivo já existente (confirmar sobrescrita)
- [ ] `add` com arquivo já existente + cancelar

**6.2 Comando Remove**
- [ ] `remove small.pdf` (arquivo existente)
- [ ] `r small.pdf` (atalho)
- [ ] `delete small.pdf` (alias)
- [ ] `remove` sem argumento (deve mostrar erro)
- [ ] `remove arquivo_inexistente.pdf` (deve mostrar erro)
- [ ] `remove` + confirmar
- [ ] `remove` + cancelar

**6.3 Comando Clear**
- [ ] `clear` com banco populado + confirmar
- [ ] `c` (atalho)
- [ ] `clear` com banco populado + cancelar
- [ ] `clear` com banco vazio (deve informar que já está vazio)

### Fase 7: Testes de Comandos Internos - Repetição e Histórico

**7.1 Repetição de Comandos**
- [ ] `!1` (repetir primeiro comando)
- [ ] `!2` (repetir segundo comando)
- [ ] `!5` (repetir quinto comando)
- [ ] `!99` (índice inexistente - deve mostrar erro)
- [ ] `!0` (índice inválido)
- [ ] `!-1` (índice negativo)

**7.2 Navegação com Setas** (teste manual)
- [ ] Seta ↑ (comando anterior)
- [ ] Seta ↓ (comando seguinte)
- [ ] Múltiplas navegações ↑↑↑
- [ ] Navegação ↑↓↑

### Fase 8: Testes de Comandos Internos - Saída

**8.1 Comandos de Saída**
- [ ] `sair`
- [ ] `exit`
- [ ] `quit`
- [ ] `q` (atalho)
- [ ] Ctrl+C (interrupção)
- [ ] Ctrl+D (EOF)
- [ ] Validar mensagem de despedida (exceto em quiet)

### Fase 9: Testes de Perguntas

**9.1 Perguntas Básicas**
- [ ] Pergunta simples sobre conteúdo do PDF
- [ ] Pergunta complexa
- [ ] Pergunta curta (1 palavra)
- [ ] Pergunta longa (100+ palavras)

**9.2 Perguntas com Banco Vazio**
- [ ] Pergunta com banco vazio (deve alertar)
- [ ] Validar que não processa a pergunta

**9.3 Perguntas em Diferentes Modos**
- [ ] Pergunta em modo normal (com indicadores de progresso)
- [ ] Pergunta em modo quiet (apenas resposta)
- [ ] Pergunta em modo verbose (com fontes e tempo)
- [ ] Pergunta em modo quiet+verbose (resposta + stats compactas)

**9.4 Múltiplas Perguntas Sequenciais**
- [ ] 3 perguntas seguidas
- [ ] 10 perguntas seguidas
- [ ] Validar que histórico é mantido

**9.5 Perguntas Fora do Contexto**
- [ ] Pergunta sobre assunto não presente no PDF
- [ ] Validar resposta: "Não tenho informações necessárias..."

### Fase 10: Testes de Combinações Complexas

**10.1 Fluxo Completo de Uso**
- [ ] Iniciar chat → add PDF → stats → pergunta → sair
- [ ] Iniciar chat com -f → pergunta → add outro PDF → pergunta → stats → sair
- [ ] Iniciar chat → add PDF1 → add PDF2 → stats → remove PDF1 → stats → sair

**10.2 Uso de Histórico**
- [ ] add → stats → !1 (repetir add) → !2 (repetir stats)
- [ ] Múltiplos comandos + repetições intercaladas

**10.3 Combinações de Parâmetros**
- [ ] -f small.pdf --quiet --verbose --top-k 5
- [ ] -f medium.pdf --temperature 0.5 --search-timeout 10
- [ ] --chunk-size 1500 --chunk-overlap 200 --quiet

**10.4 Gerenciamento de Múltiplos Documentos**
- [ ] Add 3 PDFs diferentes
- [ ] Stats (validar 3 fontes)
- [ ] Remove 1 PDF
- [ ] Stats (validar 2 fontes)
- [ ] Clear
- [ ] Stats (validar 0 documentos)

### Fase 11: Testes de Robustez e Casos Extremos

**11.1 Entradas Inválidas**
- [ ] Comando inexistente
- [ ] Comando com sintaxe errada
- [ ] Entrada vazia (múltiplas vezes)
- [ ] Caracteres especiais no comando

**11.2 Confirmações**
- [ ] Confirmação com "sim"
- [ ] Confirmação com "SIM"
- [ ] Confirmação com "s"
- [ ] Confirmação com "n"
- [ ] Confirmação com "não"
- [ ] Confirmação com entrada vazia
- [ ] Confirmação com texto aleatório

**11.3 Timeout**
- [ ] Pergunta com timeout muito curto (--search-timeout 1)
- [ ] Validar que timeout é respeitado
- [ ] Validar mensagem de erro apropriada

**11.4 Interrupções**
- [ ] Ctrl+C durante ingestão
- [ ] Ctrl+C durante pergunta
- [ ] Ctrl+C no prompt
- [ ] Validar encerramento gracioso

**11.5 Banco de Dados**
- [ ] Banco vazio + comando stats
- [ ] Banco vazio + comando clear
- [ ] Banco vazio + comando remove
- [ ] Banco vazio + pergunta

### Fase 12: Testes de Integração com Provedor

**12.1 Google Gemini**
- [ ] Ingestão com Google (gera embeddings)
- [ ] Pergunta com Google (usa LLM)
- [ ] Validar que embeddings são gerados corretamente
- [ ] Validar que respostas são coerentes

**12.2 Troca de Provedor** (não aplicável - apenas Google disponível)

**12.3 Erros de API**
- [ ] API key inválida (temporariamente)
- [ ] Validar mensagem de erro apropriada

### Fase 13: Testes de Validação de Saída

**13.1 Formatação de Saída Normal**
- [ ] Validar separadores (===, ---)
- [ ] Validar emojis (🔍, 🧠, ✅, etc.)
- [ ] Validar estrutura de mensagens

**13.2 Formatação de Saída Quiet**
- [ ] Validar ausência de logs
- [ ] Validar ausência de emojis
- [ ] Validar apenas resposta pura

**13.3 Formatação de Saída Verbose**
- [ ] Validar presença de tempo de resposta
- [ ] Validar presença de fontes
- [ ] Validar formato de estatísticas

**13.4 Estatísticas de Ingestão**
- [ ] Validar contagem de páginas
- [ ] Validar contagem de chunks
- [ ] Validar tamanho médio
- [ ] Validar IDs dos chunks

### Fase 14: Testes de Persistência e Estado

**14.1 Persistência entre Comandos**
- [ ] Add PDF → sair → iniciar novamente → stats (deve mostrar PDF)
- [ ] Add PDF → clear → sair → iniciar novamente → stats (deve estar vazio)

**14.2 Estado do Histórico**
- [ ] Histórico não persiste entre sessões
- [ ] Histórico é mantido durante sessão
- [ ] Histórico é limpo ao sair

**14.3 Múltiplas Sessões**
- [ ] Sessão 1: add PDF
- [ ] Sessão 2: stats (deve ver PDF da sessão 1)
- [ ] Sessão 2: add outro PDF
- [ ] Sessão 3: stats (deve ver ambos PDFs)

## Estrutura do Script de Teste

```bash
#!/bin/bash

# Configuração
TEST_DIR="./tests"
TEST_DATA_DIR="$TEST_DIR/test_data"
TEST_RESULTS_DIR="$TEST_DIR/test_results"
TEST_TEMP_DIR="$TEST_DIR/temp"

# Contadores
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções auxiliares (em test_helpers.sh)
source "$TEST_DIR/test_helpers.sh"

# Fases de teste
test_phase_1_ingest_basic() { ... }
test_phase_2_ingest_errors() { ... }
test_phase_3_chat_cli_basic() { ... }
test_phase_4_chat_cli_advanced() { ... }
test_phase_5_commands_help() { ... }
test_phase_6_commands_docs() { ... }
test_phase_7_commands_history() { ... }
test_phase_8_commands_exit() { ... }
test_phase_9_questions() { ... }
test_phase_10_complex_scenarios() { ... }
test_phase_11_robustness() { ... }
test_phase_12_provider() { ... }
test_phase_13_output_validation() { ... }
test_phase_14_persistence() { ... }

# Execução
main() {
    setup_test_environment
    run_all_phases
    generate_report
    cleanup
}

main "$@"
```

## Verificação

### Testes Automatizados

**Executar:**
```bash
cd tests
chmod +x test_e2e_complete.sh
./test_e2e_complete.sh
```

**Relatório:** `tests/test_results/test_e2e_results.md`

### Testes Manuais

1. Navegação de histórico com setas ↑↓
2. Interrupção com Ctrl+C em diferentes momentos
3. Validação visual de formatação

## Próximos Passos

1. ✅ Criar estrutura de diretórios `tests/`
2. ✅ Salvar plano como `implementation_plan_e2e_tests.md`
3. ⏳ Aguardar aprovação do usuário
4. ⏳ Implementar `test_e2e_complete.sh`
5. ⏳ Implementar `test_helpers.sh`
6. ⏳ Criar PDFs de teste em `test_data/`
7. ⏳ Executar suite de testes
8. ⏳ Gerar relatório de resultados
9. ⏳ Marcar tarefa 1.5.1 como concluída
