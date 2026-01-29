#!/bin/bash

#
# Suite Completa de Testes E2E para Sistema RAG
# 
# Este script executa 150+ testes cobrindo todas as funcionalidades
# do sistema de ingestão e busca semântica.
#

# Não usar set -e para permitir que testes continuem mesmo se um falhar

# Carregar funções auxiliares
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/test_helpers.sh"

# ============================================================================
# FASE 1: TESTES DE INGESTÃO BÁSICA
# ============================================================================

test_phase_1_ingest_basic() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 1: Testes de Ingestão Básica"
    echo -e "==========================================${NC}\n"
    
    # 1.1 Ingestão com caminho explícito
    run_test \
        "Ingestão de PDF pequeno" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --quiet" \
        0 \
        ""
    
    # 1.2 Ingestão de PDF médio
    run_test \
        "Ingestão de PDF médio" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/medium.pdf --quiet" \
        0 \
        ""
    
    # 1.3 Ingestão de PDF grande
    run_test \
        "Ingestão de PDF grande" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/large.pdf --quiet" \
        0 \
        ""
    
    # 1.4 Ingestão com modo quiet (sem barra de progresso)
    run_test \
        "Ingestão em modo quiet" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --quiet" \
        0 \
        ""
    
    # 1.5 Ingestão com chunk-size customizado (menor)
    run_test \
        "Ingestão com chunk-size=500" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-size 500 --quiet" \
        0 \
        ""
    
    # 1.6 Ingestão com chunk-size customizado (maior)
    run_test \
        "Ingestão com chunk-size=2000" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-size 2000 --quiet" \
        0 \
        ""
    
    # 1.7 Ingestão com chunk-overlap customizado
    run_test \
        "Ingestão com chunk-overlap=0" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-overlap 0 --quiet" \
        0 \
        ""
    
    # 1.8 Ingestão com chunk-overlap customizado (grande)
    run_test \
        "Ingestão com chunk-overlap=300" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-overlap 300 --quiet" \
        0 \
        ""
    
    # 1.9 Ingestão com combinação de parâmetros
    run_test \
        "Ingestão com chunk-size=1500 + chunk-overlap=200" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-size 1500 --chunk-overlap 200 --quiet" \
        0 \
        ""
    
    # 1.10 Ingestão com todos os parâmetros
    run_test \
        "Ingestão com todos os parâmetros customizados" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-size 800 --chunk-overlap 100 --quiet" \
        0 \
        ""
}

# ============================================================================
# FASE 2: TESTES DE INGESTÃO - CASOS DE ERRO
# ============================================================================

test_phase_2_ingest_errors() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 2: Testes de Ingestão - Casos de Erro"
    echo -e "==========================================${NC}\n"
    
    # 2.1 Arquivo não encontrado
    run_test \
        "Erro: Arquivo não encontrado" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py arquivo_inexistente.pdf --quiet 2>&1" \
        2 \
        ""
    
    # 2.2 Arquivo sem extensão .pdf
    touch "$TEST_TEMP_DIR/arquivo_sem_extensao"
    run_test \
        "Erro: Arquivo sem extensão .pdf" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_TEMP_DIR/arquivo_sem_extensao --quiet 2>&1" \
        1 \
        ""
    
    # 2.3 Arquivo .txt (formato não suportado)
    echo "teste" > "$TEST_TEMP_DIR/arquivo.txt"
    run_test \
        "Erro: Formato não suportado (.txt)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_TEMP_DIR/arquivo.txt --quiet 2>&1" \
        1 \
        ""
    
    # 2.4 Chunk-size inválido (negativo)
    run_test \
        "Erro: chunk-size negativo" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-size -100 --quiet 2>&1" \
        2 \
        ""
    
    # 2.5 Chunk-overlap inválido (negativo)
    run_test \
        "Erro: chunk-overlap negativo" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --chunk-overlap -50 --quiet 2>&1" \
        2 \
        ""
}

# ============================================================================
# FASE 3: TESTES DE CHAT - PARÂMETROS CLI BÁSICOS
# ============================================================================

