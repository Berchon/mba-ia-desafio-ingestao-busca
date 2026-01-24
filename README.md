# 🤖 Sistema RAG - Ingestão e Busca Semântica com LangChain

![GitHub release](https://img.shields.io/github/v/release/Berchon/mba-ia-desafio-ingestao-busca)

Sistema de Recuperação e Geração Aumentada (RAG) que permite fazer perguntas sobre documentos PDF usando busca semântica e LLMs.

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Funciona](#-como-funciona)
- [Comandos Disponíveis](#-comandos-disponíveis)
- [Troubleshooting](#-troubleshooting)

## 🎯 Sobre o Projeto

Este sistema permite:

1. **Ingestão de PDFs**: Carrega documentos PDF, divide em chunks e armazena embeddings em banco vetorial
2. **Busca Semântica**: Realiza buscas semânticas usando similaridade de vetores
3. **Respostas Contextualizadas**: Usa LLMs para gerar respostas baseadas apenas no conteúdo dos documentos
4. **Interface CLI**: Interação via linha de comando com comandos especiais

### Características Principais

- ✅ Barra de progresso visual durante a ingestão (`tqdm`)
- ✅ Sistema de IDs determinísticos baseados em arquivo
- ✅ Confirmação de segurança antes de sobrescrever documentos
- ✅ Exibição de estatísticas detalhadas pós-ingestão
- ✅ Amostragem de fontes (arquivo e página) nas respostas da IA
- ✅ Interface CLI interativa com comandos especiais (`add`, `clear`, `help`)
- ✅ Suporte completo a Google Gemini e OpenAI com abstração de provedor
- ✅ Banco de dados vetorial PostgreSQL com pgVector via Repository Pattern

## 🛠 Tecnologias Utilizadas

### Core
- **Python 3.x**: Linguagem principal
- **LangChain**: Framework para aplicações com LLMs
- **PostgreSQL + pgVector**: Banco de dados vetorial

### Bibliotecas Principais
- `langchain-google-genai`: Integração com Google Gemini
- `langchain-openai`: Integração com OpenAI
- `langchain-postgres`: Integração com PGVector
- `pypdf`: Leitura de arquivos PDF
- `python-dotenv`: Gerenciamento de variáveis de ambiente
- `psycopg`: Driver PostgreSQL

### Infraestrutura
- **Docker & Docker Compose**: Containerização do banco de dados
- **pgVector**: Extensão PostgreSQL para busca vetorial

## 📦 Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose
- Chave de API do Google Gemini OU OpenAI

### Obter Chaves de API

**Google Gemini:**
1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crie uma nova API Key
3. Copie a chave gerada

**OpenAI (opcional):**
1. Acesse [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crie uma nova API Key
3. Copie a chave gerada

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd mba-ia-desafio-ingestao-busca
```

### 2. Crie o Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Suba o Banco de Dados

O projeto usa Docker Compose para gerenciar o PostgreSQL com pgVector:

```bash
docker compose up -d
```

**O que este comando faz:**
- Cria um container PostgreSQL com a extensão pgVector habilitada
- Expõe a porta 5432 para conexões
- Cria um volume persistente para os dados
- Configura health checks automáticos
- Inicializa a extensão vector automaticamente

**Verificar se está rodando:**
```bash
docker compose ps
```

**Parar o banco:**
```bash
docker compose down
```

**Parar e remover dados:**
```bash
docker compose down -v
```

## ⚙️ Configuração

### 1. Crie o Arquivo `.env`

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

### 2. Configure as Variáveis de Ambiente

Edite o arquivo `.env` com suas configurações:

```bash
# === API Keys (configure pelo menos uma) ===

# Google Gemini (recomendado)
GOOGLE_API_KEY=sua_chave_google_aqui
GOOGLE_EMBEDDING_MODEL='models/embedding-001'
GOOGLE_LLM_MODEL='gemini-2.5-flash-lite'

# OpenAI (opcional)
OPENAI_API_KEY=sua_chave_openai_aqui
OPENAI_EMBEDDING_MODEL='text-embedding-3-small'
OPENAI_LLM_MODEL='gpt-4o-mini'

# === Configuração do Banco de Dados ===
DATABASE_URL='postgresql://postgres:postgres@localhost:5432/rag'
PG_VECTOR_COLLECTION_NAME='pdf_embeddings'

# === Configuração de Documentos ===
PDF_PATH=document.pdf
```

### Descrição das Variáveis

#### API Keys
- **GOOGLE_API_KEY**: Chave de API do Google Gemini (obtenha em https://aistudio.google.com)
- **GOOGLE_EMBEDDING_MODEL**: Modelo de embeddings do Google (padrão: `models/embedding-001`)
- **GOOGLE_LLM_MODEL**: Modelo de LLM do Google (padrão: `gemini-2.5-flash-lite`)
- **OPENAI_API_KEY**: Chave de API da OpenAI (opcional, obtenha em https://platform.openai.com)
- **OPENAI_EMBEDDING_MODEL**: Modelo de embeddings da OpenAI (padrão: `text-embedding-3-small`)
- **OPENAI_LLM_MODEL**: Modelo de LLM da OpenAI (padrão: `gpt-4o-mini`)

> **Nota**: O sistema detecta automaticamente qual provedor usar baseado nas chaves configuradas. Se ambas estiverem configuradas, o Google Gemini terá prioridade.

#### Banco de Dados
- **DATABASE_URL**: URL de conexão com PostgreSQL
  - Formato: `postgresql://usuario:senha@host:porta/database`
  - Para desenvolvimento local com Docker Compose: `postgresql://postgres:postgres@localhost:5432/rag`
  - **Nota de Segurança**: As credenciais `postgres:postgres` são as padrão do `docker-compose.yml` fornecido. Para ambientes de produção, altere usuário e senha tanto no `docker-compose.yml` quanto no `.env`
- **PG_VECTOR_COLLECTION_NAME**: Nome da coleção/tabela no banco vetorial (padrão: `pdf_embeddings`)

#### Documentos
- **PDF_PATH**: Caminho para o arquivo PDF padrão a ser ingerido (padrão: `document.pdf`)

## 💻 Uso

### Fluxo Completo de Uso

#### 1. Ingerir um Documento PDF

**Importante**: Certifique-se de que a variável `PDF_PATH` está configurada no arquivo `.env` apontando para o PDF que deseja ingerir.

```bash
python src/ingest.py
```

**O que acontece:**
- Carrega o PDF especificado em `PDF_PATH` (ou `document.pdf` por padrão)
- Divide o texto em chunks de 1000 caracteres com overlap de 150
- Gera embeddings para cada chunk
- Armazena os vetores no PostgreSQL com pgVector
- Exibe progresso e estatísticas

**Exemplo de saída:**
```
INFO - Iniciando ingestão do PDF: document.pdf
INFO - PDF carregado: 34 páginas
INFO - Texto dividido em 67 chunks
INFO - Gerando embeddings e armazenando no banco de dados...
INFO - ✓ Ingestão concluída com sucesso!
INFO - Total de documentos no banco: 67
```

#### 2. Iniciar o Chat Interativo

```bash
python src/chat.py
```

**Exemplo de interação:**
```
=== Sistema RAG - Chat Interativo ===
✓ Banco de dados conectado e populado
✓ Sistema pronto para responder perguntas

Digite 'help' para ver comandos disponíveis ou 'sair' para encerrar.

Faça sua pergunta:
> Qual o faturamento da empresa SuperTechIABrazil?

🔍 Buscando informações...
💡 Gerando resposta...

RESPOSTA:
O faturamento da empresa SuperTechIABrazil foi de 10 milhões de reais.

FONTES:
- document.pdf (pág 26)
- document.pdf (pág 2)

---
Faça sua pergunta:
> sair

👋 Até logo! Chat encerrado.
```

#### 3. Ingerir PDF via CLI

Você também pode ingerir um PDF específico diretamente pelo chat:

```bash
python src/chat.py -file caminho/para/documento.pdf
```

Ou durante o chat:
```
Faça sua pergunta:
> add novo_documento.pdf

📄 Iniciando ingestão de: novo_documento.pdf
✓ Ingestão concluída!
```

## 📁 Estrutura do Projeto

```
mba-ia-desafio-ingestao-busca/
├── .agent/
│   └── workflows/
│       └── development-workflow.md    # Workflow de desenvolvimento
├── src/
│   ├── chat.py                        # CLI de interação
│   ├── config.py                      # Configuração centralizada
│   ├── database.py                    # Conexão com PGVector
│   ├── embeddings_manager.py          # Singleton Manager de Embeddings
│   ├── ingest.py                      # Script de ingestão
│   ├── llm_manager.py                 # Singleton Manager de LLM
│   ├── logger.py                      # Sistema de logging centralizado
│   └── search.py                      # Módulo de busca semântica
├── .env                               # Variáveis de ambiente (não versionado)
├── .env.example                       # Template de configuração
├── .gitignore                         # Arquivos ignorados pelo Git
├── CHANGELOG.md                       # Histórico de mudanças
├── docker-compose.yml                 # Configuração do PostgreSQL
├── document.pdf                       # PDF de exemplo
├── README.md                          # Este arquivo
├── requirements.txt                   # Dependências Python
├── requisitos.md                      # Requisitos do projeto
└── TODOs.md                           # Checklist de melhorias
```

## 🔍 Como Funciona

### 1. Ingestão (ingest.py)

```
PDF → Carregamento → Chunking → Embeddings → PGVector
```

1. **Carregamento**: `PyPDFLoader` extrai texto do PDF
2. **Chunking**: `RecursiveCharacterTextSplitter` divide em chunks de 1000 caracteres (overlap 150)
3. **Embeddings**: Modelo de embeddings converte texto em vetores
4. **Armazenamento**: Vetores salvos no PostgreSQL com pgVector

### 2. Busca (search.py)

```
Pergunta → Embedding → Busca Vetorial → Top 10 → Contexto → LLM → Resposta
```

1. **Vetorização**: Pergunta convertida em embedding
2. **Busca**: Similarity search retorna 10 chunks mais relevantes (k=10)
3. **Contexto**: Chunks concatenados formam o contexto
4. **Prompt**: Template com contexto + regras + pergunta
5. **LLM**: Modelo gera resposta baseada apenas no contexto

### 3. Prompt Template

O sistema usa um prompt rigoroso para evitar alucinações:

```
CONTEXTO:
{chunks recuperados do banco}

REGRAS:
- Responda somente com base no CONTEXTO
- Se a informação não estiver no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo

PERGUNTA DO USUÁRIO:
{pergunta}
```

## 🎮 Comandos Disponíveis

No chat interativo, você pode usar:

| Comando | Descrição |
|---------|-----------|
| `help` | Exibe lista de comandos disponíveis |
| `add <caminho>` ou `ingest <caminho>` | Ingere um novo PDF |
| `sair`, `exit`, `quit`, `q` | Encerra o chat |

## 🐛 Troubleshooting

### Erro: "Database connection failed"

**Problema**: Não consegue conectar ao PostgreSQL

**Soluções**:
1. Verifique se o Docker está rodando: `docker compose ps`
2. Suba o banco: `docker compose up -d`
3. Verifique a `DATABASE_URL` no `.env`
4. Teste a conexão: `docker exec -it postgres_rag psql -U postgres -d rag`

### Erro: "API key not found"

**Problema**: Chave de API não configurada

**Soluções**:
1. Verifique se o arquivo `.env` existe
2. Confirme que `GOOGLE_API_KEY` ou `OPENAI_API_KEY` está preenchida
3. Não use aspas ao redor da chave no `.env`

### Erro: "No documents in database"

**Problema**: Banco de dados vazio

**Soluções**:
1. Execute a ingestão: `python src/ingest.py`
2. Ou use o comando `add` no chat: `add document.pdf`

### Erro: "PDF not found"

**Problema**: Arquivo PDF não encontrado

**Soluções**:
1. Verifique se o arquivo existe no caminho especificado
2. Use caminho absoluto ou relativo correto
3. Atualize `PDF_PATH` no `.env` se necessário

### Performance lenta

**Problema**: Respostas demoram muito

**Soluções**:
1. Use modelos mais rápidos (ex: `gemini-2.5-flash-lite`)
2. Reduza o valor de `k` (número de chunks recuperados)
3. Verifique sua conexão com a internet

## 📝 Próximos Passos

Consulte o arquivo [TODOs.md](TODOs.md) para ver as melhorias planejadas, incluindo:

- **Fase E: Melhorias Técnicas do Chat** (Argumentos CLI padrão, tratamento de banco vazio)
- **Fase F: Comandos Estendidos** (Comandos `stats` e `remove <arquivo>`)
- **Fase G: Melhorias de UX** (Simplificação de prompt, atalhos de comando)
- **Fase K: Refatorações Avançadas** (Histórico de conversas, cache de embeddings)

## 🤖 Desenvolvido com Antigravity

Este projeto foi inteiramente desenvolvido utilizando o **Antigravity**, o assistente de IA da Google para desenvolvimento de código. A escolha de usar o Antigravity como ferramenta principal teve como objetivo:

- **Aprendizado Prático**: Explorar as capacidades de um agente de IA moderno no desenvolvimento de software completo
- **Produtividade**: Acelerar o desenvolvimento mantendo qualidade e boas práticas
- **Experimentação**: Testar os limites da colaboração humano-IA em projetos reais
- **Documentação**: Criar um caso de uso real e bem documentado do uso de IA no desenvolvimento

Todo o código, desde a arquitetura inicial até a implementação de features, refatorações e esta documentação, foi criado em colaboração com o Antigravity. Este projeto serve como exemplo prático de como ferramentas de IA podem auxiliar no desenvolvimento de aplicações complexas envolvendo LLMs, bancos vetoriais e processamento de documentos.

## 📄 Licença

Este projeto foi desenvolvido como parte do MBA em Inteligência Artificial da Full Cycle.

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga o workflow definido em `.agent/workflows/development-workflow.md`.

---

**Desenvolvido com ❤️ usando LangChain e Google Gemini**