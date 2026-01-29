#!/bin/bash

# Funções auxiliares para testes E2E

# Cores
export GREEN='\033[0;32m'
export RED='\033[0;31m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export NC='\033[0m' # No Color

# Contadores globais
export TOTAL_TESTS=0
export PASSED_TESTS=0
export FAILED_TESTS=0
export SKIPPED_TESTS=0

# Diretórios
export PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TEST_DIR="$PROJECT_ROOT/tests"
export TEST_DATA_DIR="$TEST_DIR/test_data"
export TEST_RESULTS_DIR="$TEST_DIR/test_results"
export TEST_TEMP_DIR="$TEST_DIR/temp"
export VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

# Arquivos de log
export TEST_LOG="$TEST_RESULTS_DIR/logs/test_execution.log"
export RESULTS_FILE="$TEST_RESULTS_DIR/test_e2e_results.md"
export FAILED_LIST="$TEST_RESULTS_DIR/logs/failed_tests.list"

# Filtros de execução
export ONLY_FAILED=false
export SELECTED_PHASE=""

# Função para inicializar ambiente de testes
setup_test_environment() {
    echo -e "${BLUE}=========================================="
    echo "🧪 CONFIGURANDO AMBIENTE DE TESTES"
    echo -e "==========================================${NC}\n"
    
    # Criar diretórios se não existirem
    mkdir -p "$TEST_DATA_DIR" "$TEST_RESULTS_DIR/logs" "$TEST_TEMP_DIR"
    
    # Limpar logs anteriores se não estiver rodando apenas falhas
    if [ "$ONLY_FAILED" = false ] && [ -z "$SELECTED_PHASE" ]; then
        > "$TEST_LOG"
        > "$FAILED_LIST"
    fi
    
    # Verificar se venv existe
    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}❌ Ambiente virtual não encontrado em $VENV_PYTHON${NC}"
        exit 1
    fi
    
    # Verificar se banco está rodando
    if ! docker ps | grep -q postgres_rag; then
        echo -e "${YELLOW}⚠️  PostgreSQL não está rodando. Iniciando...${NC}"
        cd "$PROJECT_ROOT" && docker-compose up -d
        sleep 5
    fi
    
    # Verificar .env
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        echo -e "${RED}❌ Arquivo .env não encontrado${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Ambiente configurado com sucesso${NC}\n"
}

run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="${3:-0}"
    local expected_output="${4:-}"
    
    # Lógica de filtro: Se ONLY_FAILED for true, verificar se este teste está na lista de falhas
    if [ "$ONLY_FAILED" = true ]; then
        if ! grep -Fxq "$test_name" "$FAILED_LIST" 2>/dev/null; then
            return 0
        fi
    fi

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${CYAN}[Teste $TOTAL_TESTS] $test_name${NC}" | tee -a "$TEST_LOG"
    echo "Comando: $command" >> "$TEST_LOG"
    
    # Executar comando e capturar saída
    local output_file="$TEST_TEMP_DIR/test_${TOTAL_TESTS}_output.txt"
    local error_file="$TEST_TEMP_DIR/test_${TOTAL_TESTS}_error.txt"
    
    # Executar diretamente com eval (variáveis já expandidas)
    eval "$command" > "$output_file" 2> "$error_file"
    local actual_exit_code=$?
    
    local test_failed=false

    # Verificar exit code
    if [ "$actual_exit_code" -ne "$expected_exit_code" ]; then
        echo -e "${RED}  ❌ FALHOU - Exit code esperado: $expected_exit_code, obtido: $actual_exit_code${NC}" | tee -a "$TEST_LOG"
        test_failed=true
    fi
    
    # Verificar output esperado (se fornecido)
    if [ "$test_failed" = false ] && [ -n "$expected_output" ]; then
        if ! grep -qi "$expected_output" "$output_file" 2>/dev/null; then
            echo -e "${RED}  ❌ FALHOU - Output esperado não encontrado: '$expected_output'${NC}" | tee -a "$TEST_LOG"
            test_failed=true
        fi
    fi

    if [ "$test_failed" = true ]; then
        echo "  Saída:" >> "$TEST_LOG"
        cat "$output_file" >> "$TEST_LOG"
        echo "  Erros:" >> "$TEST_LOG"
        cat "$error_file" >> "$TEST_LOG"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        # Registrar falha se ainda não estiver na lista
        grep -Fxq "$test_name" "$FAILED_LIST" 2>/dev/null || echo "$test_name" >> "$FAILED_LIST"
        return 1
    fi
    
    echo -e "${GREEN}  ✅ PASSOU${NC}" | tee -a "$TEST_LOG"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    # Remover da lista de falhas se passar
    if [ -f "$FAILED_LIST" ]; then
        sed -i "/^$(echo "$test_name" | sed 's/[\/&]/\\&/g')$/d" "$FAILED_LIST"
    fi
    return 0
}