test_phase_3_chat_cli_basic() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 3: Testes de Chat - Parâmetros CLI Básicos"
    echo -e "==========================================${NC}\n"
    
    # Garantir que há documentos no banco
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    # 3.1 Chat com banco populado (stats)
    run_interactive_test \
        "Chat: stats com banco populado" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "chunks"
    
    # 3.2 Chat em modo quiet
    run_interactive_test \
        "Chat: modo quiet" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "sair" \
        0 \
        ""
    
    # 3.3 Chat com -f (ingestão inicial)
    run_interactive_test \
        "Chat: ingestão inicial com -f" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py -f $TEST_DATA_DIR/medium.pdf --quiet" \
        "sair" \
        0 \
        ""
    
    # 3.4 Chat com --provider google
    run_interactive_test \
        "Chat: provedor Google explícito" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --provider google --quiet" \
        "sair" \
        0 \
        ""
}

# ============================================================================
# FASE 4: TESTES DE CHAT - PARÂMETROS AVANÇADOS
# ============================================================================

test_phase_4_chat_cli_advanced() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 4: Testes de Chat - Parâmetros Avançados"
    echo -e "==========================================${NC}\n"
    
    # 4.1 Chat com --top-k customizado
    run_interactive_test \
        "Chat: --top-k 5" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --top-k 5 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.2 Chat com --top-k alto
    run_interactive_test \
        "Chat: --top-k 20" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --top-k 20 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.3 Chat com --temperature 0.0
    run_interactive_test \
        "Chat: --temperature 0.0 (determinístico)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --temperature 0.0 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.4 Chat com --temperature 0.5
    run_interactive_test \
        "Chat: --temperature 0.5" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --temperature 0.5 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.5 Chat com --temperature 1.0
    run_interactive_test \
        "Chat: --temperature 1.0 (criativo)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --temperature 1.0 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.6 Chat com --search-timeout curto
    run_interactive_test \
        "Chat: --search-timeout 5" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --search-timeout 5 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.7 Chat com --search-timeout longo
    run_interactive_test \
        "Chat: --search-timeout 60" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --search-timeout 60 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.8 Chat com --chunk-size para add
    run_interactive_test \
        "Chat: --chunk-size 1500" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --chunk-size 1500 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.9 Chat com --chunk-overlap para add
    run_interactive_test \
        "Chat: --chunk-overlap 200" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --chunk-overlap 200 --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.10 Chat com modo verbose
    run_interactive_test \
        "Chat: modo verbose" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --verbose --quiet" \
        "sair" \
        0 \
        ""
    
    # 4.11 Chat com quiet + verbose
    run_interactive_test \
        "Chat: quiet + verbose combinados" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet --verbose" \
        "sair" \
        0 \
        ""
    
    # 4.12 Chat com múltiplos parâmetros
    run_interactive_test \
        "Chat: múltiplos parâmetros combinados" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --top-k 10 --temperature 0.3 --quiet" \
        "sair" \
        0 \
        ""
}

# ============================================================================
# FASE 5: TESTES DE COMANDOS INTERNOS - HELP E INFO
# ============================================================================

test_phase_5_commands_help() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 5: Testes de Comandos - Help e Info"
    echo -e "==========================================${NC}\n"
    
    # 5.1 Comando help
    run_interactive_test \
        "Comando: help" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\nsair" \
        0 \
        "Comandos"
    
    # 5.2 Atalho h
    run_interactive_test \
        "Comando: h (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "h\nsair" \
        0 \
        "Comandos"
    
    # 5.3 Alias ajuda
    run_interactive_test \
        "Comando: ajuda (alias)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "ajuda\nsair" \
        0 \
        "Comandos"
    
    # 5.4 Alias ?
    run_interactive_test \
        "Comando: ? (alias)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "?\nsair" \
        0 \
        "Comandos"
    
    # 5.5 Comando stats
    run_interactive_test \
        "Comando: stats" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "chunks"
    
    # 5.6 Atalho s
    run_interactive_test \
        "Comando: s (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "s\nsair" \
        0 \
        "chunks"
    
    # 5.7 Comando history vazio
    run_interactive_test \
        "Comando: history (vazio)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "history\nsair" \
        0 \
        ""
    
    # 5.8 Comando history com comandos
    run_interactive_test \
        "Comando: history (com comandos)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\nstats\nhistory\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 6: TESTES DE COMANDOS INTERNOS - GERENCIAMENTO DE DOCUMENTOS
