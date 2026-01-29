# Especificação Funcional (As-Is)
## Sistema RAG - Ingestão e Busca Semântica com LangChain

**Versão do Documento:** 2.0  
**Data:** 2026-01-29  
**Baseado em:** Análise estática profunda do código-fonte (Versão de Produção 0.5.0)
**Status:** Documento de Referência Técnica Completa (Deep Dive)

---

## 1. Visão Geral do Sistema

### 1.1 Objetivo e Escopo
O **Sistema RAG (Retrieval-Augmented Generation)** é uma solução de software de linha de comando (CLI) desenvolvida para permitir a ingestão, indexação e consulta semântica de documentos técnicos em formato PDF. O sistema utiliza técnicas modernas de Inteligência Artificial Generativa para responder perguntas formuladas em linguagem natural, baseando-se estritamente no conteúdo dos documentos processados.

O escopo funcional abrange desde a leitura bruta de arquivos PDF, passando pelo processamento de texto (chunking), geração de embeddings vetoriais, armazenamento persistente em banco de dados relacional (PostgreSQL com pgVector), até a interface de usuário interativa para consulta (Chat REPL).

### 1.2 Público-Alvo
Esta especificação destina-se a:
- **Engenheiros de QA**: Para elaboração de casos de teste de caixa-branca e caixa-preta.
- **Desenvolvedores**: Como manual de referência da implementação atual.
- **Arquitetos de Solução**: Para análise de decisões de design e limitações técnicas.

### 1.3 Fronteiras do Sistema (O que NÃO faz)
Para clareza de escopo, define-se explicitamente o que o sistema não realiza na versão atual:
1.  **Suporte a Múltiplos Formatos**: O sistema processa **exclusivamente** arquivos com extensão `.pdf`. Arquivos `.txt`, `.docx`, `.html` ou outros são rejeitados ou ignorados.
2.  **OCR (Reconhecimento Óptico de Caracteres)**: PDFs que consistem apenas em imagens digitalizadas (scanned PDFs) sem camada de texto selecionável não gerarão chunks de texto e resultarão em erro de validação ("Nenhum texto pôde ser extraído").
3.  **Interface Gráfica**: Não há interface Web (HTML/JS) ou Desktop (GUI). A interação é 100% via terminal (STDIN/STDOUT).
4.  **Autenticação e Autorização**: O sistema assume que o usuário com acesso ao terminal e às variáveis de ambiente tem permissão total (root/admin) sobre a base de conhecimento. Não há logins, usuários ou níveis de permissão.
5.  **Memória Conversacional (Chat History Context)**: O modelo de linguagem (LLM) não recebe o histórico das perguntas anteriores. Cada interação é "stateless" do ponto de vista da IA. Perguntas como "E qual é o preço dele?" (referindo-se ao objeto da pergunta anterior) não funcionarão como esperado.

---

## 2. Arquitetura Funcional Detalhada

A aplicação é construída em Python (3.10+) seguindo uma arquitetura modular. Abaixo detalhamos a responsabilidade técnica e funcional de cada módulo encontrado em `src/`.

### 2.1 Módulo de Configuração (`src/config.py`)

Este módulo atua como a espinha dorsal de configuração do sistema. Ele não apenas carrega valores, mas impõe regras de negócio sobre a validade do ambiente.

#### 2.1.1 Classe `Config`
Atributos estáticos carregados via `python-dotenv`:

| Atributo | Origem (.env) | Tipo | Padrão (Default) | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `PROJECT_ROOT` | (Calculado) | Path | `Path(__file__).parent.parent` | Caminho raiz absoluto do projeto. |
| `DATABASE_URL` | `DATABASE_URL` | Str | - | **CRÍTICO**. Connection string do PostgreSQL. |
| `PG_VECTOR_COLLECTION_NAME` | `PG_VECTOR_COLLECTION_NAME` | Str | - | Nome da tabela lógica no pgVector. |
| `GOOGLE_API_KEY` | `GOOGLE_API_KEY` | Str | - | Chave para serviços Google Gemini. |
| `OPENAI_API_KEY` | `OPENAI_API_KEY` | Str | - | Chave para serviços OpenAI. |
| `PDF_PATH` | `PDF_PATH` | Str | - | Caminho padrão para ingestão se não informado via CLI. |
| `CHUNK_SIZE` | `CHUNK_SIZE` | Int | `1000` | Tamanho do fragmento de texto. |
| `CHUNK_OVERLAP` | `CHUNK_OVERLAP` | Int | `150` | Sobreposição entre fragmentos. |
| `TOP_K` | `TOP_K` | Int | `10` | Número de chunks recuperados na busca. |
| `RETRIEVAL_TEMPERATURE` | `RETRIEVAL_TEMPERATURE` | Float | `0.0` | Temperatura da LLM (0.0 a 1.0). |
| `SEARCH_TIMEOUT` | `SEARCH_TIMEOUT` | Int | `30` | Tempo máximo em segundos para operações de busca. |