# Função para executar teste interativo (com input)
# Uso: run_interactive_test "Nome" "comando" "input" "exit_code_esperado" "output_esperado"
run_interactive_test() {
    local test_name="$1"
    local command="$2"
    local input="$3"
    local expected_exit_code="${4:-0}"
    local expected_output="${5:-}"
    
    # Lógica de filtro
    if [ "$ONLY_FAILED" = true ]; then
        if ! grep -Fxq "$test_name" "$FAILED_LIST" 2>/dev/null; then
            return 0
        fi
    fi

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${CYAN}[Teste $TOTAL_TESTS] $test_name${NC}" | tee -a "$TEST_LOG"
    echo "Comando: $command" >> "$TEST_LOG"
    echo "Input: $input" >> "$TEST_LOG"
    
    local output_file="$TEST_TEMP_DIR/test_${TOTAL_TESTS}_output.txt"
    local error_file="$TEST_TEMP_DIR/test_${TOTAL_TESTS}_error.txt"
    
    # Executar com input via echo
    echo -e "$input" | eval "$command" > "$output_file" 2> "$error_file"
    local actual_exit_code=$?
    
    local test_failed=false

    # Verificar exit code
    if [ "$actual_exit_code" -ne "$expected_exit_code" ]; then
        echo -e "${RED}  ❌ FALHOU - Exit code esperado: $expected_exit_code, obtido: $actual_exit_code${NC}" | tee -a "$TEST_LOG"
        test_failed=true
    fi
    
    # Verificar output
    if [ "$test_failed" = false ] && [ -n "$expected_output" ]; then
        if ! grep -qi "$expected_output" "$output_file" 2>/dev/null; then
            echo -e "${RED}  ❌ FALHOU - Output esperado não encontrado${NC}" | tee -a "$TEST_LOG"
            test_failed=true
        fi
    fi

    if [ "$test_failed" = true ]; then
        echo "  Saída:" >> "$TEST_LOG"
        cat "$output_file" >> "$TEST_LOG"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        grep -Fxq "$test_name" "$FAILED_LIST" 2>/dev/null || echo "$test_name" >> "$FAILED_LIST"
        return 1
    fi
    
    echo -e "${GREEN}  ✅ PASSOU${NC}" | tee -a "$TEST_LOG"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    if [ -f "$FAILED_LIST" ]; then
        sed -i "/^$(echo "$test_name" | sed 's/[\/&]/\\&/g')$/d" "$FAILED_LIST"
    fi
    return 0
}

# Função para pular teste
skip_test() {
    local test_name="$1"
    local reason="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
    
    echo -e "${YELLOW}[Teste $TOTAL_TESTS] $test_name - PULADO: $reason${NC}" | tee -a "$TEST_LOG"
}

# Função para limpar banco de dados
clear_database() {
    echo "Limpando banco de dados..." >> "$TEST_LOG"
    echo "clear\nsim\nsair" | timeout 10 "$VENV_PYTHON" "$PROJECT_ROOT/src/chat.py" --quiet > /dev/null 2>&1 || true
}

# Função para contar documentos no banco
count_documents() {
    local count=$(echo "stats\nsair" | timeout 10 "$VENV_PYTHON" "$PROJECT_ROOT/src/chat.py" --quiet 2>/dev/null | grep -oP '\d+(?= chunks)' | head -1)
    echo "${count:-0}"
}