# ============================================================================

test_phase_6_commands_docs() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 6: Testes de Comandos - Gerenciamento de Documentos"
    echo -e "==========================================${NC}\n"
    
    # Limpar banco antes dos testes
    clear_database
    
    # 6.1 Comando add
    run_interactive_test \
        "Comando: add <pdf>" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add $TEST_DATA_DIR/small.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.2 Atalho a
    run_interactive_test \
        "Comando: a <pdf> (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "a $TEST_DATA_DIR/medium.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.3 Alias ingest
    run_interactive_test \
        "Comando: ingest <pdf> (alias)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "ingest $TEST_DATA_DIR/large.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.4 Add sem argumento (erro)
    run_interactive_test \
        "Comando: add sem argumento (erro)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add\nsair" \
        0 \
        ""
    
    # 6.5 Add arquivo inexistente (erro)
    run_interactive_test \
        "Comando: add arquivo inexistente (erro)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add arquivo_inexistente.pdf\nsair" \
        0 \
        ""
    
    # 6.6 Comando remove
    run_interactive_test \
        "Comando: remove <arquivo>" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "remove small.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.7 Atalho r
    run_interactive_test \
        "Comando: r <arquivo> (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "r medium.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.8 Alias delete
    run_interactive_test \
        "Comando: delete <arquivo> (alias)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "delete large.pdf\nsim\nsair" \
        0 \
        ""
    
    # 6.9 Remove sem argumento (erro)
    run_interactive_test \
        "Comando: remove sem argumento (erro)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "remove\nsair" \
        0 \
        ""
    
    # 6.10 Remove arquivo inexistente (erro)
    run_interactive_test \
        "Comando: remove arquivo inexistente (erro)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "remove arquivo_inexistente.pdf\nsair" \
        0 \
        ""
    
    # 6.11 Comando clear
    # Primeiro adicionar um PDF
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Comando: clear" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nsim\nsair" \
        0 \
        ""
    
    # 6.12 Atalho c
    # Adicionar PDF novamente
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Comando: c (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "c\nsim\nsair" \
        0 \
        ""
    
    # 6.13 Clear com banco vazio
    run_interactive_test \
        "Comando: clear com banco vazio" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nsair" \
        0 \
        ""
    
    # 6.14 Clear cancelado
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Comando: clear cancelado" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nn\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 7: TESTES DE COMANDOS INTERNOS - REPETIÇÃO E HISTÓRICO
# ============================================================================

test_phase_7_commands_history() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 7: Testes de Comandos - Repetição e Histórico"
    echo -e "==========================================${NC}\n"
    
    # 7.1 Repetição !1
    run_interactive_test \
        "Comando: !1 (repetir primeiro)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\n!1\nsair" \
        0 \
        ""
    
    # 7.2 Repetição !2
    run_interactive_test \
        "Comando: !2 (repetir segundo)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\nstats\n!2\nsair" \
        0 \
        ""
    
    # 7.3 Repetição índice inexistente
    run_interactive_test \
        "Comando: !99 (índice inexistente)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "!99\nsair" \
        0 \
        ""
    
    # 7.4 Repetição índice 0
    run_interactive_test \
        "Comando: !0 (índice inválido)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "!0\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 8: TESTES DE COMANDOS INTERNOS - SAÍDA
# ============================================================================

test_phase_8_commands_exit() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 8: Testes de Comandos - Saída"
    echo -e "==========================================${NC}\n"
    
    # 8.1 Comando sair
    run_interactive_test \
        "Comando: sair" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "sair" \
        0 \
        ""
    
    # 8.2 Comando exit
    run_interactive_test \
        "Comando: exit" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "exit" \
        0 \
        ""
    
    # 8.3 Comando quit
    run_interactive_test \
        "Comando: quit" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "quit" \
        0 \
        ""
    
    # 8.4 Atalho q
    run_interactive_test \
        "Comando: q (atalho)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "q" \
        0 \
        ""
}

