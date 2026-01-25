# Functional Specification (As-Is)
## Sistema RAG - Ingestão e Busca Semântica com LangChain

**Versão do Documento:** 1.0  
**Data:** 2026-01-24  
**Baseado em:** Análise do código-fonte (versão 0.4.0)

---

## 1. Visão Geral do Sistema

### 1.1 O que o Sistema Faz

O sistema é uma aplicação RAG (Retrieval-Augmented Generation) que permite:

1. **Ingestão de PDFs**: Carrega documentos PDF, divide em fragmentos (chunks), gera embeddings vetoriais e armazena no PostgreSQL com extensão pgVector.
2. **Busca Semântica**: Permite fazer perguntas em linguagem natural sobre o conteúdo dos PDFs ingeridos, utilizando busca por similaridade vetorial e geração de respostas via LLM.
3. **Interface CLI Interativa**: Fornece uma interface de linha de comando para interagir com o sistema, fazer perguntas, gerenciar documentos e visualizar estatísticas.

### 1.2 Para Quem é

- Usuários que precisam fazer perguntas sobre documentos PDF específicos
- Desenvolvedores que precisam integrar busca semântica em documentos
- Usuários técnicos que operam via linha de comando

### 1.3 O que o Sistema NÃO Faz

- **Não suporta múltiplos formatos de documento** (apenas PDF)
- **Não possui interface web ou gráfica** (apenas CLI)
- **Não mantém histórico de conversas** entre sessões
- **Não permite edição de documentos** já ingeridos (apenas remoção e re-ingestão)
- **Não possui autenticação ou controle de acesso**
- **Não suporta busca por múltiplos PDFs simultaneamente** em uma única pergunta (todos os PDFs são tratados como um corpus único)
- **Não possui cache de embeddings** para perguntas repetidas
- **Não possui timeout configurável** para operações de busca
- **Não permite templates de prompt customizáveis** (template é fixo no código)

---

## 2. Arquitetura Funcional

### 2.1 Componentes Principais

O sistema é composto pelos seguintes módulos Python:

#### 2.1.1 `config.py` - Configuração Centralizada
- **Responsabilidade**: Centraliza todas as variáveis de ambiente e configurações
- **Funcionalidades**:
  - Carrega variáveis do arquivo `.env` via `python-dotenv`
  - Fornece classe `Config` com propriedades estáticas
  - Validação de configurações críticas via `validate_config()`
  - Propriedades agnósticas ao provedor (`API_KEY`, `EMBEDDING_MODEL`, `LLM_MODEL`)
  - Detecção automática de provedor (Google tem prioridade sobre OpenAI)

#### 2.1.2 `logger.py` - Sistema de Logging
- **Responsabilidade**: Configuração centralizada de logging
- **Funcionalidades**:
  - Função `get_logger()` para criar loggers consistentes
  - Formatação padrão: `%(levelname)s: %(message)s`
  - Função `set_global_log_level()` para modo silencioso
  - Evita duplicação de handlers

#### 2.1.3 `embeddings_manager.py` - Gerenciador de Embeddings
- **Responsabilidade**: Singleton para modelo de embeddings
- **Funcionalidades**:
  - Padrão Singleton para garantir uma única instância
  - Detecção automática de provedor (Google ou OpenAI)
  - Import dinâmico das classes corretas
  - Prioriza Google se ambas as chaves estiverem configuradas

#### 2.1.4 `llm_manager.py` - Gerenciador de LLM
- **Responsabilidade**: Singleton para modelo de linguagem
- **Funcionalidades**:
  - Padrão Singleton para garantir uma única instância
  - Suporte a temperatura configurável
  - Reset dinâmico do singleton quando temperatura muda
  - Detecção automática de provedor (Google ou OpenAI)

#### 2.1.5 `database.py` - Repositório de Banco de Dados
- **Responsabilidade**: Abstração de acesso ao PGVector
- **Funcionalidades**:
  - Classe `VectorStoreRepository` (padrão Repository)
  - Operações: `count()`, `count_sources()`, `list_sources()`, `exists()`, `clear()`, `delete_by_source()`, `source_exists()`
  - Queries SQL diretas para operações eficientes
  - Tratamento de erros específicos (OperationalError, ProgrammingError)
  - Função legacy `get_vector_store()` para compatibilidade

#### 2.1.6 `ingest.py` - Módulo de Ingestão
- **Responsabilidade**: Processamento e armazenamento de PDFs
- **Funcionalidades**:
  - Carregamento de PDFs via `PyPDFLoader`
  - Chunking com `RecursiveCharacterTextSplitter` (tamanho e overlap configuráveis)
  - Enriquecimento de metadados (chunk_id, chunk_index, total_chunks, filename)
  - Limpeza automática de dados antigos antes de re-ingerir
  - Barra de progresso visual (tqdm)
  - Processamento em lotes (batch_size=16)
  - Estatísticas pós-ingestão
  - Modo silencioso (`--quiet`)
  - Confirmação de sobrescrita (quando não em modo quiet)

#### 2.1.7 `search.py` - Módulo de Busca
- **Responsabilidade**: Busca semântica e geração de respostas
- **Funcionalidades**:
  - Função `search_prompt()`: Cria chain LangChain completa
  - Função `search_with_sources()`: Retorna resposta + metadados das fontes
  - Template de prompt fixo (conforme requisitos.md)
  - Parâmetros configuráveis: `top_k`, `temperature`
  - Formatação de contexto via concatenação de chunks
  - Extração de fontes únicas (arquivo + página)

#### 2.1.8 `chat.py` - Interface CLI
- **Responsabilidade**: Interface interativa com o usuário
- **Funcionalidades**:
  - Loop de chat interativo
  - Comandos especiais (help, add, remove, clear, stats, sair)
  - Atalhos de comandos (h, a, r, c, s, q)
  - Validação de banco vazio antes de perguntas
  - Modos de operação: `--quiet`, `--verbose`
  - Argumentos CLI: `--file`, `--top-k`, `--temperature`, `--chunk-size`, `--chunk-overlap`
  - Ingestão inicial via argumento `-f/--file`
  - Tratamento de erros específicos
  - Encerramento robusto (os._exit para evitar sys.excepthook)

### 2.2 Dependências Externas

#### 2.2.1 Serviços Externos
- **Google Gemini API** (opcional): Para embeddings e LLM
- **OpenAI API** (opcional): Para embeddings e LLM (alternativa ao Google)
- **PostgreSQL + pgVector**: Banco de dados vetorial (via Docker Compose)

