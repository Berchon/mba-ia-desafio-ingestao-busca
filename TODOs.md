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
- [x] **A.1.2** Refatorar `database.py` para usar Config
  - [x] Remover variáveis locais, importar de Config
  - [x] Testar → Commit: `refactor: use centralized config in database`
- [x] **A.1.3** Refatorar `ingest.py` para usar Config
  - [x] Remover variáveis locais, importar de Config
  - [x] Testar → Commit: `refactor: use centralized config in ingest`
- [x] **A.1.4** Refatorar `search.py` para usar Config
  - [x] Remover variáveis locais, importar de Config
  - [x] Testar → Commit: `refactor: use centralized config in search`
- [x] **A.1.5** Tornar Config agnóstico ao provedor (Google/OpenAI)
  - [x] Adicionar `OPENAI_LLM_MODEL` no .env.example
  - [x] Criar propriedades `API_KEY`, `EMBEDDING_MODEL`, `LLM_MODEL` que retornam valores baseados no provedor disponível
  - [x] Testar → Commit: `feat: add provider-agnostic config properties`
- [x] **A.1.6** Refatorar `chat.py` para usar Config
  - [x] Remover variáveis locais, importar de Config
  - [x] Testar → Commit: `refactor: use centralized config in chat`
- [x] **TESTE COMPLETO** → Merge com main

#### A.1.7 Adicionar Badge de Release no README
**Branch**: `docs/add-release-badge`
- [x] **A.1.7.1** Adicionar badge de release no topo do README.md
  - [x] Badge de versão: `![GitHub release](https://img.shields.io/github/v/release/usuario/repo)`
  - [x] Posicionar logo após o título principal
  - [x] Testar → Commit: `docs: add release version badge to README`
- [x] **TESTE COMPLETO** → Merge com main

#### A.2 Singleton de Embeddings e Abstração de Provedor (CC1)
- [x] **A.2.1** Criar `src/embeddings_manager.py`
  - [x] Função `get_embeddings()` com singleton pattern
  - [x] Detecção automática de provedor (Google/OpenAI)
  - [x] Import dinâmico das classes corretas (GoogleGenerativeAIEmbeddings ou OpenAIEmbeddings)
  - [x] Testar → Commit: `feat: add embeddings singleton with provider abstraction`
- [x] **A.2.2** Criar `src/llm_manager.py`
  - [x] Função `get_llm()` com singleton pattern
  - [x] Detecção automática de provedor (Google/OpenAI)
  - [x] Import dinâmico das classes corretas (ChatGoogleGenerativeAI ou ChatOpenAI)
  - [x] Testar → Commit: `feat: add llm singleton with provider abstraction`
- [x] **A.2.3** Refatorar todos arquivos para usar managers
  - [x] Atualizar chat.py, ingest.py, search.py
  - [x] Remover imports diretos de langchain_google_genai
  - [x] Testar → Commit: `refactor: use embeddings and llm managers everywhere`
- [x] **TESTE COMPLETO** → Merge com main

#### A.3 Logging Consistente (CC3)
- [x] **A.3.1** Criar `src/logger.py` centralizado
  - [x] Configuração única de logging
  - [x] Testar → Commit: `feat: add centralized logger configuration`
- [x] **A.3.2** Refatorar todos arquivos
  - [x] Remover `logging.basicConfig()` duplicado
  - [x] Usar `logger = logging.getLogger(__name__)`
  - [x] Testar → Commit: `refactor: use centralized logging`
- [x] **TESTE COMPLETO** → Merge com main

#### A.4 Validação de API Key (CC5, CHAT18)
- [x] **A.4.1** Adicionar validação no `config.py`
  - [x] Método `validate_config()` completo
  - [x] Testar → Commit: `feat: add api key validation in config`
- [x] **A.4.2** Chamar validação no início de cada script
  - [x] chat.py, ingest.py main()
  - [x] Testar → Commit: `feat: validate config at startup`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE B: Database Improvements (Alta/Média Prioridade)
**Branch**: `feature/database-improvements`

