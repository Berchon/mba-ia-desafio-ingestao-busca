# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Documentação técnica completa: `ANALISE_REQUISITOS.md`, `FUNCTIONAL_SPECIFICATION_AS_IS.md`, e `PRD.md` na pasta `docs/` (`1205463`)

### Alterado
- Type hints completos em todos os módulos de `src/` para melhorar legibilidade e manutenção (`85321ff`)
- Docstrings completas (Args/Returns/Raises/Examples) nos principais módulos e funções (`882b63e`)

### Corrigido
- Adicionado import faltante de `SQLAlchemyError` em `search.py` e `chat.py` para tratamento correto de exceções de banco de dados (`f9edd2b`)
- Corrigido modelo padrão OpenAI LLM de `gpt-4o-mini` para `gpt-5-nano` conforme requisitos (`f9edd2b`)
- Corrigido modelo padrão Google Embedding em `.env.example` para `models/embedding-001` conforme requisitos (`f9edd2b`)

---

## [0.4.0] - 2026-01-24

### Adicionado
- Melhorias no tratamento de erros (`feature/error-handling`): substituição de exceções genéricas por `SQLAlchemyError`, `IOError`, etc em `database.py`, `chat.py` e `search.py` (`d6b9534`)
- Parâmetros configuráveis via CLI (`--chunk-size`, `--chunk-overlap`, `--top-k`, `--temperature`) em `chat.py` e `ingest.py` (`e8df239`)
- Estatísticas de resposta no Chat CLI (tempo de execução e fontes) ativadas via flag `-v, --verbose` (`986c201`)
- Modo silencioso (`-q, --quiet`) em todos os comandos (`chat.py` e `ingest.py`) para suprimir logs e feedback visual (`65b9f96`)
- Atalhos de comandos no Chat CLI (`h`, `a`, `c`, `s`, `r`) para maior agilidade (`12b4a89`)
- Indicadores de progresso visual durante a busca ("Recuperando...", "Gerando...") no Chat CLI (`a1a8c23`)
- Prompt simplificado (`>`) no Chat CLI após a primeira instrução para uma interface mais limpa (`e540e31`)
- Novo comando `remove` no Chat CLI para remover arquivos específicos da base com confirmação (`6279bf9`)
- Novo comando `stats` no Chat CLI para exibir estatísticas detalhadas do banco de dados (`b84c137`)
- Novo comando `clear` no Chat CLI com confirmação de segurança e verificação de banco vazio (`a395130`)
- Novo método `count_sources` no `VectorStoreRepository` para contagem de arquivos únicos (`276e684`)
- Feedback visual no Chat CLI mostrando contagem de trechos e arquivos (`276e684`)
- Tratamento de banco de dados vazio no chat, impedindo perguntas sem documentos e orientando o usuário (`9eab3cc`)

### Corrigido
- Padronização do argumento de arquivo no chat de `-file` para `-f, --file` para seguir convenções de CLI (`75dbaaa`)
- Erro `sys.excepthook` ao encerrar o chat, implementando um encerramento mais robusto com `os._exit` (`1bbde33`)

---

## [0.3.0] - 2026-01-24

### Adicionado
- Sistema de confirmação antes de sobrescrever documentos já existentes na base durante a ingestão (`src/chat.py`, `src/ingest.py`) (`ff16bb4`)
- Nova função `search_with_sources` que retorna um dicionário com a resposta e metadados das fontes utilizadas (`src/search.py`) (`7e3f01f`)
- Temperatura configurável para geração da LLM com reset dinâmico de singleton (`src/llm_manager.py`, `src/search.py`) (`86fa760`)
- Parametrização do número de resultados recuperados (`top_k`) na chain de busca (`src/search.py`) (`ef56f88`)
- Contador de documentos eficiente no banco de dados vetorial usando SQL direto (`src/database.py`) (`36dc8e3`)
- Exibição do número real de documentos na tela de boas-vindas do chat (`src/chat.py`) (`36dc8e3`)
- Sistema de logs detalhados para operações no banco de dados (`src/database.py`) (`d4a9790`)
- Tratamento de erros específicos de conexão (OperationalError) e tabelas ausentes (ProgrammingError) (`src/database.py`) (`5be4ed1`)
- Implementação do padrão Repository com a classe `VectorStoreRepository` (`src/database.py`) (`cbc68f9`)
- Novo comando `clear` no Chat CLI para limpeza total da base de dados (`src/chat.py`) (`cbc68f9`)
- Implementação de IDs determinísticos baseados no nome do arquivo (Cenário A) (`src/ingest.py`) (`af396e7`)
- Sistema de limpeza seletiva por fonte no `VectorStoreRepository` (`src/database.py`) (`03c1a95`)
- Integração da limpeza automática no fluxo de ingestão de PDFs (`src/ingest.py`) (`e0c0d89`)
- Barra de progresso visual usando `tqdm` durante a geração de embeddings (`src/ingest.py`) (`09e81b7`)
- Exibição de estatísticas detalhadas pós-ingestão, incluindo total de páginas, chunks e tamanho médio (`src/ingest.py`) (`09e81b7`)
- Sistema de enriquecimento de metadados durante a ingestão com `chunk_id`, `chunk_index`, `total_chunks` e `filename` (`src/ingest.py`) (`daa0944`)

### Alterado
- Removido parâmetro `question` não utilizado na função `search_prompt` para melhor clareza do código (`src/search.py`) (`8577128`)

### Corrigido
- Bug na query de contagem de documentos que sempre retornava 0 devido a filtragem incorreta de metadados (`src/database.py`) (`36dc8e3`)
- Remoção de variável não utilizada `table_name` em `src/database.py` (`36dc8e3`)

---

## [0.2.0] - 2026-01-23

### Adicionado
- Singleton de Embeddings com abstração de provedor (Google/OpenAI) no módulo `src/embeddings_manager.py` (`946fbb1`)
- Singleton de LLM com abstração de provedor (Google/OpenAI) no módulo `src/llm_manager.py` (`7025f72`)
- Logger centralizado no módulo `src/logger.py` para configuração consistente de logging (`e663baa`)

### Alterado
- Refatorado `ingest.py`, `search.py` e `chat.py` para utilizar os novos managers de Embeddings e LLM (`7c2a172`)
- Atualizado workflow de desenvolvimento para incluir testes automáticos de subtasks (`e663baa`)
- Refatorados todos os módulos (`ingest.py`, `search.py`, `chat.py`, `embeddings_manager.py`, `llm_manager.py`) para usar logger centralizado (`7af7e47`)
- README.md atualizado com novas características e estrutura do projeto (`3b906c4`)

### Melhorias de Infraestrutura
- Arquitetura com padrão Singleton para Embeddings e LLM
- Sistema de logging centralizado e consistente
- Abstração completa de provedor (Google/OpenAI)
- Validação de configuração já implementada desde v0.1.0

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