#### 2.2.2 Bibliotecas Python Principais
- `langchain`: Framework principal
- `langchain-community`: Loaders de documentos
- `langchain-postgres`: Integração com PGVector
- `langchain-google-genai`: Integração Google Gemini
- `langchain-openai`: Integração OpenAI
- `pypdf`: Leitura de PDFs
- `tqdm`: Barras de progresso
- `python-dotenv`: Gerenciamento de variáveis de ambiente
- `sqlalchemy`: ORM e queries SQL
- `psycopg`: Driver PostgreSQL

---

## 3. Funcionalidades por Módulo

### 3.1 Ingestão de PDFs (`ingest.py`)

#### 3.1.1 Função Principal: `ingest_pdf()`

**Descrição**: Processa um arquivo PDF e armazena seus chunks vetorizados no banco de dados.

**Parâmetros**:
- `pdf_path` (str, opcional): Caminho do PDF. Se None, usa `Config.PDF_PATH`
- `quiet` (bool, default=False): Se True, oculta logs e barras de progresso
- `chunk_size` (int, opcional): Tamanho do chunk em caracteres. Se None, usa `Config.CHUNK_SIZE` (padrão: 1000)
- `chunk_overlap` (int, opcional): Sobreposição entre chunks. Se None, usa `Config.CHUNK_OVERLAP` (padrão: 150)

**Fluxo de Execução**:
1. Valida configuração via `Config.validate_config()`
2. Ajusta nível de log se `quiet=True`
3. Resolve caminho do PDF (parâmetro ou `Config.PDF_PATH`)
4. Valida existência do arquivo (lança `FileNotFoundError` se não existir)
5. Carrega PDF via `PyPDFLoader`
6. Divide texto em chunks via `RecursiveCharacterTextSplitter`
7. Valida que chunks foram gerados (lança `ValueError` se vazio)
8. Enriquece metadados de cada chunk:
   - `chunk_id`: `{filename}-{index}`
   - `chunk_index`: índice do chunk (0-based)
   - `total_chunks`: total de chunks do arquivo
   - `filename`: nome do arquivo (basename)
   - Preserva metadados originais (source, page) se existirem
9. Inicializa embeddings via `get_embeddings()`
10. Cria repositório `VectorStoreRepository`
11. **Limpa dados antigos** da mesma fonte via `delete_by_source()`
12. Processa chunks em lotes de 16, gerando embeddings e salvando no banco
13. Exibe estatísticas (se não estiver em modo quiet)

**Validações**:
- Arquivo deve existir no sistema de arquivos
- Arquivo deve ser PDF (validação feita no chat, não no ingest.py diretamente)
- PDF deve conter texto extraível (pelo menos 1 chunk)

**Mensagens de Erro**:
- `ValueError`: "Caminho do PDF não especificado..." ou "Nenhum texto pôde ser extraído..."
- `FileNotFoundError`: "Arquivo PDF não encontrado: {path}"
- Erros de banco de dados: capturados e logados, mas não interrompem o fluxo silenciosamente

**Limitações**:
- Processa apenas um PDF por vez
- Não valida se PDF está corrompido ou protegido por senha
- Não suporta PDFs com imagens (apenas texto)
- Limpeza de dados antigos é automática (não há opção de desabilitar)

#### 3.1.2 Script CLI: `python src/ingest.py`

**Argumentos**:
- `pdf_path` (posicional, opcional): Caminho do PDF
- `-q, --quiet`: Modo silencioso
- `--chunk-size INT`: Tamanho do chunk
- `--chunk-overlap INT`: Sobreposição do chunk

**Comportamento**:
- Se PDF já existe na base, solicita confirmação (exceto em modo quiet)
- Em modo quiet, assume confirmação automática (sobrescreve)

### 3.2 Busca Semântica (`search.py`)

#### 3.2.1 Função: `search_prompt()`

**Descrição**: Cria uma chain LangChain configurada para busca e resposta.

**Parâmetros**:
- `top_k` (int, default=`Config.TOP_K`): Número de documentos a recuperar (padrão: 10)
- `temperature` (float, opcional): Temperatura do LLM. Se None, usa `Config.RETRIEVAL_TEMPERATURE` (padrão: 0)

**Retorno**: `RunnableSequence` do LangChain (pronta para `.invoke()`)

**Fluxo**:
1. Inicializa embeddings via `get_embeddings()`
2. Cria `VectorStoreRepository` com embeddings
3. Cria retriever com `search_type="similarity"` e `k=top_k`
4. Inicializa LLM via `get_llm(temperature=temperature)`
5. Cria prompt template (template fixo `PROMPT_TEMPLATE`)
6. Define função `format_docs()` que concatena conteúdo dos documentos
7. Monta chain: `{"contexto": retriever | format_docs, "pergunta": RunnablePassthrough()} | prompt | llm | StrOutputParser()`
8. Retorna chain

**Tratamento de Erros**:
- `ValueError`: Retorna `None`, loga erro
- `SQLAlchemyError`: Retorna `None`, loga erro
- `Exception`: Retorna `None`, loga erro com traceback

#### 3.2.2 Função: `search_with_sources()`

**Descrição**: Realiza busca e retorna resposta + metadados das fontes.

**Parâmetros**:
- `question` (str): Pergunta do usuário
- `top_k` (int, default=`Config.TOP_K`): Número de documentos
- `temperature` (float, opcional): Temperatura do LLM

**Retorno**: `dict` com chaves:
- `"answer"`: Resposta gerada (str)
- `"sources"`: Lista de dicionários com `filename`, `page`, `source`

**Fluxo**:
1. Inicializa embeddings e repositório
2. Executa `similarity_search()` no vector store
3. Formata contexto via concatenação
4. Inicializa LLM
5. Cria prompt e chain
6. Invoca chain com contexto e pergunta
7. Extrai fontes únicas dos metadados dos documentos recuperados
8. Retorna dicionário

**Tratamento de Erros**:
- Retorna dicionário com `answer` contendo mensagem de erro e `sources=[]`

#### 3.2.3 Template de Prompt

O template é fixo e está definido na constante `PROMPT_TEMPLATE`:

```
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
[...exemplos...]

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
```

**Limitações**:
- Template não é configurável (hardcoded)
- Não há suporte a templates externos ou customizáveis

### 3.3 Interface CLI (`chat.py`)

#### 3.3.1 Função Principal: `main()`

**Descrição**: Ponto de entrada do CLI.

**Fluxo**:
1. Valida configuração via `Config.validate_config()`
2. Parse de argumentos CLI
3. Ajusta nível de log se `--quiet`
4. Se `--file` especificado, executa ingestão inicial
5. Verifica status do banco via `check_database_status()`
6. Exibe boas-vindas (se não quiet)
7. Inicializa chain via `search_prompt()`
8. Inicia loop de chat via `chat_loop()`