# ============================================================================
# FASE 9: TESTES DE PERGUNTAS
# ============================================================================

test_phase_9_questions() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 9: Testes de Perguntas"
    echo -e "==========================================${NC}\n"
    
    # Garantir que há documentos no banco
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    # 9.1 Pergunta simples
    run_interactive_test \
        "Pergunta: simples" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "Qual o conteúdo do documento?\nsair" \
        0 \
        ""
    
    # 9.2 Pergunta em modo verbose
    run_interactive_test \
        "Pergunta: modo verbose" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet --verbose" \
        "Qual o conteúdo?\nsair" \
        0 \
        ""
    
    # 9.3 Pergunta com banco vazio
    clear_database
    
    run_interactive_test \
        "Pergunta: banco vazio (deve alertar)" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "Qual o conteúdo?\nsair" \
        0 \
        ""
    
    # 9.4 Múltiplas perguntas sequenciais
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Perguntas: múltiplas sequenciais" \
        "timeout 120 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "Pergunta 1?\nPergunta 2?\nPergunta 3?\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 10: TESTES DE COMBINAÇÕES COMPLEXAS
# ============================================================================

test_phase_10_complex_scenarios() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 10: Testes de Combinações Complexas"
    echo -e "==========================================${NC}\n"
    
    # Limpar banco
    clear_database
    
    # 10.1 Fluxo completo: add → stats → pergunta → sair
    run_interactive_test \
        "Fluxo: add → stats → pergunta → sair" \
        "timeout 120 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add $TEST_DATA_DIR/small.pdf\nsim\nstats\nQual o conteúdo?\nsair" \
        0 \
        ""
    
    # 10.2 Múltiplos PDFs
    clear_database
    
    run_interactive_test \
        "Fluxo: múltiplos PDFs" \
        "timeout 90 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add $TEST_DATA_DIR/small.pdf\nsim\nadd $TEST_DATA_DIR/medium.pdf\nsim\nstats\nsair" \
        0 \
        ""
    
    # 10.3 Add + remove + stats
    run_interactive_test \
        "Fluxo: add + remove + stats" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "add $TEST_DATA_DIR/small.pdf\nsim\nstats\nremove small.pdf\nsim\nstats\nsair" \
        0 \
        ""
    
    # 10.4 Uso de histórico com repetições
    run_interactive_test \
        "Fluxo: histórico com repetições" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\nstats\n!1\n!2\nsair" \
        0 \
        ""
    
    # 10.5 Chat com -f + parâmetros múltiplos
    run_interactive_test \
        "Fluxo: -f + múltiplos parâmetros" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py -f $TEST_DATA_DIR/small.pdf --top-k 5 --temperature 0.5 --quiet" \
        "stats\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 11: TESTES DE ROBUSTEZ E CASOS EXTREMOS
# ============================================================================

test_phase_11_robustness() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 11: Testes de Robustez e Casos Extremos"
    echo -e "==========================================${NC}\n"
    
    # 11.1 Comando inexistente
    run_interactive_test \
        "Robustez: comando inexistente" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "comando_invalido\nsair" \
        0 \
        ""
    
    # 11.2 Entrada vazia (múltiplas)
    run_interactive_test \
        "Robustez: entradas vazias" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "\n\n\nsair" \
        0 \
        ""
    
    # 11.3 Confirmação com variações
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Robustez: confirmação 'SIM'" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nSIM\nsair" \
        0 \
        ""
    
    # 11.4 Confirmação cancelada
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Robustez: confirmação 'n'" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nn\nsair" \
        0 \
        ""
    
    # 11.5 Confirmação com texto aleatório
    run_interactive_test \
        "Robustez: confirmação texto aleatório" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\ntexto_aleatorio\nsair" \
        0 \
        ""
    
    # 11.6 Stats com banco vazio
    clear_database
    
    run_interactive_test \
        "Robustez: stats com banco vazio" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        ""
    
    # 11.7 Remove com banco vazio
    run_interactive_test \
        "Robustez: remove com banco vazio" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "remove arquivo.pdf\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 12: TESTES DE INTEGRAÇÃO COM PROVEDOR
