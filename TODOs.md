# 📋 Checklist Detalhado do Projeto RAG com LangChain e PGVector

## 📌 Diretrizes de Desenvolvimento
- [x] **Referência**: Usar [github.com/Berchon/mba](https://github.com/Berchon/mba) como base técnica.
- [x] **Code Style**: Seguir PEP 8 e boas práticas de LangChain/IAs.
- [x] **Git Workflow**: 
    - [x] Criar uma branch para cada feature (ex: `feature/ingestao-pdf`).
    - [x] Commits frequentes e descritivos (Conventional Commits em inglês).
    - [x] **WORKFLOW**: Ver `.agent/workflows/development-workflow.md`
- [x] **Comunicação**: Manter pensamentos e diálogos em Português Brasileiro (PT-BR).

---

## Fase 1: Implementação Core (Requisitos Base + Melhorias Solicitadas)

### 1.1 Configuração do Ambiente
- [x] **1.1.1** Criar arquivo `.env` baseado no `.env.example`
- [x] **1.1.2** Criar/Configurar ambiente virtual Python
- [x] **1.1.3** Subir banco de dados com Docker

---

### 1.2 Implementação do `ingest.py` (Script de Ingestão)
- [x] **1.2.1** Criar branch `feature/ingest-implementation`
- [x] **1.2.2** Estrutura base do script
  - [x] Importar bibliotecas necessárias (`PyPDFLoader`, `RecursiveCharacterTextSplitter`, `PGVector`, embeddings)
  - [x] Carregar variáveis de ambiente com `dotenv`
  - [x] Configurar conexão com banco de dados (módulo `database.py` criado)
- [x] **1.2.3** Implementar carregamento do PDF
  - [x] Usar `PyPDFLoader` para carregar o PDF
  - [x] Extrair documentos/páginas do PDF (34 páginas carregadas)
- [x] **1.2.4** Implementar chunking do texto
  - [x] Usar `RecursiveCharacterTextSplitter` (`chunk_size=1000`, `chunk_overlap=150`) - 67 chunks gerados
- [x] **1.2.5** Implementar geração de embeddings (Google Gemini - `models/embedding-001`)
- [x] **1.2.6** Implementar armazenamento no PGVector
- [x] **1.2.7** Implementar controle de dados existentes (IDs determinísticos: `doc-0` a `doc-66`)
- [x] **1.2.8** Adicionar logs e feedback ao usuário
- [x] **1.2.9** Finalizar branch (Commit 7fd8729 concluído)

---

### 1.3 Implementação do `search.py` (Módulo de Busca)
- [x] **1.3.1** Criar branch `feature/search-implementation`
- [x] **1.3.2** Estrutura base e conexão PGVector (usando módulo `database.py`)
- [x] **1.3.3** Implementar busca semântica (`similarity_search`, k=10)
- [x] **1.3.4** Implementar montagem do prompt com contexto (função `format_docs`)
- [x] **1.3.5** Implementar chamada à LLM (Chain LangChain com Gemini 1.5 Flash)
- [x] **1.3.6** Finalizar branch (Commit 49a2fec + Merge 6164887 concluídos)

---

### 1.4 Implementação do `chat.py` (CLI de Interação)
- [x] **1.4.1** Criar branch `feature/chat-cli`
- [x] **1.4.2** Argumentos de linha de comando (`-file`)
- [x] **1.4.3** Validação de dados na base
- [x] **1.4.4** Loop de chat e tratamento de comandos (`sair`, `help`, `add`)
- [x] **1.4.5** Tratamento de erros
- [x] **1.4.6** Finalizar branch (Commit be5a938 & Merge concluídos)

---

## 🚀 Estratégia de Melhorias (46 itens do Improvements Analysis)

> **Referência**: Ver análise completa em `/brain/improvements_analysis.md`
> **Workflow**: Seguir `.agent/workflows/development-workflow.md`

### FASE A: Infraestrutura Base (Alta Prioridade)
**Branch**: `feature/infrastructure-improvements`

#### A.1 Config Centralizado (CC2)
- [x] **A.1.1** Criar arquivo `src/config.py`
  - [x] Classe `Config` com todas variáveis de ambiente
  - [x] Método `validate_config()` para validação
  - [x] Testar → Commit: `feat: add centralized config module`
- [ ] **A.1.2** Refatorar `database.py` para usar Config
  - [ ] Remover variáveis locais, importar de Config
  - [ ] Testar → Commit: `refactor: use centralized config in database`
- [ ] **A.1.3** Refatorar `ingest.py` para usar Config
  - [ ] Remover variáveis locais, importar de Config
  - [ ] Testar → Commit: `refactor: use centralized config in ingest`
- [ ] **A.1.4** Refatorar `search.py` para usar Config
  - [ ] Remover variáveis locais, importar de Config
  - [ ] Testar → Commit: `refactor: use centralized config in search`
- [ ] **A.1.5** Refatorar `chat.py` para usar Config
  - [ ] Remover variáveis locais, importar de Config
  - [ ] Testar → Commit: `refactor: use centralized config in chat`
- [ ] **TESTE COMPLETO** → Merge com main

#### A.2 Singleton de Embeddings (CC1)
- [ ] **A.2.1** Criar `src/embeddings_manager.py`
  - [ ] Função `get_embeddings()` com singleton pattern
  - [ ] Testar → Commit: `feat: add embeddings singleton manager`
- [ ] **A.2.2** Refatorar todos arquivos para usar singleton
  - [ ] Atualizar chat, ingest, search
  - [ ] Testar → Commit: `refactor: use embeddings singleton everywhere`
- [ ] **TESTE COMPLETO** → Merge com main

#### A.3 Logging Consistente (CC3)
- [ ] **A.3.1** Criar `src/logger.py` centralizado
  - [ ] Configuração única de logging
  - [ ] Testar → Commit: `feat: add centralized logger configuration`
- [ ] **A.3.2** Refatorar todos arquivos
  - [ ] Remover `logging.basicConfig()` duplicado
  - [ ] Usar `logger = logging.getLogger(__name__)`
  - [ ] Testar → Commit: `refactor: use centralized logging`
- [ ] **TESTE COMPLETO** → Merge com main

#### A.4 Validação de API Key (CC5, CHAT18)
- [ ] **A.4.1** Adicionar validação no `config.py`
  - [ ] Método `validate_config()` completo
  - [ ] Testar → Commit: `feat: add api key validation in config`
- [ ] **A.4.2** Chamar validação no início de cada script
  - [ ] chat.py, ingest.py main()
  - [ ] Testar → Commit: `feat: validate config at startup`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE B: Database Improvements (Alta/Média Prioridade)
**Branch**: `feature/database-improvements`

#### B.1 Função de Contagem Eficiente (DATABASE3, CHAT17)
- [ ] **B.1.1** Adicionar `count_documents()` em database.py
  - [ ] Query SQL direto (sem embeddings)
  - [ ] Testar → Commit: `feat: add efficient document count function`
- [ ] **B.1.2** Refatorar `check_database_status()` no chat.py
  - [ ] Usar nova função de contagem
  - [ ] Testar → Commit: `refactor: use efficient count in chat status`
- [ ] **TESTE COMPLETO** → Merge com main

#### B.2 Logging no Database (DATABASE2)
- [ ] **B.2.1** Adicionar logger em database.py
  - [ ] Logs de conexão e operações
  - [ ] Testar → Commit: `feat: add logging to database module`
- [ ] **TESTE COMPLETO** → Merge com main

#### B.3 Tratamento de Erros de Conexão (DATABASE4)
- [ ] **B.3.1** Capturar erros específicos (OperationalError, etc)
  - [ ] Try/except específicos
  - [ ] Testar → Commit: `feat: add specific error handling for database`
- [ ] **TESTE COMPLETO** → Merge com main

#### B.4 Expandir para Repositório (DATABASE1)
- [ ] **B.4.1** Criar classe `VectorStoreRepository`
  - [ ] Métodos: count, clear, exists
  - [ ] Testar → Commit: `refactor: create vector store repository class`
- [ ] **B.4.2** Migrar código existente para nova classe
  - [ ] Atualizar todos os imports
  - [ ] Testar → Commit: `refactor: migrate to repository pattern`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE C: Ingest Improvements (Alta/Média Prioridade)
**Branch**: `feature/ingest-improvements`

#### C.1 IDs Determinísticos (INGEST1)
- [ ] **C.1.1** Escolher estratégia (hash vs limpar vs metadata)
  - [ ] Implementar solução escolhida
  - [ ] Testar → Commit: `fix: improve document id generation strategy`
- [ ] **TESTE COMPLETO** → Merge com main

#### C.2 Confirmação de Sobrescrita (INGEST2, CHAT6)
- [ ] **C.2.1** Adicionar parâmetro `force` no ingest_pdf()
  - [ ] Verificar contagem antes de ingest
  - [ ] Testar → Commit: `feat: add force parameter to ingest`
- [ ] **C.2.2** Adicionar confirmação interativa
  - [ ] Perguntar ao usuário se sobrescrever
  - [ ] Testar → Commit: `feat: add overwrite confirmation`
- [ ] **C.2.3** Atualizar chat.py para usar confirmação
  - [ ] Integrar com handle_add_command
  - [ ] Testar → Commit: `feat: integrate overwrite confirmation in chat`
- [ ] **TESTE COMPLETO** → Merge com main

#### C.3 Enriquecer Metadados (INGEST6)
- [ ] **C.3.1** Adicionar metadados úteis aos chunks
  - [ ] chunk_id, total_chunks, pdf_source, etc
  - [ ] Testar → Commit: `feat: enrich document metadata`
- [ ] **TESTE COMPLETO** → Merge com main

#### C.4 Barra de Progresso (INGEST4)
- [ ] **C.4.1** Instalar tqdm e adicionar progresso
  - [ ] Barra para chunking/embedding
  - [ ] Testar → Commit: `feat: add progress bar to ingestion`
- [ ] **TESTE COMPLETO** → Merge com main

#### C.5 Estatísticas Pós-Ingestão (INGEST5)
- [ ] **C.5.1** Mostrar resumo após ingestão
  - [ ] Páginas, chunks, tamanho médio
  - [ ] Testar → Commit: `feat: show ingestion statistics`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE D: Search Improvements (Média Prioridade)
**Branch**: `feature/search-improvements`

#### D.1 Parametrizar k (SEARCH2)
- [ ] **D.1.1** Adicionar parâmetro `top_k` em search_prompt()
  - [ ] Default = Config.TOP_K
  - [ ] Testar → Commit: `feat: parametrize top k in search`
- [ ] **TESTE COMPLETO** → Merge com main

#### D.2 Temperature Configurável (SEARCH4)
- [ ] **D.2.1** Adicionar parâmetro `temperature`
  - [ ] Default = Config.RETRIEVAL_TEMPERATURE
  - [ ] Testar → Commit: `feat: make temperature configurable`
- [ ] **TESTE COMPLETO** → Merge com main

#### D.3 Remover Parâmetro question Não Usado (SEARCH6)
- [ ] **D.3.1** Limpar parâmetro question ou usar
  - [ ] Decisão: remover ou validar
  - [ ] Testar → Commit: `refactor: clean unused question parameter`
- [ ] **TESTE COMPLETO** → Merge com main

#### D.4 Retornar Fontes (SEARCH3)
- [ ] **D.4.1** Modificar para retornar dict com answer + sources
  - [ ] Criar função search_with_sources()
  - [ ] Testar → Commit: `feat: return sources with answer`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE E: Chat Improvements - Técnico (Alta Prioridade)
**Branch**: `feature/chat-technical-improvements`

#### E.1 Corrigir Argumento --file (CHAT16)
- [ ] **E.1.1** Mudar de `-file` para `-f, --file`
  - [ ] Atualizar argparse
  - [ ] Testar → Commit: `fix: correct file argument to standard format`
- [ ] **TESTE COMPLETO** → Merge com main

#### E.2 Feedback Visual (CHAT4)
- [ ] **E.2.1** Mostrar contagem exata de documentos
  - [ ] Usar count_documents() eficiente
  - [ ] Testar → Commit: `feat: show exact document count`
- [ ] **TESTE COMPLETO** → Merge com main

#### E.3 Tratamento de Banco Vazio (CHAT20)
- [ ] **E.3.1** Verificar banco antes de perguntas
  - [ ] Mensagem clara se vazio
  - [ ] Testar → Commit: `feat: handle empty database in questions`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE F: Chat Improvements - Comandos (Média Prioridade)
**Branch**: `feature/chat-commands`

#### F.1 Comando clear (CHAT9)
- [ ] **F.1.1** Implementar comando `clear`
  - [ ] Confirmação antes de limpar
  - [ ] Testar → Commit: `feat: add clear command`
- [ ] **TESTE COMPLETO** → Merge com main

#### F.2 Comando stats (CHAT15)
- [ ] **F.2.1** Implementar comando `stats`
  - [ ] Mostrar estatísticas do banco
  - [ ] Testar → Commit: `feat: add stats command`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE G: Chat Improvements - UX (Média Prioridade)
**Branch**: `feature/chat-ux-improvements`

#### G.1 Simplificar Prompt (CHAT8)
- [ ] **G.1.1** Prompt simplificado após primeira vez
  - [ ] Apenas `>` depois da primeira pergunta
  - [ ] Testar → Commit: `feat: simplify prompt after first question`
- [ ] **TESTE COMPLETO** → Merge com main

#### G.2 Indicador de Progresso (CHAT7)
- [ ] **G.2.1** Mostrar etapas durante busca
  - [ ] "Recuperando...", "Gerando resposta..."
  - [ ] Testar → Commit: `feat: add progress indicator to search`
- [ ] **TESTE COMPLETO** → Merge com main

#### G.3 Atalhos (CHAT10)
- [ ] **G.3.1** Adicionar aliases para comandos
  - [ ] h→help, a→add, c→clear, etc
  - [ ] Testar → Commit: `feat: add command shortcuts`
- [ ] **TESTE COMPLETO** → Merge com main

#### G.4 Modo Silencioso (CHAT13)
- [ ] **G.4.1** Flag --quiet
  - [ ] Esconder logs de inicialização
  - [ ] Testar → Commit: `feat: add quiet mode flag`
- [ ] **TESTE COMPLETO** → Merge com main

#### G.5 Estatísticas de Resposta (CHAT14)
- [ ] **G.5.1** Mostrar tempo e chunks usados
  - [ ] Flag --verbose
  - [ ] Testar → Commit: `feat: add response statistics`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE H: Parâmetros Configuráveis (CC4)
**Branch**: `feature/configurable-parameters`

#### H.1 CLI Arguments Override
- [ ] **H.1.1** Adicionar args para chunk_size, overlap, top_k
  - [ ] Atualizar ingest.py e search.py
  - [ ] Testar → Commit: `feat: add cli arguments for parameters`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE I: Tratamento de Erros (CC6)
**Branch**: `feature/error-handling`

#### I.1 Erros Específicos
- [ ] **I.1.1** Substituir `except Exception` por erros específicos
  - [ ] FileNotFoundError, PermissionError, etc
  - [ ] Testar cada arquivo → Commits individuais
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE J: Code Quality (Baixa Prioridade)
**Branch**: `feature/code-quality`

#### J.1 Type Hints (CC7)
- [ ] **J.1.1** Adicionar type hints completos
  - [ ] Todos os arquivos
  - [ ] Testar → Commit: `refactor: add complete type hints`
- [ ] **TESTE COMPLETO** → Merge com main

#### J.2 Docstrings (CC8)
- [ ] **J.2.1** Completar docstrings
  - [ ] Raises, Examples, etc
  - [ ] Testar → Commit: `docs: complete docstrings`
- [ ] **TESTE COMPLETO** → Merge com main

#### J.3 Magic Numbers (CC9)
- [ ] **J.3.1** Eliminar magic numbers
  - [ ] Definir constantes
  - [ ] Testar → Commit: `refactor: replace magic numbers with constants`
- [ ] **TESTE COMPLETO** → Merge com main

---

### FASE K: Refatorações Avançadas (Baixa Prioridade)
**Branch**: `feature/advanced-refactoring`

#### K.1 Separar Módulos CLI (CHAT1)
- [ ] **K.1.1** Criar estrutura cli/
  - [ ] commands.py, ui.py, validators.py
  - [ ] Testar → Commit: `refactor: separate cli into modules`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.2 Histórico de Conversas (CHAT5)
- [ ] **K.2.1** Implementar histórico
  - [ ] Comando history, !N para repetir
  - [ ] Testar → Commit: `feat: add conversation history`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.3 Exemplos Contextuais (CHAT12)
- [ ] **K.3.1** Help com sugestões do PDF
  - [ ] Analisar metadados
  - [ ] Testar → Commit: `feat: add contextual help suggestions`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.4 Timeout de Busca (CHAT11)
- [ ] **K.4.1** Implementar timeout
  - [ ] signal + contextmanager
  - [ ] Testar → Commit: `feat: add search timeout`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.5 Recarregar Chain (CHAT19)
- [ ] **K.5.1** Recriar chain após add
  - [ ] Atualizar chat_loop
  - [ ] Testar → Commit: `feat: reload chain after ingestion`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.6 Templates Customizáveis (SEARCH1)
- [ ] **K.6.1** Suporte a templates externos
  - [ ] load_prompt_template()
  - [ ] Testar → Commit: `feat: support custom prompt templates`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.7 Cache de Embeddings (SEARCH5)
- [ ] **K.7.1** LRU cache para perguntas repetidas
  - [ ] @lru_cache
  - [ ] Testar → Commit: `feat: add embeddings cache`
- [ ] **TESTE COMPLETO** → Merge com main

#### K.8 Fallback LLM (SEARCH7)
- [ ] **K.8.1** Retornar docs se LLM falhar
  - [ ] Try/except com fallback
  - [ ] Testar → Commit: `feat: add llm fallback`
- [ ] **TESTE COMPLETO** → Merge com main

---

### 1.5 Testes e Validação
- [ ] **1.5.1** Testar fluxo completo
- [ ] **1.5.2** Atualizar README.md

---

## Fase 2: CLI Profissional
*(Refatoração usando bibliotecas como Click ou Typer)*

## Fase 3: UI/Layout do Terminal
*(Melhorias visuais com Rich)*

## Fase 4: Sistema de Load do PDF no CLI
*(Gestão avançada de múltiplos PDFs)*