**Argumentos CLI**:
- `-f, --file PDF_PATH`: Caminho do PDF para ingestão inicial
- `-q, --quiet`: Modo silencioso (oculta logs e mensagens)
- `-v, --verbose`: Modo detalhado (mostra estatísticas de resposta)
- `--top-k INT`: Número de documentos a recuperar
- `--temperature FLOAT`: Temperatura para geração
- `--chunk-size INT`: Tamanho do chunk para novas ingestões
- `--chunk-overlap INT`: Sobreposição do chunk para novas ingestões

**Comportamento de Encerramento**:
- Usa `os._exit(0)` para evitar erro `sys.excepthook`
- Captura `KeyboardInterrupt` e `SystemExit` graciosamente

#### 3.3.2 Função: `chat_loop()`

**Descrição**: Loop principal de interação com o usuário.

**Parâmetros**:
- `chain`: Chain LangChain configurada
- `quiet` (bool): Modo silencioso
- `verbose` (bool): Modo detalhado
- `top_k` (int, opcional): Override de top_k
- `temperature` (float, opcional): Override de temperature
- `chunk_size` (int, opcional): Override de chunk_size para novas ingestões
- `chunk_overlap` (int, opcional): Override de chunk_overlap para novas ingestões

**Comportamento**:
- Primeira pergunta mostra prompt completo: "Faça sua pergunta (ou 'help' para ajuda)\n> "
- Próximas perguntas mostram apenas: "> "
- Em modo quiet, sempre mostra apenas: "> "
- Ignora entradas vazias
- Processa comandos especiais antes de tratar como pergunta
- Verifica se banco está vazio antes de processar perguntas

**Comandos Especiais**:
- `sair`, `exit`, `quit`, `q`: Encerra o chat
- `help`, `ajuda`, `?`, `h`: Exibe ajuda
- `add <caminho>`, `ingest <caminho>`, `a <caminho>`: Adiciona PDF
- `remove <arquivo>`, `delete <arquivo>`, `r <arquivo>`: Remove arquivo específico
- `clear`, `c`: Limpa toda a base
- `stats`, `s`: Mostra estatísticas

#### 3.3.3 Função: `process_question()`

**Descrição**: Processa uma pergunta do usuário.

**Parâmetros**:
- `chain`: Chain LangChain
- `question`: Pergunta do usuário
- `quiet`: Modo silencioso
- `verbose`: Modo detalhado
- `top_k`: Override de top_k
- `temperature`: Override de temperature

**Comportamento**:
- Se não quiet, mostra: "🔍 Recuperando informações relevantes..." e "🧠 Gerando resposta baseada nos documentos..."
- Se verbose, usa `search_with_sources()` para obter fontes
- Se não verbose, usa `chain.invoke()` diretamente
- Calcula tempo de execução
- Se não quiet, formata saída com separadores
- Se verbose, mostra estatísticas (tempo, fontes)
- Se quiet, mostra apenas resposta pura (para automação)
- Se quiet E verbose, mostra resposta + estatísticas mínimas em uma linha

**Tratamento de Erros**:
- `KeyboardInterrupt`, `EOFError`: Re-lança (para captura no chat_loop)
- `SQLAlchemyError`: Mostra mensagem de erro, loga
- `Exception`: Mostra mensagem genérica, loga com traceback

#### 3.3.4 Funções de Comandos

##### `handle_add_command()`
- Valida que caminho foi especificado
- Valida existência do arquivo
- Valida extensão .pdf
- Verifica se arquivo já existe na base
- Se existe e não quiet, solicita confirmação
- Se quiet, assume confirmação automática
- Chama `ingest_pdf()` com parâmetros
- Retorna `True` se sucesso, `False` caso contrário

##### `handle_remove_command()`
- Valida que nome do arquivo foi especificado
- Lista fontes disponíveis
- Tenta encontrar correspondência (exata ou por basename)
- Se não encontrado, mostra mensagem e sugere `stats`
- Solicita confirmação
- Executa `delete_by_source()` se confirmado

##### `handle_clear_command()`
- Verifica se banco está vazio (evita confirmação desnecessária)
- Solicita confirmação ("sim" para confirmar)
- Executa `clear()` se confirmado
- Retorna `True` se limpeza foi executada

##### `handle_stats_command()`
- Obtém contagem de chunks e fontes
- Lista todas as fontes
- Exibe estatísticas formatadas

##### `display_help()`
- Exibe lista completa de comandos e atalhos
- Organizado por categorias (perguntas, documentos, ajuda, sair, admin, estatísticas)

#### 3.3.5 Funções de Validação

##### `check_database_status()`
- Retorna tupla `(num_chunks, num_sources)`
- Usa `VectorStoreRepository` para contagem
- Trata erros retornando `(0, 0)`
- Loga informações se chunks > 0

##### `display_welcome()`
- Exibe banner de boas-vindas
- Mostra status do banco (vazio ou populado)
- Mostra dica se banco vazio

### 3.4 Gerenciamento de Banco de Dados (`database.py`)

#### 3.4.1 Classe: `VectorStoreRepository`

**Padrão**: Repository Pattern

**Métodos Principais**:

##### `count() -> int`
- Conta documentos via SQL direto
- Query: `SELECT COUNT(*) FROM langchain_pg_embedding JOIN langchain_pg_collection WHERE name = :collection`
- Retorna 0 em caso de erro

##### `count_sources() -> int`
- Conta fontes únicas via SQL
- Query: `SELECT COUNT(DISTINCT cmetadata->>'source') ...`
- Retorna 0 em caso de erro

##### `list_sources() -> list[str]`
- Lista todas as fontes únicas
- Query: `SELECT DISTINCT cmetadata->>'source' ... ORDER BY ...`
- Retorna lista vazia em caso de erro

##### `exists() -> bool`
- Verifica se existem documentos
- Usa `count() > 0`

##### `clear() -> bool`
- Remove todos os documentos da coleção
- Query: `DELETE FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid ...)`
- Retorna `True` se sucesso, `False` caso contrário

##### `delete_by_source(source: str) -> bool`
- Remove todos os chunks de uma fonte específica
- Query: `DELETE FROM langchain_pg_embedding WHERE cmetadata->>'source' = :source ...`
- Retorna `True` sempre (mesmo se nada foi deletado)

##### `source_exists(source: str) -> bool`
- Verifica se fonte existe na base
- Query: `SELECT EXISTS (SELECT 1 ... WHERE cmetadata->>'source' = :source ...)`
- Retorna `False` em caso de erro