# ============================================================================

test_phase_12_provider() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 12: Testes de Integração com Provedor"
    echo -e "==========================================${NC}\n"
    
    # Garantir que há documentos
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    # 12.1 Ingestão com Google (gera embeddings)
    run_test \
        "Provedor: ingestão com Google" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf --quiet" \
        0 \
        ""
    
    # 12.2 Pergunta com Google (usa LLM)
    run_interactive_test \
        "Provedor: pergunta com Google" \
        "timeout 60 $VENV_PYTHON $PROJECT_ROOT/src/chat.py --provider google --quiet" \
        "Qual o conteúdo?\nsair" \
        0 \
        ""
    
    # 12.3 Chat com provedor explícito
    run_interactive_test \
        "Provedor: --provider google" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --provider google --quiet" \
        "stats\nsair" \
        0 \
        ""
}

# ============================================================================
# FASE 13: TESTES DE VALIDAÇÃO DE SAÍDA
# ============================================================================

test_phase_13_output_validation() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 13: Testes de Validação de Saída"
    echo -e "==========================================${NC}\n"
    
    # 13.1 Validar formato stats
    run_interactive_test \
        "Saída: formato stats" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "chunks"
    
    # 13.2 Validar formato help
    run_interactive_test \
        "Saída: formato help" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "help\nsair" \
        0 \
        "Comandos"
    
    # 13.3 Validar saída quiet (sem logs)
    run_interactive_test \
        "Saída: modo quiet sem logs" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "sair" \
        0 \
        ""
    
    # 13.4 Validar estatísticas de ingestão
    run_interactive_test \
        "Saída: estatísticas de ingestão" \
        "$VENV_PYTHON $PROJECT_ROOT/src/ingest.py $TEST_DATA_DIR/small.pdf 2>&1" \
        "sim\n" \
        0 \
        "ESTATÍSTICAS"
}

# ============================================================================
# FASE 14: TESTES DE PERSISTÊNCIA E ESTADO
# ============================================================================

test_phase_14_persistence() {
    echo -e "\n${BLUE}=========================================="
    echo "FASE 14: Testes de Persistência e Estado"
    echo -e "==========================================${NC}\n"
    
    # Limpar banco
    clear_database
    
    # 14.1 Persistência entre comandos
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    
    run_interactive_test \
        "Persistência: PDF persiste entre sessões" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "chunks"
    
    # 14.2 Clear persiste
    run_interactive_test \
        "Persistência: clear persiste" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "clear\nsim\nsair" \
        0 \
        ""
    
    # Validar que banco está vazio
    run_interactive_test \
        "Persistência: validar banco vazio após clear" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "vazia"
    
    # 14.3 Múltiplas sessões
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/small.pdf" --quiet
    "$VENV_PYTHON" "$PROJECT_ROOT/src/ingest.py" "$TEST_DATA_DIR/medium.pdf" --quiet
    
    run_interactive_test \
        "Persistência: múltiplos PDFs persistem" \
        "$VENV_PYTHON $PROJECT_ROOT/src/chat.py --quiet" \
        "stats\nsair" \
        0 \
        "Total de arquivos:        2"
}

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

show_usage() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --phase N    Executa apenas a fase N (1-14)"
    echo "  --failed     Executa apenas os testes que falharam na última rodada"
    echo "  --list       Lista todas as fases disponíveis"
    echo "  --help       Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 --phase 1"
    echo "  $0 --failed"
}

