# Diretório de Testes E2E

Este diretório contém a suite completa de testes End-to-End para o sistema RAG.

## Estrutura

```
tests/
├── README.md                         # Este arquivo
├── implementation_plan_e2e_tests.md  # Plano detalhado dos testes
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

## Como Executar

```bash
cd tests
chmod +x test_e2e_complete.sh
./test_e2e_complete.sh
```

## Fases de Teste

1. **Fase 1-2:** Testes de Ingestão (básica + erros)
2. **Fase 3-4:** Testes de Chat CLI (básico + avançado)
3. **Fase 5-8:** Testes de Comandos Internos
4. **Fase 9:** Testes de Perguntas
5. **Fase 10:** Testes de Combinações Complexas
6. **Fase 11:** Testes de Robustez
7. **Fase 12:** Testes de Provedor (Google Gemini)
8. **Fase 13:** Testes de Validação de Saída
9. **Fase 14:** Testes de Persistência

Total: **150+ casos de teste**

## Relatório de Resultados

Após execução, consulte: `test_results/test_e2e_results.md`