# Função para criar PDF de teste
create_test_pdf() {
    local filename="$1"
    local num_pages="${2:-1}"
    local output_path="$TEST_DATA_DIR/$filename"
    
    # Usar fpdf2 para criar PDF
    "$VENV_PYTHON" - <<EOF
from fpdf import FPDF
from fpdf.enums import XPos, YPos

pdf = FPDF()
for i in range($num_pages):
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(200, 10, text=f"Página {i+1} de $num_pages", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.multi_cell(0, 10, text="Este é um documento de teste para o sistema RAG. " * 50)

pdf.output("$output_path")
EOF
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PDF criado: $output_path${NC}"
    else
        echo -e "${RED}❌ Erro ao criar PDF: $output_path${NC}"
        return 1
    fi
}

# Função para gerar relatório final
generate_report() {
    echo -e "\n${BLUE}=========================================="
    echo "📊 GERANDO RELATÓRIO DE TESTES"
    echo -e "==========================================${NC}\n"
    
    local pass_rate=0
    if [ $TOTAL_TESTS -gt 0 ]; then
        pass_rate=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS / $TOTAL_TESTS) * 100}")
    fi
    
    cat > "$RESULTS_FILE" <<EOF
# Relatório de Testes E2E - Sistema RAG

**Data:** $(date '+%Y-%m-%d %H:%M:%S')  
**Duração:** ${SECONDS}s

## Resumo Executivo

| Métrica | Valor |
|---------|-------|
| **Total de Testes** | $TOTAL_TESTS |
| **Testes Passados** | $PASSED_TESTS ✅ |
| **Testes Falhados** | $FAILED_TESTS ❌ |
| **Testes Pulados** | $SKIPPED_TESTS ⏭️ |
| **Taxa de Sucesso** | ${pass_rate}% |

## Status

EOF

    if [ $FAILED_TESTS -eq 0 ]; then
        echo "✅ **TODOS OS TESTES PASSARAM!**" >> "$RESULTS_FILE"
    else
        echo "❌ **ALGUNS TESTES FALHARAM**" >> "$RESULTS_FILE"
    fi
    
    cat >> "$RESULTS_FILE" <<EOF

## Detalhes

Para logs completos, consulte: \`test_results/logs/test_execution.log\`

## Próximos Passos

EOF

    if [ $FAILED_TESTS -gt 0 ]; then
        echo "1. Revisar logs de testes falhados" >> "$RESULTS_FILE"
        echo "2. Corrigir problemas identificados" >> "$RESULTS_FILE"
        echo "3. Re-executar suite de testes" >> "$RESULTS_FILE"
    else
        echo "1. ✅ Sistema validado e pronto para release" >> "$RESULTS_FILE"
        echo "2. Atualizar documentação se necessário" >> "$RESULTS_FILE"
        echo "3. Marcar tarefa 1.5.1 como concluída no TODOs.md" >> "$RESULTS_FILE"
    fi
    
    echo -e "${GREEN}✅ Relatório gerado: $RESULTS_FILE${NC}\n"
}

# Função para exibir resumo final
show_summary() {
    echo -e "\n${BLUE}=========================================="
    echo "📊 RESUMO DOS TESTES"
    echo -e "==========================================${NC}"
    echo -e "Total:    ${TOTAL_TESTS}"
    echo -e "Passou:   ${GREEN}${PASSED_TESTS}${NC}"
    echo -e "Falhou:   ${RED}${FAILED_TESTS}${NC}"
    echo -e "Pulados:  ${YELLOW}${SKIPPED_TESTS}${NC}"
    
    if [ $TOTAL_TESTS -gt 0 ]; then
        local pass_rate=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS / $TOTAL_TESTS) * 100}")
        echo -e "Taxa:     ${pass_rate}%"
    fi
    
    echo -e "${BLUE}==========================================${NC}\n"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}✅ TODOS OS TESTES PASSARAM! Sistema pronto para release! 🚀${NC}\n"
        return 0
    else
        echo -e "${RED}❌ ALGUNS TESTES FALHARAM. Revise os logs para detalhes.${NC}\n"
        return 1
    fi
}

# Função para cleanup
cleanup() {
    echo -e "\n${BLUE}🧹 Limpando arquivos temporários...${NC}"
    # Manter logs mas limpar outputs temporários
    rm -f "$TEST_TEMP_DIR"/test_*_output.txt
    rm -f "$TEST_TEMP_DIR"/test_*_error.txt
    echo -e "${GREEN}✅ Cleanup concluído${NC}\n"
}