list_phases() {
    echo "Fases disponíveis:"
    echo "  1: Ingestão Básica"
    echo "  2: Casos de Erro de Ingestão"
    echo "  3: Chat CLI Básico"
    echo "  4: Chat CLI Avançado"
    echo "  5: Comandos Help e Info"
    echo "  6: Gerenciamento de Documentos"
    echo "  7: Repetição e Histórico"
    echo "  8: Comandos de Saída"
    echo "  9: Perguntas e Respostas"
    echo "  10: Combinações Complexas"
    echo "  11: Robustez e Casos Extremos"
    echo "  12: Integração com Provedor"
    echo "  13: Validação de Saída"
    echo "  14: Persistência e Estado"
}

main() {
    # Parse argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --phase)
                SELECTED_PHASE="$2"
                shift 2
                ;;
            --failed)
                ONLY_FAILED=true
                shift
                ;;
            --list)
                list_phases
                exit 0
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                echo "Opção desconhecida: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validar SELECTED_PHASE se informada
    if [ -n "$SELECTED_PHASE" ]; then
        if [[ ! "$SELECTED_PHASE" =~ ^[1-9]$|^1[0-4]$ ]]; then
            echo "Erro: Fase inválida '$SELECTED_PHASE'. Use um número de 1 a 14."
            exit 1
        fi
    fi

    # Validar --failed se o arquivo não existir
    if [ "$ONLY_FAILED" = true ] && [ ! -s "$FAILED_LIST" ]; then
        echo -e "${GREEN}✨ Nenhum teste falhou na última rodada! Nada para re-executar.${NC}"
        exit 0
    fi

    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║        SUITE COMPLETA DE TESTES E2E - SISTEMA RAG          ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}\n"

    if [ "$ONLY_FAILED" = true ]; then
        echo -e "${YELLOW}🔁 RE-EXECUTANDO APENAS TESTES FALHADOS${NC}\n"
    elif [ -n "$SELECTED_PHASE" ]; then
        echo -e "${CYAN}🎯 EXECUTANDO APENAS FASE $SELECTED_PHASE${NC}\n"
    fi
    
    # Setup
    setup_test_environment
    
    # Criar PDFs de teste (sempre necessário)
    echo -e "${BLUE}📄 Verificando/Criando PDFs de teste...${NC}\n"
    
    # Verificar fpdf2
    "$VENV_PYTHON" -c "import fpdf" 2>/dev/null || "$VENV_PYTHON" -m pip install fpdf2 --quiet
    
    create_test_pdf "small.pdf" 1
    create_test_pdf "medium.pdf" 5
    create_test_pdf "large.pdf" 20
    
    echo ""
    
    # Executar conforme filtros
    run_phase() {
        local phase_num="$1"
        local phase_func="$2"
        if [ -z "$SELECTED_PHASE" ] || [ "$SELECTED_PHASE" = "$phase_num" ]; then
            $phase_func
        fi
    }

    run_phase 1 test_phase_1_ingest_basic
    run_phase 2 test_phase_2_ingest_errors
    run_phase 3 test_phase_3_chat_cli_basic
    run_phase 4 test_phase_4_chat_cli_advanced
    run_phase 5 test_phase_5_commands_help
    run_phase 6 test_phase_6_commands_docs
    run_phase 7 test_phase_7_commands_history
    run_phase 8 test_phase_8_commands_exit
    run_phase 9 test_phase_9_questions
    run_phase 10 test_phase_10_complex_scenarios
    run_phase 11 test_phase_11_robustness
    run_phase 12 test_phase_12_provider
    run_phase 13 test_phase_13_output_validation
    run_phase 14 test_phase_14_persistence
    
    if [ $TOTAL_TESTS -eq 0 ] && [ "$ONLY_FAILED" = true ]; then
         echo -e "${GREEN}✅ Todos os testes falhados anteriormente agora passaram!${NC}"
    fi

    # Gerar relatório (apenas se não for rodada parcial ou se algo rodou)
    if [ $TOTAL_TESTS -gt 0 ]; then
        generate_report
        show_summary
    fi
    
    # Cleanup
    cleanup
    
    # Retornar código apropriado
    [ $FAILED_TESTS -eq 0 ] && exit 0 || exit 1
}

# Executar
main "$@"