#### 2.1.2 Lógica de Seleção de Provedor (`Config.set_provider`)
O sistema suporta troca dinâmica de provedor.
- **Default**: Se `GOOGLE_API_KEY` estiver presente, assume `google`. Caso contrário e `OPENAI_API_KEY` presente, assume `openai`. Se ambos ausentes, erro.
- **Forced**: O método `set_provider('openai')` força o uso da OpenAI mesmo que a chave do Google exista, alterando o comportamento das propriedades `API_KEY`, `EMBEDDING_MODEL` e `LLM_MODEL`.

#### 2.1.3 Validação (`Config.validate_config`)
Executada no início de `ingest.py` e `chat.py`.
- **Regra 1**: Verifica se `DATABASE_URL` e `PG_VECTOR_COLLECTION_NAME` estão preenchidos.
- **Regra 2**: Verifica se pelo menos uma chave de API (`GOOGLE` ou `OPENAI`) está disponível.
- **Ação em Falha**: Lança `ValueError` com lista detalhada de variáveis faltantes, abortando a execução.

### 2.2 Módulo de Banco de Dados (`src/database.py`)

Implementa o padrão **Repository** para abstrair a complexidade do `langchain_postgres`. Diferente de implementações simples, este módulo usa **SQL Direto (SQLAlchemy Text)** para performance e precisão em contagens e deleções.

#### 2.2.1 Classe `VectorStoreRepository`

##### Método `__init__(embeddings)`
- **Lógica**: Inicialização "Lazy". A conexão com o banco não é aberta instantaneamente, apenas quando uma propriedade (`vector_store` ou `engine`) é acessada.

##### Método `count() -> int`
- **Funcionalidade**: Retorna o número total de chunks na coleção atual.
- **SQL Utilizado**:
  ```sql
  SELECT COUNT(*) 
  FROM langchain_pg_embedding e
  JOIN langchain_pg_collection c ON e.collection_id = c.uuid
  WHERE c.name = :collection
  ```
- **Tratamento de Erro**: Captura `sa.exc.OperationalError` (banco fora do ar) e `sa.exc.ProgrammingError` (tabelas inexistentes), retornando `0` e logando erro/aviso.

##### Método `count_sources() -> int`
- **Funcionalidade**: Retorna o número de **arquivos únicos** ingeridos.
- **SQL Utilizado**:
  ```sql
  SELECT COUNT(DISTINCT e.cmetadata->>'source') 
  FROM langchain_pg_embedding e
  ...
  ```
- **Nota Técnica**: Acessa o campo JSONB `cmetadata` diretamente.

##### Método `list_sources() -> list[str]`
- **Funcionalidade**: Retorna lista de strings com os caminhos dos arquivos.
- **Uso**: Usado pelo comando `stats` e `remove` do CLI.

##### Método `delete_by_source(source: str) -> bool`
- **Funcionalidade**: Remove atomicamente todos os chunks associados a um arquivo PDF.
- **SQL Utilizado**:
  ```sql
  DELETE FROM langchain_pg_embedding 
  WHERE cmetadata->>'source' = :source
  AND collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = :collection)
  ```
- **Uso**: Chamado antes de qualquer re-ingestão ou pelo comando `remove`.
- **Transação**: Executa dentro de um bloco `with conn.begin():` para garantir atomicidade.

##### Método `clear() -> bool`
- **Funcionalidade**: Limpa toda a coleção (Wipeout).
- **Segurança**: Primeiro busca o UUID da coleção pelo nome, depois deleta tudo associado a esse UUID. Evita deletar coleções erradas se houver múltiplas no mesmo banco.