##### `add_documents(documents, ids=None)`
- Adiciona documentos ao vector store
- Usa `as_upsert()` se disponível, senão `add_documents()` direto

##### `as_retriever(**kwargs)`
- Retorna vector store como retriever
- Delega para `vector_store.as_retriever()`

**Propriedades**:
- `vector_store`: Lazy initialization do PGVector
- `engine`: Lazy initialization do SQLAlchemy engine

**Tratamento de Erros**:
- `OperationalError`: Erro de conexão, loga e retorna valor padrão
- `ProgrammingError`: Tabelas não encontradas, loga e retorna valor padrão
- `SQLAlchemyError`: Erro genérico de banco, loga e retorna valor padrão
- `Exception`: Erro inesperado, loga e retorna valor padrão

---

## 4. Fluxos Funcionais

### 4.1 Fluxo Feliz: Ingestão de PDF

1. Usuário executa: `python src/ingest.py document.pdf`
2. Sistema valida configuração (API keys, DATABASE_URL)
3. Sistema carrega PDF via PyPDFLoader
4. Sistema divide texto em chunks (1000 chars, overlap 150)
5. Sistema enriquece metadados de cada chunk
6. Sistema verifica se PDF já existe na base
   - Se existe, solicita confirmação (exceto se `--quiet`)
7. Sistema limpa dados antigos do mesmo PDF
8. Sistema gera embeddings em lotes de 16
9. Sistema salva chunks no PGVector
10. Sistema exibe estatísticas (páginas, chunks, tamanho médio)

**Resultado Esperado**: PDF ingerido com sucesso, chunks disponíveis para busca.

### 4.2 Fluxo Feliz: Pergunta no Chat

1. Usuário executa: `python src/chat.py`
2. Sistema valida configuração
3. Sistema verifica status do banco (não vazio)
4. Sistema exibe boas-vindas com contagem de documentos
5. Sistema inicializa chain de busca
6. Usuário digita pergunta
7. Sistema verifica se banco não está vazio
8. Sistema mostra indicadores de progresso ("Recuperando...", "Gerando...")
9. Sistema executa busca vetorial (top 10 chunks)
10. Sistema formata contexto
11. Sistema gera resposta via LLM
12. Sistema exibe resposta formatada
13. Sistema retorna ao prompt para próxima pergunta

**Resultado Esperado**: Resposta contextualizada baseada nos documentos.

### 4.3 Fluxo Alternativo: Ingestão com Arquivo Já Existente

1. Usuário executa: `python src/ingest.py document.pdf`
2. Sistema detecta que `document.pdf` já existe na base
3. Sistema exibe: "⚠️  O arquivo 'document.pdf' já existe na base de dados."
4. Sistema solicita: "Deseja sobrescrever os dados existentes? (sim/n): "
5. **Cenário A**: Usuário digita "sim"
   - Sistema limpa dados antigos
   - Sistema processa e salva novos dados
6. **Cenário B**: Usuário digita qualquer outra coisa
   - Sistema exibe: "Operação cancelada pelo usuário."
   - Sistema encerra sem modificar dados

**Comportamento em Modo Quiet**:
- Se `--quiet`, assume confirmação automática (sobrescreve sem perguntar)

### 4.4 Fluxo Alternativo: Pergunta com Banco Vazio

1. Usuário executa: `python src/chat.py`
2. Sistema detecta banco vazio
3. Sistema exibe: "⚠️  Status: Banco de dados vazio"
4. Sistema exibe: "💡 Dica: Use o comando 'add <caminho_pdf>' para adicionar documentos"
5. Usuário digita pergunta (não comando)
6. Sistema detecta banco vazio novamente
7. Sistema exibe: "⚠️  O banco de dados está vazio!"
8. Sistema exibe: "💡 Adicione um PDF primeiro usando 'add <caminho_pdf>'."
9. Sistema retorna ao prompt (não processa pergunta)

**Resultado**: Usuário é orientado a adicionar documentos antes de fazer perguntas.

### 4.5 Fluxo de Erro: PDF Não Encontrado

1. Usuário executa: `python src/ingest.py arquivo_inexistente.pdf`
2. Sistema valida configuração
3. Sistema verifica existência do arquivo
4. Sistema lança `FileNotFoundError`: "Arquivo PDF não encontrado: arquivo_inexistente.pdf"
5. Script encerra com código de erro

**Tratamento**: Erro não é capturado, interrompe execução.

### 4.6 Fluxo de Erro: API Key Não Configurada

1. Usuário executa: `python src/chat.py`
2. Sistema chama `Config.validate_config()`
3. Sistema detecta ausência de `GOOGLE_API_KEY` e `OPENAI_API_KEY`
4. Sistema lança `ValueError` com mensagem detalhada
5. Sistema exibe: "❌ Erro de configuração: {mensagem}"
6. Script encerra com `sys.exit(1)`

**Mensagem de Erro**: Lista variáveis faltando e orienta a configurar `.env`.

### 4.7 Fluxo com Parâmetros Combinados: Quiet + Verbose

1. Usuário executa: `python src/chat.py -q -v`
2. Sistema ativa modo quiet (oculta logs de inicialização)
3. Sistema ativa modo verbose (mostra estatísticas de resposta)
4. Sistema exibe apenas prompt simplificado: "> "
5. Usuário faz pergunta
6. Sistema processa sem mostrar indicadores de progresso (quiet)
7. Sistema exibe apenas resposta pura
8. Sistema exibe estatísticas em linha: "--- Stats: 2.34s | 3 sources ---"

**Comportamento**: Quiet suprime mensagens, mas verbose ainda mostra estatísticas mínimas.

### 4.8 Fluxo com Parâmetros: Ingestão Inicial + Chat

1. Usuário executa: `python src/chat.py -f document.pdf --chunk-size 2000 --chunk-overlap 300`
2. Sistema valida configuração
3. Sistema executa ingestão com chunk_size=2000, chunk_overlap=300
4. Se ingestão falhar, sistema continua mesmo assim (com aviso)
5. Sistema inicia chat normalmente
6. Se usuário usar `add` durante o chat, novos PDFs usarão chunk_size=2000, chunk_overlap=300 (herdados do CLI)

**Comportamento**: Parâmetros de chunk são propagados para ingestões durante o chat.

### 4.9 Fluxo: Comando Remove

