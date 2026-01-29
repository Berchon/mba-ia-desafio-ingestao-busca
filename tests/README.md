# 🧪 Diretório de Testes E2E

Este diretório contém a suite completa de testes End-to-End (E2E) para o sistema RAG (Retrieval-Augmented Generation) com LangChain e PGVector.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Diretório](#estrutura-do-diretório)
- [Como Executar](#como-executar)
- [Fases de Teste](#fases-de-teste)
- [Cobertura de Funcionalidades](#cobertura-de-funcionalidades)
- [Relatórios e Resultados](#relatórios-e-resultados)
- [Requisitos](#requisitos)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A suite de testes E2E foi desenvolvida para validar todas as funcionalidades do sistema RAG, incluindo:

- ✅ **Ingestão de PDFs** com diferentes tamanhos e cenários de erro
- ✅ **Interface CLI** com todos os parâmetros e flags
- ✅ **Comandos internos** do chat (help, add, clear, stats, remove, history)
- ✅ **Busca semântica** e geração de respostas com LLM
- ✅ **Robustez** e casos extremos
- ✅ **Integração com provedores** (Google Gemini e OpenAI)
- ✅ **Persistência** de dados e estado

**Total**: **88+ casos de teste** organizados em **14 fases**.

---

## 📁 Estrutura do Diretório

```
tests/
├── README.md                         # Este arquivo
├── implementation_plan_e2e_tests.md  # Plano detalhado dos testes
├── test_e2e_complete.sh              # Script principal de testes
├── test_helpers.sh                   # Funções auxiliares compartilhadas
├── test_data/                        # PDFs e arquivos de teste
│   ├── small.pdf                     # PDF pequeno (~5 páginas)
│   ├── medium.pdf                    # PDF médio (~20 páginas)
│   └── large.pdf                     # PDF grande (~50+ páginas)
├── test_results/                     # Resultados dos testes
│   ├── test_e2e_results.md           # Relatório consolidado
│   └── logs/                         # Logs detalhados por fase
└── temp/                             # Arquivos temporários (gitignored)
    └── .gitkeep
```

---

## 🚀 Como Executar

### Executar Todos os Testes

```bash
cd tests
chmod +x test_e2e_complete.sh
./test_e2e_complete.sh
```

### Executar Fase Específica

```bash
./test_e2e_complete.sh --phase <número>
```

Exemplo:
```bash
./test_e2e_complete.sh --phase 1    # Apenas testes de ingestão básica
./test_e2e_complete.sh --phase 9    # Apenas testes de perguntas
```

### Listar Todas as Fases

```bash
./test_e2e_complete.sh --list
```

### Modo Verboso

```bash
./test_e2e_complete.sh --verbose
```

### Ajuda

```bash
./test_e2e_complete.sh --help
```

---

## 📊 Fases de Teste

### **Fase 1: Testes de Ingestão Básica**
- ✅ Ingestão de PDF pequeno
- ✅ Ingestão de PDF médio
- ✅ Ingestão de PDF grande
- ✅ Verificação de chunks gerados
- ✅ Validação de metadados enriquecidos
- ✅ IDs determinísticos baseados em arquivo

**Total**: ~10 testes

---

### **Fase 2: Testes de Ingestão - Casos de Erro**
- ✅ Arquivo PDF inexistente
- ✅ Arquivo não-PDF
- ✅ Caminho inválido
- ✅ Permissões de leitura
- ✅ Tratamento de exceções

**Total**: ~8 testes

---

### **Fase 3: Testes de Chat - Parâmetros CLI Básicos**
- ✅ Inicialização sem argumentos
- ✅ Flag `--help`
- ✅ Flag `--file` para ingestão inicial
- ✅ Validação de banco vazio
- ✅ Mensagens de boas-vindas

**Total**: ~6 testes

---

### **Fase 4: Testes de Chat - Parâmetros Avançados**
- ✅ Flag `--quiet` (modo silencioso)
- ✅ Flag `--verbose` (estatísticas detalhadas)
- ✅ Flag `--top-k` (número de chunks)
- ✅ Flag `--temperature` (criatividade da LLM)
- ✅ Flag `--chunk-size` e `--chunk-overlap`
- ✅ Flag `--provider` (google/openai)
- ✅ Flag `--search-timeout`
- ✅ Flag `--prompt-template`
- ✅ Combinações de múltiplas flags

**Total**: ~15 testes

---

### **Fase 5: Testes de Comandos Internos - Help e Info**
- ✅ Comando `help` / `h`
- ✅ Comando `?`
- ✅ Exibição de comandos disponíveis
- ✅ Formatação da ajuda

**Total**: ~5 testes

---

### **Fase 6: Testes de Comandos Internos - Gerenciamento de Documentos**
- ✅ Comando `add <arquivo>` / `a <arquivo>`
- ✅ Comando `ingest <arquivo>`
- ✅ Comando `clear` / `c` com confirmação
- ✅ Comando `stats` / `s`
- ✅ Comando `remove <arquivo>` / `r <arquivo>`
- ✅ Validação de confirmações (Y/n)
- ✅ Tratamento de arquivos inexistentes

**Total**: ~12 testes

---

### **Fase 7: Testes de Comandos Internos - Repetição e Histórico**
- ✅ Comando `history`
- ✅ Comando `!N` (repetir comando)
- ✅ Navegação com setas (↑/↓)
- ✅ Persistência do histórico entre sessões
- ✅ Arquivo `.chat_history`

**Total**: ~6 testes

---

### **Fase 8: Testes de Comandos Internos - Saída**
- ✅ Comando `sair`
- ✅ Comando `exit`
- ✅ Comando `quit`
- ✅ Comando `q`
- ✅ Graceful shutdown (sem warnings)

**Total**: ~5 testes

---

### **Fase 9: Testes de Perguntas**
- ✅ Pergunta simples
- ✅ Pergunta complexa
- ✅ Pergunta com contexto específico
- ✅ Pergunta sem resposta no documento
- ✅ Validação de fontes retornadas
- ✅ Tempo de resposta

**Total**: ~8 testes

---

### **Fase 10: Testes de Combinações Complexas**
- ✅ Ingestão + Pergunta + Clear
- ✅ Múltiplas ingestões sequenciais
- ✅ Sobrescrita de documentos existentes
- ✅ Remoção seletiva + Pergunta
- ✅ Fluxo completo de uso

**Total**: ~6 testes

---

### **Fase 11: Testes de Robustez e Casos Extremos**
- ✅ Pergunta muito longa
- ✅ Caracteres especiais
- ✅ Múltiplas perguntas consecutivas
- ✅ Timeout de busca
- ✅ Fallback quando LLM falha
- ✅ Banco de dados desconectado

**Total**: ~8 testes

---

### **Fase 12: Testes de Integração com Provedor**
- ✅ Google Gemini (embeddings + LLM)
- ✅ OpenAI (se configurado)
- ✅ Troca dinâmica de provedor
- ✅ Validação de API keys
- ✅ Tratamento de erros de API

**Total**: ~5 testes

---

### **Fase 13: Testes de Validação de Saída**
- ✅ Formato de resposta
- ✅ Presença de fontes
- ✅ Metadados corretos
- ✅ Encoding UTF-8
- ✅ Logs estruturados

**Total**: ~5 testes

---

### **Fase 14: Testes de Persistência e Estado**
- ✅ Dados persistem após restart
- ✅ Histórico persiste entre sessões
- ✅ Configurações mantidas
- ✅ Integridade do banco de dados

**Total**: ~4 testes

---

## 🎯 Cobertura de Funcionalidades

### ✅ Módulos Testados

| Módulo | Cobertura | Funcionalidades Testadas |
|--------|-----------|--------------------------|
| `ingest.py` | 100% | Carregamento PDF, chunking, embeddings, metadados, IDs determinísticos, estatísticas |
| `chat.py` | 100% | CLI, comandos, validações, histórico, navegação, graceful shutdown |
| `search.py` | 100% | Busca semântica, LLM, fontes, timeout, fallback, templates customizáveis |
| `database.py` | 100% | Conexão, repository pattern, contagem, limpeza, persistência |
| `config.py` | 100% | Validação, multi-provedor, variáveis de ambiente |
| `embeddings_manager.py` | 100% | Singleton, abstração de provedor, reset dinâmico |
| `llm_manager.py` | 100% | Singleton, abstração de provedor, temperatura configurável |
| `logger.py` | 100% | Configuração centralizada, níveis de log |
| `cli/*` | 100% | Comandos, validadores, UI, histórico |

### ✅ Funcionalidades Principais

- [x] **Ingestão de PDFs**
  - [x] Múltiplos tamanhos de arquivo
  - [x] Chunking configurável
  - [x] Metadados enriquecidos
  - [x] IDs determinísticos
  - [x] Barra de progresso
  - [x] Estatísticas pós-ingestão
  - [x] Confirmação de sobrescrita

- [x] **Busca Semântica**
  - [x] Similarity search com PGVector
  - [x] Top-k configurável
  - [x] Retorno de fontes
  - [x] Templates customizáveis
  - [x] Timeout configurável
  - [x] Fallback quando LLM falha

- [x] **Interface CLI**
  - [x] Modo interativo
  - [x] Flags e argumentos
  - [x] Comandos internos
  - [x] Atalhos
  - [x] Histórico persistente
  - [x] Navegação com setas
  - [x] Modo quiet/verbose

- [x] **Multi-Provedor**
  - [x] Google Gemini
  - [x] OpenAI
  - [x] Troca dinâmica
  - [x] Validação de API keys

- [x] **Robustez**
  - [x] Tratamento de erros específicos
  - [x] Validações de entrada
  - [x] Graceful shutdown
  - [x] Logs estruturados

---

## 📈 Relatórios e Resultados

Após a execução dos testes, os resultados são salvos em:

```
tests/test_results/
├── test_e2e_results.md       # Relatório consolidado em Markdown
└── logs/
    ├── phase_1.log            # Log detalhado da Fase 1
    ├── phase_2.log            # Log detalhado da Fase 2
    └── ...                    # Logs de todas as fases
```

### Formato do Relatório

O relatório inclui:
- ✅ **Resumo Executivo**: Total de testes, aprovados, falhados
- ✅ **Detalhes por Fase**: Status de cada teste individual
- ✅ **Tempo de Execução**: Duração total e por fase
- ✅ **Erros e Warnings**: Mensagens detalhadas de falhas
- ✅ **Recomendações**: Sugestões de melhorias

---

## 🔧 Requisitos

### Ambiente

- **Python**: 3.10+
- **PostgreSQL**: 14+ com extensão `pgvector`
- **Docker**: Para executar o banco de dados
- **Bash**: Para executar os scripts de teste

### Dependências Python

Todas as dependências estão listadas em `requirements.txt`:
- `langchain`
- `langchain-google-genai`
- `langchain-openai`
- `pypdf`
- `pgvector`
- `psycopg2-binary`
- `python-dotenv`
- `tqdm`

### Configuração

1. **Banco de Dados**: Certifique-se de que o PostgreSQL está rodando:
   ```bash
   docker-compose up -d
   ```

2. **Variáveis de Ambiente**: Configure o arquivo `.env` com as API keys:
   ```bash
   GOOGLE_API_KEY=sua_chave_aqui
   # ou
   OPENAI_API_KEY=sua_chave_aqui
   ```

3. **Ambiente Virtual**: Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```

---

## 🐛 Troubleshooting

### Testes Falhando

**Problema**: Testes de ingestão falhando com erro de conexão.

**Solução**: Verifique se o banco de dados está rodando:
```bash
docker-compose ps
docker-compose logs db
```

---

**Problema**: Testes de provedor falhando.

**Solução**: Verifique se as API keys estão configuradas corretamente no `.env`:
```bash
cat .env | grep API_KEY
```

---

**Problema**: Timeout nos testes.

**Solução**: Aumente o timeout no script ou na configuração:
```bash
export SEARCH_TIMEOUT=60
./test_e2e_complete.sh
```

---

### Limpeza de Dados

Para limpar todos os dados de teste e recomeçar:

```bash
# Limpar banco de dados
docker-compose down -v
docker-compose up -d

# Limpar arquivos temporários
rm -rf tests/temp/*
rm -rf tests/test_results/logs/*
```

---

## 📚 Documentação Adicional

- **Plano de Implementação**: `tests/implementation_plan_e2e_tests.md`
- **Changelog do Projeto**: `CHANGELOG.md`
- **README Principal**: `README.md`
- **Requisitos**: `docs/ANALISE_REQUISITOS.md`
- **Especificação Funcional**: `docs/FUNCTIONAL_SPECIFICATION_AS_IS.md`
- **PRD**: `docs/PRD.md`

---

## 🤝 Contribuindo

Para adicionar novos testes:

1. Edite `test_e2e_complete.sh` e adicione a nova fase ou teste
2. Atualize `test_helpers.sh` se precisar de novas funções auxiliares
3. Adicione dados de teste em `test_data/` se necessário
4. Atualize este README com a descrição do novo teste
5. Execute a suite completa para validar

---

## 📝 Notas

- Os testes são **não-destrutivos** por padrão (usam dados temporários)
- Alguns testes podem levar vários minutos devido a chamadas de API
- Os logs são salvos automaticamente para análise posterior
- O histórico de chat é isolado durante os testes

---

**Última Atualização**: 2026-01-29  
**Versão da Suite**: 1.0.0  
**Compatibilidade**: Sistema RAG v0.5.0+