### 2.3 Módulo de Ingestão (`src/ingest.py`)

Responsável pelo pipeline ETL (Extract, Transform, Load).

#### 2.3.1 Função `normalize_pdf_path(path: str) -> str`
- **Objetivo**: Garantir consistência no metadado `source`.
- **Lógica**:
  1. Converte para caminho absoluto (`os.path.realpath`).
  2. Tenta calcular caminho relativo à `PROJECT_ROOT`.
  3. Se o arquivo estiver dentro do projeto, retorna relativo (ex: `docs/manual.pdf`).
  4. Se estiver fora (ex: `/tmp/doc.pdf`), mantém absoluto.

#### 2.3.2 Função `ingest_pdf(...)`
Esta é a função "workhorse" do sistema.

**Fluxo de Execução Passo-a-Passo:**
1.  **Validação Config**: Chama `Config.validate_config()`.
2.  **Validação de Args**:
    - `chunk_size` deve ser > 0.
    - `chunk_overlap` deve ser >= 0 e < `chunk_size`.
    - Lança `ValueError` se inválido.
3.  **Setup do Logger**: Se `quiet=True`, define nível global para `WARNING` (suprime INFO/DEBUG).
4.  **Resolução de Caminho**: Determina `input_pdf` (Argumento > Config > Erro).
5.  **Validação de Arquivo**:
    - Existe? (`os.path.exists`) -> Senão, `FileNotFoundError`.
    - Extensão `.pdf`? (`endswith`) -> Senão, `TypeError`.
6.  **Carregamento (Extract)**: Usa `PyPDFLoader`.
7.  **Fragmentação (Transform)**:
    - Usa `RecursiveCharacterTextSplitter`.
    - Separa por parágrafos, quebras de linha, espaços.
    - Se a lista `splits` resultante for vazia, lança `ValueError` ("Nenhum texto pôde ser extraído").
8.  **Enriquecimento de Metadados**:
    - Itera sobre cada chunk gerando um `chunk_id` determinístico: `{filename}-{i}`.
    - Adiciona campos: `chunk_index`, `total_chunks`, `filename`, `source`.
    - Limpa campos nulos originais.
    - Utiliza `tqdm` para mostrar barra de progresso (exceto se `quiet`).
9.  **Preparação de Banco (Pre-Load)**:
    - Instancia `VectorStoreRepository`.
    - Executa `repo.delete_by_source(source)` preventivamente para limpar versão anterior do documento.
10. **Inserção em Lotes (Load)**:
    - Define `batch_size = 16`.
    - Itera chunks em lotes.
    - Chama `repo.add_documents(batch_docs, ids=batch_ids)`.
    - IDs explícitos permitem upsert/idempotência.
11. **Finalização**:
    - Calcula estatísticas (tamanho médio de chunk).
    - Exibe relatório final formatado (exceto se `quiet`).

### 2.4 Módulo de Interface e CLI (`src/cli/`)

#### 2.4.1 `src/cli/ui.py`
Módulo de apresentação puramente visual.
- **Constantes**: `DISPLAY_WIDTH = 70`.
- **Função `display_welcome(counts)`**: Imprime banner ASCII e status do banco.
  - Lógica Condicional: Se `counts[0] == 0`, exibe aviso amarelo com dica de comando `add`.
- **Função `display_help()`**: Categoriza comandos em "Fazer Perguntas", "Gerenciar Documentos", "Ajuda", "Sair", "Limpar" e "Estatísticas".

#### 2.4.2 `src/cli/validators.py`
Funções puras de análise de strings (Parsing).
- `is_exit_command(text)`: Retorna True para `['sair', 'exit', 'quit', 'q']`.
- `is_help_command(text)`: Retorna True para `['help', 'ajuda', '?', 'h']`.
- `is_add_command(text)`: Detecta `add`, `ingest`, `a` no início da string.
- `parse_repeat_command(text)`:
  - Regex: `^!(\d+)$`
  - Retorna: Inteiro `N` se match, ou `None`.

#### 2.4.3 `src/cli/history.py`
Módulo de gestão de estado de sessão.
- **Classe `ChatHistory`**:
  - `__init__`: Tenta carregar arquivo `.chat_history`.
  - `add(command)`: Adiciona comando à lista em memória e faz append no arquivo.
  - `get_by_index(index)`: Retorna o comando na posição `index-1` (ajuste 1-based para 0-based).
  - `display()`: Imprime lista numerada dos últimos comandos.