#### B.1 Função de Contagem Eficiente (DATABASE3, CHAT17)
- [x] **B.1.1** Adicionar `count_documents()` em database.py
  - [x] Query SQL direto (sem embeddings)
  - [x] Testar → Commit: `feat: add efficient document count function`
- [x] **B.1.2** Refatorar `check_database_status()` no chat.py
  - [x] Usar nova função de contagem
  - [x] Testar → Commit: `refactor: use efficient count in chat status`
- [x] **TESTE COMPLETO** → Merge com main

#### B.2 Logging no Database (DATABASE2)
- [x] **B.2.1** Adicionar logger em database.py
  - [x] Logs de conexão e operações
  - [x] Testar → Commit: `feat: add logging to database module`
- [x] **TESTE COMPLETO** → Merge com main

#### B.3 Tratamento de Erros de Conexão (DATABASE4)
- [x] **B.3.1** Capturar erros específicos (OperationalError, etc)
  - [x] Try/except específicos
  - [x] Testar → Commit: `feat: add specific error handling for database`
- [x] **TESTE COMPLETO** → Merge com main

#### B.4 Expandir para Repositório (DATABASE1)
- [x] **B.4.1** Criar classe `VectorStoreRepository`
  - [x] Métodos: count, clear, exists
  - [x] Testar → Commit: `refactor: create vector store repository class`
- [x] **B.4.2** Migrar código existente para nova classe
  - [x] Atualizar todos os imports
  - [x] Testar → Commit: `refactor: migrate to repository pattern`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE C: Ingest Improvements (Alta/Média Prioridade)
**Branch**: `feature/ingest-improvements`

#### C.1 IDs Determinísticos (INGEST1)
- [x] **C.1.1** Implementar Cenário A (Nome do Arquivo + Índice)
  - [x] Garantir que IDs sejam únicos por arquivo (ex: doc.pdf-0, doc.pdf-1)
  - [x] Testar → Commit: `feat: implement file-based deterministic IDs`
- [x] **TESTE COMPLETO** → Merge com main

#### C.2 Limpeza Automática por Source (INGEST2, CHAT6)
- [x] **C.2.1** Implementar `delete_by_source()` no `VectorStoreRepository`
  - [x] Lógica para apagar todos os chunks que tenham o mesmo `metadata['source']`
  - [x] Testar → Commit: `feat: add delete by source to repository`
- [x] **C.2.2** Integrar limpeza no fluxo de `ingest_pdf()`
  - [x] Limpar dados antigos do arquivo antes de realizar a nova ingestão
  - [x] Testar → Commit: `feat: auto-clean old file data before ingestion`
- [x] **TESTE COMPLETO** → Merge com main

#### C.3 Enriquecer Metadados (INGEST6)
- [x] **C.3.1** Adicionar metadados úteis aos chunks
  - [x] chunk_id, total_chunks, pdf_source, etc
  - [x] Testar → Commit: `feat: enrich document metadata`
- [x] **TESTE COMPLETO** → Merge com main

#### C.4 Barra de Progresso (INGEST4)
- [x] **C.4.1** Instalar tqdm e adicionar progresso
  - [x] Barra para chunking/embedding
  - [x] Testar → Commit: `feat: add progress bar to ingestion`
- [x] **TESTE COMPLETO** → Merge com main

#### C.5 Estatísticas Pós-Ingestão (INGEST5)
- [x] **C.5.1** Mostrar resumo após ingestão
  - [x] Páginas, chunks, tamanho médio
  - [x] Testar → Commit: `feat: show ingestion statistics`
- [x] **TESTE COMPLETO** → Merge com main

#### C.6 Confirmação de Sobrescrita (Novo)
- [x] **C.6.1** Verificar se 'source' já existe no repositório
- [x] **C.6.2** Solicitar confirmação (Y/n) antes de limpar e re-ingerir
- [x] Testar → Commit: `feat: add overwrite confirmation for existing documents`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE D: Search Improvements (Média Prioridade)
**Branch**: `feature/search-improvements`