1. Usuário digita: `remove document.pdf`
2. Sistema valida que nome foi especificado
3. Sistema lista fontes disponíveis
4. Sistema tenta encontrar correspondência (exata ou basename)
5. **Cenário A**: Arquivo encontrado
   - Sistema exibe: "⚠️  Você está prestes a remover TODOS os dados relacionados a: {caminho}"
   - Sistema solicita: "Tem certeza que deseja continuar? (sim/n): "
   - Se "sim", executa `delete_by_source()` e confirma
   - Se não "sim", cancela operação
6. **Cenário B**: Arquivo não encontrado
   - Sistema exibe: "⚠️  Arquivo 'document.pdf' não encontrado na base de dados."
   - Sistema sugere: "💡 Use o comando 'stats' para ver a lista de arquivos disponíveis."

### 4.10 Fluxo: Comando Clear

1. Usuário digita: `clear`
2. Sistema verifica se banco está vazio
3. **Cenário A**: Banco vazio
   - Sistema exibe: "💡 O banco de dados já está vazio. Nada para limpar."
   - Retorna ao prompt (não solicita confirmação)
4. **Cenário B**: Banco populado
   - Sistema exibe: "⚠️  CERTEZA que deseja limpar toda a base? (sim/n): "
   - Se "sim", executa `clear()` e confirma
   - Se não "sim", cancela operação

---

## 5. Interface CLI

### 5.1 Script: `python src/ingest.py`

**Sintaxe**:
```bash
python src/ingest.py [pdf_path] [-q|--quiet] [--chunk-size INT] [--chunk-overlap INT]
```

**Argumentos**:
- `pdf_path` (posicional, opcional): Caminho do PDF. Se omitido, usa `Config.PDF_PATH`
- `-q, --quiet`: Modo silencioso (oculta logs e barras de progresso)
- `--chunk-size INT`: Tamanho do chunk em caracteres (override de `Config.CHUNK_SIZE`)
- `--chunk-overlap INT`: Sobreposição entre chunks (override de `Config.CHUNK_OVERLAP`)

**Exemplos**:
```bash
python src/ingest.py document.pdf
python src/ingest.py document.pdf --quiet
python src/ingest.py document.pdf --chunk-size 2000 --chunk-overlap 300
```

**Saída** (modo normal):
- Logs de progresso
- Barra de progresso durante processamento
- Estatísticas finais (páginas, chunks, tamanho médio)

**Saída** (modo quiet):
- Apenas erros críticos (se houver)

### 5.2 Script: `python src/chat.py`

**Sintaxe**:
```bash
python src/chat.py [-f|--file PDF_PATH] [-q|--quiet] [-v|--verbose] [--top-k INT] [--temperature FLOAT] [--chunk-size INT] [--chunk-overlap INT]
```

**Argumentos**:
- `-f, --file PDF_PATH`: Caminho do PDF para ingestão inicial antes de iniciar chat
- `-q, --quiet`: Modo silencioso (oculta logs de inicialização e mensagens de status)
- `-v, --verbose`: Modo detalhado (mostra tempo de resposta e fontes utilizadas)
- `--top-k INT`: Número de documentos a recuperar na busca (override de `Config.TOP_K`)
- `--temperature FLOAT`: Temperatura para geração do LLM (override de `Config.RETRIEVAL_TEMPERATURE`)
- `--chunk-size INT`: Tamanho do chunk para novas ingestões via comando `add` (override de `Config.CHUNK_SIZE`)
- `--chunk-overlap INT`: Sobreposição do chunk para novas ingestões (override de `Config.CHUNK_OVERLAP`)

**Exemplos**:
```bash
python src/chat.py
python src/chat.py -f document.pdf
python src/chat.py --quiet --verbose
python src/chat.py --top-k 20 --temperature 0.5
python src/chat.py -f doc.pdf --chunk-size 2000 -q
```

**Comandos Disponíveis no Chat**:

| Comando | Atalho | Descrição |
|---------|--------|-----------|
| `help` | `h` | Exibe lista de comandos |
| `add <caminho>` | `a <caminho>` | Adiciona PDF ao banco |
| `ingest <caminho>` | - | (Mesmo que `add`) |
| `remove <arquivo>` | `r <arquivo>` | Remove arquivo específico |
| `delete <arquivo>` | - | (Mesmo que `remove`) |
| `clear` | `c` | Limpa toda a base |
| `stats` | `s` | Mostra estatísticas |
| `sair` | `q` | Encerra o chat |
| `exit` | - | (Mesmo que `sair`) |
| `quit` | - | (Mesmo que `sair`) |

**Comportamento de Atalhos**:
- Atalhos funcionam apenas quando o comando está sozinho (ex: `h` funciona, mas `help` também)
- Para comandos com argumentos, o atalho deve ser seguido de espaço e argumento (ex: `a document.pdf`)

**Prompt**:
- Primeira pergunta: `"Faça sua pergunta (ou 'help' para ajuda)\n> "`
- Próximas perguntas: `"> "`
- Modo quiet: sempre `"> "`

**Encerramento**:
- Comandos: `sair`, `exit`, `quit`, `q`
- Interrupção: `Ctrl+C` ou `Ctrl+D`
- Mensagem: "👋 Até logo! Chat encerrado." (exceto em modo quiet)

---

## 6. Configurações

### 6.1 Variáveis de Ambiente (`.env`)

#### 6.1.1 API Keys (Obrigatório: pelo menos uma)

**GOOGLE_API_KEY**
- Tipo: String
- Obrigatório: Não (mas necessário se OpenAI não estiver configurado)
- Descrição: Chave de API do Google Gemini
- Exemplo: `GOOGLE_API_KEY=AIzaSy...`

**OPENAI_API_KEY**
- Tipo: String
- Obrigatório: Não (mas necessário se Google não estiver configurado)
- Descrição: Chave de API da OpenAI
- Exemplo: `OPENAI_API_KEY=sk-...`

**Prioridade**: Se ambas estiverem configuradas, Google tem prioridade.

#### 6.1.2 Modelos Google (Opcional, usado se GOOGLE_API_KEY configurado)

**GOOGLE_EMBEDDING_MODEL**
- Tipo: String
- Padrão: `"models/text-embedding-004"` (nota: código usa este padrão, mas `.env.example` sugere `models/embedding-001`)
- Descrição: Modelo de embeddings do Google
- Exemplo: `GOOGLE_EMBEDDING_MODEL='models/embedding-001'`

**GOOGLE_LLM_MODEL**
- Tipo: String
- Padrão: `"gemini-2.5-flash-lite"`
- Descrição: Modelo LLM do Google
- Exemplo: `GOOGLE_LLM_MODEL='gemini-2.5-flash-lite'`

#### 6.1.3 Modelos OpenAI (Opcional, usado se OPENAI_API_KEY configurado)