#### 2.4.4 `src/cli/commands.py`
Controlador de comandos (Controller Layer).
- **`handle_add_command`**: Wrapper em torno de `ingest_pdf`. Adiciona camada de interação (perguntar "Sobrescrever?") se não estiver em modo quiet.
- **`handle_remove_command`**:
  - Lista fontes do banco.
  - Faz matching parcial (substring) ou exato.
  - Se encontrar ambiguidade ou nenhum arquivo, avisa usuário.
  - Solicita confirmação explícita antes de chamar `repo.delete_by_source`.
- **`handle_clear_command`**: Solicita confirmação explícita antes de `repo.clear()`.
- **`process_question`**:
  - Timer: `start_time = time.time()`.
  - Invoca search chain.
  - Trata `SQLAlchemyError` (exibe "Erro crítico de banco").
  - Formata output:
    - Modo Normal: Resposta + Separadores.
    - Modo Verbose: Resposta + Fontes + Tempo de execução + Separadores.
    - Modo Quiet: Apenas a Resposta (Raw).

### 2.5 Módulo de Chat (`src/chat.py`)

Ponto de entrada principal (`main` e `chat_loop`).

#### 2.5.1 Função `main()`
- **Argparse Completo**:
  | Flag | Long Flag | Tipo | Help |
  | :--- | :--- | :--- | :--- |
  | `-f` | `--file` | str | Caminho do PDF para ingestão inicial. |
  | | `--provider` | str | `google` ou `openai`. |
  | `-q` | `--quiet` | bool | Modo silencioso. |
  | `-v` | `--verbose` | bool | Modo detalhado. |
  | | `--top-k` | int | Override de Config.TOP_K. |
  | | `--temperature` | float | Override de Config.RETRIEVAL_TEMPERATURE. |
  | | `--chunk-size` | int | Override para ingestão. |
  | | `--chunk-overlap` | int | Override para ingestão. |
  | | `--search-timeout` | int | Override de timeout. |
  | | `--prompt-template` | str | Caminho de arquivo template. |
- **Inicialização**:
  1. Configura nível de log (Quiet vs Normal).
  2. Aplica Provider Override se flag estiver presente (Reseta Singletons).
  3. Valida Config.
  4. Executa ingestão inicial (se `-f` presente).
  5. Checa status do banco (para mensagem de boas-vindas).
  6. Instancia Chain (`search_prompt`).
  7. Entra no Loop de Chat.

#### 2.5.2 Função `chat_loop()`
- Loop infinito `while True`.
- `input()`: Lê entrada do usuário (com prompt `> `).
- Tratamento de `KeyboardInterrupt`: Captura Ctrl+C para saída graciosa.
- Roteamento:
  - Vazio -> `continue`
  - Comando `!N` -> Expande comando do histórico.
  - Comando `history` -> Exibe histórico.
  - Comando `exit` -> Break.
  - Comandos `add/clear/remove/stats` -> Chama handlers em `cli.commands`.
  - Outros -> Verifica se banco vazio. Se não, `process_question`.

### 2.6 Módulo de Busca (`src/search.py`)

#### 2.6.1 Lógica de Fallback de Robustez
Este é um diferencial funcional importante.
- **Função `search_with_sources`**:
  - Tenta: `chain.invoke(question)`
  - Except (Erro na LLM):
    - Captura exceção genérica.
    - Formata uma "Resposta de Fallback".
    - Mensagem: "⚠️ Aviso: O serviço de IA está instável... Abaixo estão os trechos mais relevantes:".
    - Anexa os textos dos chunks recuperados diretamente do retriever.
    - Isso garante que o usuário *nunca* fica sem resposta se a informação estiver no banco, mesmo que a IA (Google/OpenAI) esteja fora do ar.

#### 2.6.2 Timeout
- Utiliza `signal.SIGALRM` (Unix-only) para interromper chamadas que excedam `Config.SEARCH_TIMEOUT`.

---

## 3. Fluxos Funcionais Completos

Esta seção descreve a sequência exata de eventos para os casos de uso principais.

