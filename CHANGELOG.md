# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Singleton de Embeddings com abstração de provedor (Google/OpenAI) no módulo `src/embeddings_manager.py` (`946fbb1`)
- Singleton de LLM com abstração de provedor (Google/OpenAI) no módulo `src/llm_manager.py` (`7025f72`)
- Logger centralizado no módulo `src/logger.py` para configuração consistente de logging (`e663baa`)

### Alterado
- Refatorado `ingest.py`, `search.py` e `chat.py` para utilizar os novos managers de Embeddings e LLM (`7c2a172`)
- Atualizado workflow de desenvolvimento para incluir testes automáticos de subtasks (`e663baa`)
- Refatorados todos os módulos (`ingest.py`, `search.py`, `chat.py`, `embeddings_manager.py`, `llm_manager.py`) para usar logger centralizado (`7af7e47`)

---

## [0.1.0] - 2026-01-23

### Adicionado

#### Infraestrutura Base
- **Configuração Centralizada** (`src/config.py`)
  - Classe `Config` com todas as variáveis de ambiente
  - Validação automática de configurações
  - Suporte agnóstico a provedores (Google Gemini e OpenAI)
  - Propriedades dinâmicas: `API_KEY`, `EMBEDDING_MODEL`, `LLM_MODEL`
  - Detecção automática do provedor baseado em chaves configuradas

#### Funcionalidades Core
- **Ingestão de PDFs** (`src/ingest.py`)
  - Carregamento de PDFs com `PyPDFLoader`
  - Chunking com `RecursiveCharacterTextSplitter` (1000 chars, overlap 150)
  - Geração de embeddings usando Google Gemini
  - Armazenamento em PGVector com IDs determinísticos
  - Logs detalhados de progresso
  - Controle de documentos existentes

- **Busca Semântica** (`src/search.py`)
  - Busca por similaridade vetorial (k=10)
  - Integração com LLM (Google Gemini 1.5 Flash)
  - Formatação de contexto a partir dos chunks recuperados
  - Prompt template rigoroso para evitar alucinações
  - Chain LangChain para geração de respostas

- **Interface CLI** (`src/chat.py`)
  - Chat interativo via linha de comando
  - Validação de status do banco de dados
  - Comandos especiais:
    - `help`: Exibe ajuda
    - `add <pdf>` / `ingest <pdf>`: Ingere novo PDF
    - `sair` / `exit` / `quit` / `q`: Encerra o chat
  - Argumento `-file` para ingestão inicial
  - Tratamento de erros robusto
  - Feedback visual de progresso

- **Módulo de Database** (`src/database.py`)
  - Função centralizada `get_vector_store()`
  - Conexão com PGVector
  - Reutilização de configurações

#### Documentação
- README.md com instruções completas de instalação e uso
  - Índice navegável com links
  - Seção detalhada sobre tecnologias utilizadas
  - Guia passo a passo de instalação
  - Explicação completa de todas as variáveis de ambiente
  - Instruções de uso do Docker Compose
  - Fluxo completo de uso com exemplos práticos
  - Estrutura do projeto documentada
  - Diagramas de como o sistema funciona
  - Tabela de comandos disponíveis
  - Seção de troubleshooting com soluções comuns
  - Seção sobre desenvolvimento com Antigravity
- CHANGELOG.md seguindo padrão Keep a Changelog
  - Versionamento semântico
  - Histórico completo de mudanças
  - Categorização clara (Adicionado, Alterado, Técnico)
- `.env.example` com template de configuração atualizado
- Workflow de desenvolvimento atualizado
  - Instruções para manutenção do CHANGELOG
  - Instruções para manutenção do README
  - Exemplos práticos de quando e como atualizar documentação

#### Infraestrutura
- Docker Compose para PostgreSQL + pgVector
- Health checks automáticos
- Inicialização automática da extensão vector
- Volume persistente para dados
- Arquivo `.gitignore` configurado

### Alterado
- Refatorado `database.py` para usar `Config` centralizado
- Refatorado `ingest.py` para usar `Config` centralizado
- Refatorado `search.py` para usar `Config` centralizado
- Refatorado `chat.py` para usar `Config` centralizado
- Atualizado `.env.example` com variáveis OpenAI

### Técnico

#### Commits Principais
- `c3805ea` - feat: add centralized config module
- `d3c330e` - refactor: use centralized config in database
- `94e3e5e` - refactor: use centralized config in ingest
- `d17fe1e` - refactor: use centralized config in search
- `b860530` - feat: add provider-agnostic config properties
- `00cee35` - refactor: use centralized config in chat
- `be5a938` - feat: implement interactive chat CLI
- `49a2fec` - feat: implement semantic search with LLM integration using Gemini
- `7fd8729` - feat: implement PDF ingestion with PGVector and create database module

#### Branches Mergeadas
- `feature/config-module` - Módulo de configuração centralizado
- `feature/config-database` - Integração config com database
- `feature/config-ingest` - Integração config com ingest
- `feature/config-search` - Integração config com search
- `feature/config-provider-agnostic` - Suporte multi-provedor
- `feature/config-chat` - Integração config com chat
- `feature/chat-cli` - Interface CLI interativa
- `feature/search-implementation` - Busca semântica
- `feature/ingest-implementation` - Ingestão de PDFs

---

## [0.0.1] - 2026-01-21

### Adicionado
- Setup inicial do projeto
- Estrutura de diretórios
- Arquivo `requirements.txt` com dependências
- Configuração do `.gitignore`
- Documentação de requisitos (`requisitos.md`)

---

## Tipos de Mudanças

- **Adicionado**: para novas funcionalidades
- **Alterado**: para mudanças em funcionalidades existentes
- **Descontinuado**: para funcionalidades que serão removidas
- **Removido**: para funcionalidades removidas
- **Corrigido**: para correções de bugs
- **Segurança**: para vulnerabilidades corrigidas
- **Técnico**: para detalhes de implementação (commits, branches, etc)

---

## Versionamento

Este projeto usa [Versionamento Semântico](https://semver.org/lang/pt-BR/):

- **MAJOR** (X.0.0): Mudanças incompatíveis com versões anteriores
- **MINOR** (0.X.0): Novas funcionalidades compatíveis com versões anteriores
- **PATCH** (0.0.X): Correções de bugs compatíveis com versões anteriores

Durante o desenvolvimento inicial (0.x.x), a API pode mudar a qualquer momento.