**OPENAI_EMBEDDING_MODEL**
- Tipo: String
- Padrão: `"text-embedding-3-small"`
- Descrição: Modelo de embeddings da OpenAI
- Exemplo: `OPENAI_EMBEDDING_MODEL='text-embedding-3-small'`

**OPENAI_LLM_MODEL**
- Tipo: String
- Padrão: `"gpt-4o-mini"`
- Descrição: Modelo LLM da OpenAI
- Exemplo: `OPENAI_LLM_MODEL='gpt-4o-mini'`

#### 6.1.4 Banco de Dados (Obrigatório)

**DATABASE_URL**
- Tipo: String
- Obrigatório: Sim
- Descrição: URL de conexão PostgreSQL
- Formato: `postgresql://usuario:senha@host:porta/database`
- Exemplo: `DATABASE_URL='postgresql://postgres:postgres@localhost:5432/rag'`

**PG_VECTOR_COLLECTION_NAME**
- Tipo: String
- Obrigatório: Sim
- Descrição: Nome da coleção/tabela no PGVector
- Exemplo: `PG_VECTOR_COLLECTION_NAME='pdf_embeddings'`

#### 6.1.5 Ingestão (Opcional)

**PDF_PATH**
- Tipo: String
- Obrigatório: Não (pode ser passado como argumento)
- Descrição: Caminho padrão do PDF para ingestão
- Exemplo: `PDF_PATH='document.pdf'`

**CHUNK_SIZE**
- Tipo: Integer
- Padrão: `1000`
- Descrição: Tamanho do chunk em caracteres
- Exemplo: `CHUNK_SIZE=1000`

**CHUNK_OVERLAP**
- Tipo: Integer
- Padrão: `150`
- Descrição: Sobreposição entre chunks em caracteres
- Exemplo: `CHUNK_OVERLAP=150`

#### 6.1.6 Busca/Retrieval (Opcional)

**TOP_K**
- Tipo: Integer
- Padrão: `10`
- Descrição: Número de documentos a recuperar na busca
- Exemplo: `TOP_K=10`

**RETRIEVAL_TEMPERATURE**
- Tipo: Float
- Padrão: `0.0`
- Descrição: Temperatura para geração do LLM (0 = determinístico, >0 = mais criativo)
- Exemplo: `RETRIEVAL_TEMPERATURE=0`

### 6.2 Validação de Configuração

A função `Config.validate_config()` é chamada no início de `chat.py` e `ingest.py`.

**Validações**:
1. Pelo menos uma API key deve estar configurada (GOOGLE_API_KEY ou OPENAI_API_KEY)
2. DATABASE_URL deve estar configurada
3. PG_VECTOR_COLLECTION_NAME deve estar configurada

**Comportamento em Falha**:
- Lança `ValueError` com mensagem detalhada listando variáveis faltando
- Scripts encerram com `sys.exit(1)`

### 6.3 Propriedades Dinâmicas (Agnósticas ao Provedor)

A classe `Config` fornece propriedades que retornam valores baseados no provedor disponível:

**Config.API_KEY**
- Retorna `GOOGLE_API_KEY` se configurada, senão `OPENAI_API_KEY`
- Lança `ValueError` se nenhuma estiver configurada

**Config.EMBEDDING_MODEL**
- Retorna `GOOGLE_EMBEDDING_MODEL` se Google configurado, senão `OPENAI_EMBEDDING_MODEL`
- Lança `ValueError` se nenhuma API key estiver configurada

**Config.LLM_MODEL**
- Retorna `GOOGLE_LLM_MODEL` se Google configurado, senão `OPENAI_LLM_MODEL`
- Lança `ValueError` se nenhuma API key estiver configurada

### 6.4 Comportamentos Condicionais

#### 6.4.1 Detecção de Provedor
- Se `GOOGLE_API_KEY` configurada → usa Google (embeddings e LLM)
- Senão, se `OPENAI_API_KEY` configurada → usa OpenAI
- Se nenhuma configurada → erro de validação

#### 6.4.2 Modo Quiet
- Quando `--quiet` ou `quiet=True`:
  - Nível de log ajustado para `WARNING` globalmente
  - Logs de inicialização suprimidos
  - Barras de progresso desabilitadas (tqdm)
  - Mensagens de status suprimidas
  - Confirmações assumem resposta positiva (sobrescreve sem perguntar)

#### 6.4.3 Modo Verbose
- Quando `--verbose` ou `verbose=True`:
  - Usa `search_with_sources()` em vez de `chain.invoke()`
  - Mostra tempo de execução
  - Mostra lista de fontes utilizadas (arquivo + página)
  - Em modo quiet+verbose, mostra estatísticas em linha compacta

---

## 7. Estados e Restrições do Sistema

### 7.1 Estado: Banco de Dados Vazio

**Condição**: `count() == 0`

**Comportamento**:
- Chat exibe aviso na inicialização
- Perguntas são bloqueadas com mensagem orientativa
- Comando `clear` detecta e informa que já está vazio (não solicita confirmação)
- Comando `stats` mostra "A base de dados está vazia."

**Ações Permitidas**:
- Comandos: `help`, `add`, `sair`
- Não permitido: fazer perguntas

### 7.2 Estado: Documento Já Existente

**Condição**: `source_exists(pdf_path) == True`

**Comportamento**:
- Ingestão detecta e solicita confirmação (exceto em modo quiet)
- Se confirmado, limpa dados antigos antes de re-ingerir
- Se não confirmado, cancela operação

**Limitação**: Não há modo "append" - sempre substitui completamente.

### 7.3 Estado: PDF Não Encontrado

**Condição**: Arquivo não existe no sistema de arquivos

**Comportamento**:
- `ingest.py`: Lança `FileNotFoundError`, encerra script
- `chat.py` (comando `add`): Exibe mensagem de erro, retorna ao prompt

### 7.4 Estado: Falha de Configuração

**Condição**: Variáveis críticas ausentes no `.env`

**Comportamento**:
- `Config.validate_config()` lança `ValueError`
- Scripts exibem mensagem de erro e encerram com código 1
- Mensagem lista variáveis faltando

### 7.5 Estado: Falha de Conexão com Banco

**Condição**: PostgreSQL inacessível ou tabelas não existem

**Comportamento**:
- `VectorStoreRepository` captura `OperationalError` ou `ProgrammingError`
- Métodos retornam valores padrão (0, [], False)
- Logs registram erro
- Chat pode iniciar, mas operações falham silenciosamente
- Mensagens de erro são logadas, mas não sempre exibidas ao usuário