### 3.1 Fluxo F1: Ingestão de Novo Arquivo (Happy Path)
**Ator**: Usuário no Terminal.
**Pré-condição**: Banco acessível, PDF válido em `docs/manual_v1.pdf`.

1.  Usuário digita: `add docs/manual_v1.pdf`.
2.  `chat_loop` detecta comando `add`.
3.  `commands.handle_add_command` é invocado.
4.  O sistema verifica se o arquivo existe no disco. (Sim)
5.  O sistema cria repositório e chama `repo.source_exists('docs/manual_v1.pdf')`. (Retorna False)
6.  O sistema invoca `ingest.ingest_pdf('docs/manual_v1.pdf')`.
7.  `ingest_pdf`:
    - Carrega PDF (PyPDFLoader).
    - Divide em 150 chunks.
    - Gera metadados.
    - Exibe barra de progresso `tqdm` 0%..100% (Embeddings).
    - Salva no PGVector.
    - Calcula estatísticas.
8.  `ingest_pdf` retorna `True`.
9.  O sistema imprime mensagem de sucesso.
10. O sistema adiciona o comando `add docs/manual_v1.pdf` ao final do arquivo `.chat_history`.
11. Prompt `> ` reaparece.

### 3.2 Fluxo F2: Detecção e Tratamento de Duplicidade (Overlap)
**Ator**: Usuário.
**Pré-condição**: `docs/manual_v1.pdf` já foi ingerido anteriormente.

1.  Usuário digita: `add docs/manual_v1.pdf`.
2.  `commands.handle_add_command` verifica `repo.source_exists`. (Retorna True).
3.  Sistema exibe: `"⚠️ O arquivo 'docs/manual_v1.pdf' já existe na base de dados."`
4.  Sistema pergunta: `"Deseja sobrescrever os dados existentes? (sim/n): "`
5.  **Caminho A (Usuário digita 'n')**:
    - Sistema imprime: `"Operação cancelada pelo usuário."`
    - Retorna ao prompt. Nenhuma alteração no banco.
6.  **Caminho B (Usuário digita 'sim')**:
    - `ingest_pdf` é chamado.
    - Antes de inserir, executa `repo.delete_by_source(...)`.
    - Logs mostram: `"Removidos X chunks antigos..."`.
    - Novos chunks são inseridos.
    - Mensagem de sucesso.

### 3.3 Fluxo F3: Busca com Sucesso (RAG Standard)
**Ator**: Usuário.
**Pré-condição**: Banco populado, API Key válida.

1.  Usuário digita: `"Qual a data de validade do produto?"`
2.  `chat_loop` valida `check_database_status()` > 0.
3.  `process_question` inicia cronômetro.
4.  Sistema exibe: `"🔍 Recuperando informações relevantes..."`
5.  Retrieval busca Top-K (10) chunks via similaridade de cosseno.
6.  Sistema exibe: `"🧠 Gerando resposta baseada nos documentos..."`
7.  LLM recebe Prompt + Contexto + Pergunta.
8.  LLM retorna: `"A validade é de 5 anos."`
9.  Sistema calcula tempo delta (ex: 2.1s).
10. Sistema imprime resposta formatada.
11. Se flag `--verbose` estiver ativa:
    - Imprime linha separadora.
    - Imprime: `"📚 Fontes utilizadas:"`
    - Lista: `- manual_v1.pdf (pág 12)`
    - Imprime: `"⏱️ Tempo de execução: 2.10s"`

### 3.4 Fluxo F4: Erro de API e Fallback
**Ator**: Usuário.
**Pré-condição**: Banco populado, mas API OpenAI instável (Timeout/Error 500).

1.  Usuário digita pergunta.
2.  Retrieval funciona (banco local). 10 chunks recuperados.
3.  Chamada `llm.invoke` trava ou falha.
4.  Código captura `Exception`.
5.  Sistema exibe Output de Fallback:
    ```
    ⚠️ Aviso: O serviço de IA está instável ou indisponível no momento.
    
    Abaixo estão os trechos mais relevantes encontrados nos documentos:
    
    --- Trecho 1 (manual_v1.pdf - Pág 12) ---
    ...conteúdo do texto...
    
    --- Trecho 2 (manual_v1.pdf - Pág 13) ---
    ...conteúdo do texto...
    ```