#### D.1 Parametrizar k (SEARCH2)
- [x] **D.1.1** Adicionar parâmetro `top_k` em search_prompt()
  - [x] Default = Config.TOP_K
  - [x] Testar → Commit: `feat: parametrize top k in search`
- [x] **TESTE COMPLETO** → Merge com main

#### D.2 Temperature Configurável (SEARCH4)
- [x] **D.2.1** Adicionar parâmetro `temperature`
  - [x] Default = Config.RETRIEVAL_TEMPERATURE
  - [x] Testar → Commit: `feat: make temperature configurable`
- [x] **TESTE COMPLETO** → Merge com main

#### D.3 Remover Parâmetro question Não Usado (SEARCH6)
- [x] **D.3.1** Limpar parâmetro question ou usar
  - [x] Decisão: remover ou validar
  - [x] Testar → Commit: `refactor: clean unused question parameter`
- [x] **TESTE COMPLETO** → Merge com main

#### D.4 Retornar Fontes (SEARCH3)
- [x] **D.4.1** Modificar para retornar dict com answer + sources
  - [x] Criar função search_with_sources()
  - [x] Testar → Commit: `feat: return sources with answer`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE E: Chat Improvements - Técnico (Alta Prioridade)
**Branch**: `feature/chat-technical-improvements`

#### E.1 Corrigir Argumento --file (CHAT16)
- [x] **E.1.1** Mudar de `-file` para `-f, --file`
  - [x] Atualizar argparse
  - [x] Testar → Commit: `fix: correct file argument to standard format`
- [x] **TESTE COMPLETO** → Merge com main

#### E.2 Feedback Visual (CHAT4)
- [x] **E.2.1** Mostrar contagem exata de documentos
  - [x] Usar count_documents() eficiente
  - [x] Testar → Commit: `feat: show exact document count`
- [x] **TESTE COMPLETO** → Merge com main

#### E.3 Tratamento de Banco Vazio (CHAT20)
- [x] **E.3.1** Verificar banco antes de perguntas
  - [x] Mensagem clara se vazio
  - [x] Testar → Commit: `feat: handle empty database in questions`
- [x] **TESTE COMPLETO** → Merge com main

#### E.4 Corrigir Warning de Shutdown (CHAT21)
- [x] **E.4.1** Adicionar cleanup adequado ao sair
  - [x] Implementar graceful shutdown para objetos assíncronos
  - [x] Fechar conexões do LangChain/httpx adequadamente
  - [x] Testar → Commit: `fix: add graceful shutdown to prevent sys.excepthook error`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE F: Chat Improvements - Comandos (Média Prioridade)
**Branch**: `feature/chat-commands`

#### F.1 Comando clear (CHAT9)
- [x] **F.1.1** Implementar comando `clear`
  - [x] Confirmação antes de limpar
  - [x] Testar → Commit: `feat: add clear command`

#### F.2 Comando stats (CHAT15)
- [x] **F.2.1** Implementar comando `stats`
  - [x] Mostrar estatísticas do banco
  - [x] Testar → Commit: `feat: add stats command`

#### F.3 Comando remove <arquivo> (Novo)
- [x] **F.3.1** Implementar comando `remove <nome_arquivo>` ou `delete <nome_arquivo>`
  - [x] Permitir remover dados de apenas um documento específico
  - [x] Testar → Commit: `feat: add remove by file command to chat`
- [x] **TESTE COMPLETO** → Merge com main

---

### FASE G: Chat Improvements - UX (Média Prioridade)
**Branch**: `feature/chat-ux-improvements`

#### G.1 Simplificar Prompt (CHAT8)
- [x] **G.1.1** Prompt simplificado após primeira vez
  - [x] Apenas `>` depois da primeira pergunta
  - [x] Testar → Commit: `feat: simplify prompt after first question`

#### G.2 Indicador de Progresso (CHAT7)
- [x] **G.2.1** Mostrar etapas durante busca
  - [x] "Recuperando...", "Gerando resposta..."
  - [x] Testar → Commit: `feat: add progress indicator to search`
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