**Limitação**: Não há retry automático ou validação proativa de conexão.

### 7.6 Estado: Arquivo Não Encontrado na Base (Comando Remove)

**Condição**: `remove <arquivo>` com arquivo que não existe

**Comportamento**:
- Sistema lista fontes disponíveis
- Tenta correspondência exata ou por basename
- Se não encontrado, exibe mensagem e sugere usar `stats`
- Retorna ao prompt (não encerra)

### 7.7 Restrições de Validação

#### 7.7.1 Validação de Arquivo PDF
- **Onde**: Apenas no `chat.py` (comando `add`)
- **Validação**: Verifica extensão `.pdf` (case-insensitive)
- **Comportamento**: Rejeita arquivos sem extensão `.pdf`
- **Limitação**: `ingest.py` não valida extensão (aceita qualquer arquivo que PyPDFLoader consiga processar)

#### 7.7.2 Validação de Chunks Vazios
- **Onde**: `ingest.py` após chunking
- **Validação**: Verifica se `len(splits) > 0`
- **Comportamento**: Lança `ValueError` se nenhum chunk foi gerado
- **Causas Possíveis**: PDF vazio, PDF protegido, PDF apenas com imagens

---

## 8. Limitações Atuais

### 8.1 Limitações Técnicas

#### 8.1.1 Singleton de LLM com Temperatura
- **Limitação**: O singleton de LLM é resetado apenas quando temperatura muda explicitamente
- **Impacto**: Se temperatura for alterada via CLI, singleton é recriado, mas mudanças subsequentes podem não ser refletidas se o valor for o mesmo
- **Workaround**: Reiniciar o chat para garantir reset completo

#### 8.1.2 Import Faltante em `chat.py`
- **Limitação**: `chat.py` usa `sa.exc.SQLAlchemyError` mas não importa `sqlalchemy as sa`
- **Impacto**: Erro de runtime se exceção for lançada (NameError)
- **Status**: Bug conhecido no código atual

#### 8.1.3 Processamento em Lotes Fixo
- **Limitação**: Batch size é hardcoded como 16 em `ingest.py`
- **Impacto**: Não é configurável via CLI ou `.env`
- **Workaround**: Modificar código-fonte

#### 8.1.4 Template de Prompt Fixo
- **Limitação**: Template está hardcoded em `search.py`
- **Impacto**: Não é possível customizar prompt sem modificar código
- **Workaround**: Editar constante `PROMPT_TEMPLATE`

#### 8.1.5 Sem Validação de PDF Corrompido
- **Limitação**: Sistema não valida integridade do PDF antes de processar
- **Impacto**: Pode falhar silenciosamente ou gerar chunks vazios
- **Workaround**: Validar PDF externamente antes de ingerir

#### 8.1.6 Sem Timeout Configurável
- **Limitação**: Operações de busca e LLM não têm timeout
- **Impacto**: Pode travar indefinidamente se API estiver lenta
- **Workaround**: Interromper manualmente (Ctrl+C)

### 8.2 Limitações Funcionais

#### 8.2.1 Apenas PDFs
- **Limitação**: Suporta apenas arquivos PDF
- **Impacto**: Não é possível ingerir outros formatos (DOCX, TXT, etc.)
- **Workaround**: Converter outros formatos para PDF antes

#### 8.2.2 Sem Histórico de Conversas
- **Limitação**: Cada pergunta é independente, sem contexto de perguntas anteriores
- **Impacto**: Não é possível fazer perguntas de follow-up que dependem de contexto anterior
- **Workaround**: Reformular perguntas de forma autossuficiente

#### 8.2.3 Sem Cache de Embeddings
- **Limitação**: Embeddings são gerados a cada busca, mesmo para perguntas idênticas
- **Impacto**: Performance desnecessária para perguntas repetidas
- **Workaround**: Nenhum (limitação de design)

#### 8.2.4 Sem Suporte a Múltiplos PDFs em Uma Pergunta
- **Limitação**: Todos os PDFs são tratados como um corpus único
- **Impacto**: Não é possível fazer perguntas específicas sobre um PDF quando há múltiplos
- **Workaround**: Usar `remove` para isolar PDFs antes de perguntar

#### 8.2.5 Sem Modo Append na Ingestão
- **Limitação**: Re-ingerir um PDF sempre substitui dados antigos completamente
- **Impacto**: Não é possível adicionar novos chunks sem perder os antigos
- **Workaround**: Nenhum (limitação de design)

#### 8.2.6 Sem Validação de Duplicatas de Chunks
- **Limitação**: Sistema não detecta se o mesmo conteúdo foi ingerido múltiplas vezes
- **Impacto**: Pode haver chunks duplicados no banco
- **Workaround**: Gerenciar manualmente quais PDFs são ingeridos

### 8.3 Limitações de Design

#### 8.3.1 Confirmações em Modo Quiet
- **Limitação**: Em modo quiet, confirmações assumem resposta positiva automaticamente
- **Impacto**: Pode sobrescrever dados sem aviso em scripts automatizados
- **Workaround**: Não usar `--quiet` em operações destrutivas

#### 8.3.2 Sem Validação de Tamanho de Chunk
- **Limitação**: Sistema aceita qualquer valor de `chunk_size` e `chunk_overlap`
- **Impacto**: Valores inválidos (ex: overlap > size) podem causar comportamento inesperado
- **Workaround**: Validar valores manualmente antes de usar

#### 8.3.3 Sem Validação de Modelo de Embedding
- **Limitação**: Sistema não valida se o modelo especificado existe ou é válido
- **Impacto**: Erro só aparece em runtime quando tenta usar o modelo
- **Workaround**: Testar configuração antes de usar em produção

#### 8.3.4 Sem Suporte a Múltiplas Coleções
- **Limitação**: Sistema usa apenas uma coleção (definida por `PG_VECTOR_COLLECTION_NAME`)
- **Impacto**: Não é possível separar documentos em diferentes namespaces
- **Workaround**: Usar diferentes instâncias do banco ou diferentes valores de `PG_VECTOR_COLLECTION_NAME`

### 8.4 Limitações de Interface

#### 8.4.1 Sem Interface Web
- **Limitação**: Apenas CLI disponível
- **Impacto**: Requer conhecimento de linha de comando
- **Workaround**: Nenhum (limitação de design)

#### 8.4.2 Sem Autocomplete de Comandos
- **Limitação**: CLI não oferece autocomplete ou sugestões
- **Impacto**: Usuário deve conhecer comandos de memória
- **Workaround**: Usar comando `help` frequentemente