6.  Usuário consegue ler a informação bruta.

### 3.5 Fluxo F5: Limpeza de Banco (`clear`)
1.  Usuário digita `clear`.
2.  Sistema pergunta: `"⚠️ CERTEZA que deseja limpar toda a base? (sim/n): "`
3.  Usuário confirma `sim`.
4.  `repo.clear()` executa `DELETE FROM ...`.
5.  Sistema confirma limpeza.
6.  Usuário digita uma pergunta.
7.  Sistema bloqueia e avisa: `"⚠️ O banco de dados está vazio!"`.

---

## 4. Guia de Referência da Interface CLI

### 4.1 Comandos de Terminal (`src/chat.py` argumentos)

| Argumento Completo | Abrev. | Tipo | Obrig? | Descrição Detalhada |
| :--- | :--- | :--- | :--- | :--- |
| `--file PATH` | `-f` | Path | Não | Executa ingestão deste arquivo antes de abrir o prompt. Útil para "Load & Chat" rápido. |
| `--provider NAME` | - | Enum | Não | Valores: `google` ou `openai`. Força o uso de uma API específica, ignorando a ordem padrão de detecção. |
| `--quiet` | `-q` | Flag | Não | Ativa **Modo Silencioso**. Suprime banner de boas-vindas, barras de progresso, logs de INFO e mensagens de status intermediárias ("Recuperando..."). Ideal para automação ou usuários experientes. |
| `--verbose` | `-v` | Flag | Não | Ativa **Modo Detalhado**. Exibe metadados das fontes (arquivo/página) e tempo de resposta ao final de cada interação. |
| `--top-k INT` | - | Int | Não | Substitui o valor `TOP_K` do `.env`. Define quantos fragmentos de documento são enviados para a LLM. Valor alto = mais contexto, maior custo, maior risco de alucinação ou estouro de janela. |
| `--temperature FLOAT` | - | Float | Não | Substitui `RETRIEVAL_TEMPERATURE`. 0.0 é determinístico (melhor para RAG). 1.0 é criativo. |
| `--search-timeout INT` | - | Int | Não | Define timeout em segundos para a operação completa de busca. |
| `--prompt-template PATH`| - | Path | Não | Caminho para um arquivo `.txt` contendo um template Jinja2 customizado para o prompt. Deve conter as variáveis `{contexto}` e `{pergunta}`. |

### 4.2 Comandos Interativos (REPL)

Estes comandos são digitados dentro do chat (`> `). Eles não diferenciam maiúsculas/minúsculas.

| Comando | Aliases | Argumentos | Ação | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| `add` | `ingest`, `a` | `<path>` | Inicia fluxo de ingestão de PDF. | `a docs/manual.pdf` |
| `remove` | `delete`, `r`| `<nome>` | Remove arquivos por nome (exato ou parcial). | `r manual.pdf` |
| `stats` | `s` | - | Exibe total de chunks e lista de arquivos. | `s` |
| `clear` | `c` | - | Limpa todo o banco de vetores (Requer confirmação). | `c` |
| `history` | `hist` | - | Lista os últimos N comandos da sessão e anteriores. | `hist` |
| `!N` | - | - | Executa novamente o comando de índice N do histórico. | `!5` |
| `help` | `h`, `?` | - | Exibe o menu de ajuda. | `?` |
| `sair` | `exit`, `q` | - | Sai do programa. Salva histórico pendente. | `q` |

---

## 5. Configuração e Variáveis de Ambiente

O arquivo `.env` deve estar na raiz do projeto.

### 5.1 Tabela de Variáveis

| Variável | Obrigatória? | Tipo | Descrição Técnica | Exemplo |
| :--- | :--- | :--- | :--- | :--- |
| **Infraestrutura** | | | | |
| `DATABASE_URL` | **SIM** | URI | URL de conexão PostgreSQL (deve incluir driver `postgresql://` ou `postgresql+psycopg://`). | `postgresql://user:pass@localhost:5432/rag` |
| `PG_VECTOR_COLLECTION_NAME` | **SIM** | Str | Nome usado na coluna `name` da tabela `langchain_pg_collection`. | `documentos_v1` |
| **Provedores de IA** | | | | |
| `GOOGLE_API_KEY` | *Condicional* | Str | Chave de API Google AI Studio. Obrigatória se OpenAI não for usada. | `AIzaSy...` |
| `OPENAI_API_KEY` | *Condicional* | Str | Chave de API OpenAI. Obrigatória se Google não for usado. | `sk-proj-...` |
| **Modelos (Google)** | | | | |
| `GOOGLE_EMBEDDING_MODEL` | Não | Str | ID do modelo de embeddings. Código usa default hardcoded se vazio. | `models/text-embedding-004` |
| `GOOGLE_LLM_MODEL` | Não | Str | ID do modelo generativo. | `gemini-2.5-flash-lite` |
| **Modelos (OpenAI)** | | | | |
| `OPENAI_EMBEDDING_MODEL` | Não | Str | ID do modelo de embeddings. | `text-embedding-3-small` |
| `OPENAI_LLM_MODEL` | Não | Str | ID do modelo generativo. | `gpt-4o-mini` |
| **Parâmetros de Tuning** | | | | |
| `CHUNK_SIZE` | Não | Int | Tamanho dos blocos de texto. Afeta a granularidade da busca. | `1000` |
| `CHUNK_OVERLAP` | Não | Int | Quantidade de repetição entre blocos para preservar contexto. | `150` |
| `TOP_K` | Não | Int | Quantidade de blocos recuperados do banco. | `10` |
| `SEARCH_TIMEOUT` | Não | Int | Tempo limite para timeout. | `30` |

---

## 6. Estados e Mensagens do Sistema

### 6.1 Banco de Dados Indisponível (Critical Failure)
- **Sintoma**: `DATABASE_URL` incorreta ou serviço Docker parado.
- **Log**: `OperationalError: connection to server at "localhost" ... failed`.
- **Comportamento UI**: Comandos `stats`, `add`, `search` falham. O sistema pode abrir, mas exibirá erros ao tentar manipular dados. As funções de contagem retornam `0` silenciosamente em alguns casos (ver `src/database.py:count`).

### 6.2 Banco Inicializado mas Vazio (Cold Start)
- **Sintoma**: Tabelas criadas, mas nenhum PDF ingerido.
- **Comportamento UI**:
  - Banner de boas-vindas mostra: `⚠️ Status: Banco de dados vazio`.
  - Perguntas são bloqueadas com mensagem: `💡 Adicione um PDF primeiro`.

### 6.3 Conflito de Arquivos (File Collision)
- **Cenário**: Tentar ingerir `relatorio.pdf` duas vezes.
- **Detecção**: O sistema usa o metadado `source`. Se o caminho normalizado for idêntico, considera conflito.
- **Comportamento**: Prompt interativo de confirmação.

---

## 7. Limitações Técnicas e Conhecidas

### 7.1 Processamento de PDF
- **Limitação**: O uso de `PyPDFLoader` (baseado em `pypdf`) pode ter dificuldades com layouts complexos (colunas múltiplas, tabelas) resultando em ordem de leitura incorreta ou junção de textos de células vizinhas.
- **Impacto**: A qualidade da resposta RAG depende diretamente da qualidade da extração de texto.

### 7.2 Embeddings Estáticos
- **Limitação**: Se o modelo de embeddings for alterado no `.env` (ex: trocar de Google para OpenAI), os vetores já persistidos no banco tornam-se incompatíveis (dimensões ou espaço semântico diferentes).
- **Ação Necessária**: O usuário deve executar `clear` e re-ingerir todos os documentos ao trocar de modelo de embeddings. O sistema **não** detecta essa incompatibilidade automaticamente, o que resultará em erros de dimensão do PostgreSQL ou resultados de busca sem sentido.

### 7.3 Singletons de Conexão
- **Design**: `EmbeddingsManager` e `LLMManager` são singletons.
- **Impacto**: Alterações nas variáveis de ambiente *durante* a execução não têm efeito a menos que se force um reset (como a flag `--provider` faz).

### 7.4 Timeout em Windows
- **Limitação**: O uso de `signal.SIGALRM` para implementar timeouts funciona apenas em ambientes Unix (Linux/macOS).
- **Impacto**: No Windows, a flag `--search-timeout` será ignorada ou causará erro se não houver tratamento de plataforma (o código atual não possui verificação `if sys.platform == 'win32'`).

---

**Fim da Especificação Funcional**