#### 8.4.3 Sem Histórico de Comandos Persistente
- **Limitação**: Histórico de comandos não é salvo entre sessões
- **Impacto**: Não é possível revisar perguntas anteriores
- **Workaround**: Nenhum (limitação de design)

#### 8.4.4 Sem Formatação Rica de Respostas
- **Limitação**: Respostas são texto plano, sem markdown ou formatação
- **Impacto**: Respostas longas podem ser difíceis de ler
- **Workaround**: Usar ferramentas externas para formatação

---

## 9. Mensagens de Erro e Códigos

### 9.1 Erros de Configuração

**Mensagem**: `"Configurações críticas ausentes no arquivo .env:\n  - {lista}\n\nPor favor, configure estas variáveis no arquivo .env antes de continuar."`

**Código**: `ValueError`  
**Onde**: `Config.validate_config()`  
**Ação do Sistema**: Script encerra com `sys.exit(1)`

### 9.2 Erros de Arquivo

**Mensagem**: `"Arquivo PDF não encontrado: {path}"`

**Código**: `FileNotFoundError`  
**Onde**: `ingest.py`  
**Ação do Sistema**: Script encerra (não capturado)

**Mensagem**: `"❌ Erro: Arquivo não encontrado: {path}"`

**Código**: Não lança exceção  
**Onde**: `chat.py` (comando `add`)  
**Ação do Sistema**: Retorna ao prompt

### 9.3 Erros de Banco de Dados

**Mensagem**: `"Falha de conexão com o banco de dados: {erro}"`

**Código**: `OperationalError` (SQLAlchemy)  
**Onde**: `database.py`  
**Ação do Sistema**: Métodos retornam valores padrão (0, [], False), erro é logado

**Mensagem**: `"Tabelas não encontradas (banco inicializado mas vazio). Detalhe: {erro}"`

**Código**: `ProgrammingError` (SQLAlchemy)  
**Onde**: `database.py`  
**Ação do Sistema**: Métodos retornam 0, erro é logado como warning

**Mensagem**: `"❌ Erro crítico de banco de dados: {erro}"`

**Código**: `SQLAlchemyError`  
**Onde**: `chat.py` (process_question)  
**Ação do Sistema**: Exibe mensagem, loga erro, retorna ao prompt

### 9.4 Erros de Processamento

**Mensagem**: `"Nenhum texto pôde ser extraído do PDF. O arquivo pode estar vazio ou protegido."`

**Código**: `ValueError`  
**Onde**: `ingest.py`  
**Ação do Sistema**: Script encerra (não capturado)

**Mensagem**: `"❌ Erro inesperado ao processar pergunta: {erro}"`

**Código**: `Exception` genérica  
**Onde**: `chat.py` (process_question)  
**Ação do Sistema**: Exibe mensagem, loga com traceback, retorna ao prompt

### 9.5 Erros de API

**Mensagem**: (Erros de API não são explicitamente tratados no código atual)

**Código**: Exceções das bibliotecas LangChain/Google/OpenAI  
**Onde**: `embeddings_manager.py`, `llm_manager.py`, `search.py`  
**Ação do Sistema**: Depende da biblioteca - geralmente propaga exceção ou retorna None/erro genérico

---

## 10. Decisões de Design Explícitas

### 10.1 Prioridade do Provedor Google sobre OpenAI
- **Decisão**: Se ambas as API keys estiverem configuradas, Google tem prioridade
- **Implementação**: Verificação `if Config.GOOGLE_API_KEY` antes de `elif Config.OPENAI_API_KEY`
- **Razão**: Não documentada no código, mas consistente em todos os managers

### 10.2 Limpeza Automática na Re-ingestão
- **Decisão**: Sempre limpa dados antigos antes de re-ingerir o mesmo PDF
- **Implementação**: `repo.delete_by_source()` chamado automaticamente em `ingest_pdf()`
- **Razão**: Evita chunks órfãos se número de chunks mudar

### 10.3 IDs Determinísticos Baseados em Arquivo
- **Decisão**: IDs seguem padrão `{filename}-{index}`
- **Implementação**: `chunk_id = f"{filename}-{i}"` em `ingest.py`
- **Razão**: Permite identificação clara da origem do chunk

### 10.4 Batch Size Fixo de 16
- **Decisão**: Processamento em lotes de 16 chunks
- **Implementação**: `batch_size = 16` hardcoded
- **Razão**: Balanceamento entre performance e uso de memória (não documentado)

### 10.5 Modo Quiet Assume Confirmações Positivas
- **Decisão**: Em modo quiet, confirmações são assumidas como "sim"
- **Implementação**: Lógica condicional em `ingest.py` e `chat.py`
- **Razão**: Facilita automação, mas pode ser perigoso

### 10.6 Encerramento com `os._exit()`
- **Decisão**: Usa `os._exit(0)` em vez de `sys.exit(0)`
- **Implementação**: `main()` em `chat.py`
- **Razão**: Evita erro `sys.excepthook` ao encerrar (documentado no CHANGELOG)

### 10.7 Template de Prompt Fixo
- **Decisão**: Template não é configurável
- **Implementação**: Constante `PROMPT_TEMPLATE` em `search.py`
- **Razão**: Conformidade com requisitos.md (template especificado)

### 10.8 Validação de Extensão PDF Apenas no Chat
- **Decisão**: Validação de extensão `.pdf` apenas em `chat.py`, não em `ingest.py`
- **Implementação**: Verificação `if not pdf_path.lower().endswith('.pdf')` apenas no comando `add`
- **Razão**: `ingest.py` pode ser usado programaticamente com outros formatos (se PyPDFLoader suportar)

---

## 11. Observações Finais

### 11.1 Divergências entre Código e Documentação

1. **`.env.example` sugere `models/embedding-001`**, mas código usa padrão `models/text-embedding-004`
2. **README menciona "gpt-5-nano"** em requisitos, mas código usa `gpt-4o-mini` como padrão
3. **CHANGELOG menciona features** que podem não estar completamente implementadas (verificar código)

### 11.2 Bugs Conhecidos

1. **Import faltante**: `chat.py` usa `sa.exc.SQLAlchemyError` sem importar `sqlalchemy as sa`
2. **Validação inconsistente**: Extensão PDF validada apenas no chat, não no ingest.py

### 11.3 Áreas de Melhoria Identificadas (Não Implementadas)

- Cache de embeddings
- Histórico de conversas
- Timeout configurável
- Templates customizáveis
- Suporte a múltiplos formatos
- Validação de integridade de PDF
- Retry automático em falhas de conexão
- Interface web
- Autocomplete de comandos

---

**Fim do Documento**
