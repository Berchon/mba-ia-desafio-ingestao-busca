# 🤖 Sistema RAG - Ingestão e Busca Semântica

![GitHub release](https://img.shields.io/github/v/release/Berchon/mba-ia-desafio-ingestao-busca)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MBA--IA-green)

Sistema profissional de **Retrieval-Augmented Generation (RAG)** desenvolvido como desafio técnico para o MBA em IA da Full Cycle. O software permite a ingestão inteligente de documentos PDF em um banco de dados vetorial e a realização de consultas em linguagem natural via terminal.

---

## 📋 Índice

- [🎯 Objetivo do Projeto](#-objetivo-do-projeto)
- [🛠 Tecnologias Obrigatórias](#-tecnologias-obrigatórias)
- [🚀 Guia de Início Rápido](#-guia-de-início-rápido)
  - [1. Clonar o Projeto](#1-clonar-o-projeto)
  - [2. Ambiente Virtual](#2-ambiente-virtual)
  - [3. Instalação de Dependências](#3-instalação-de-dependências)
  - [4. Configuração do Ambiente (.env)](#4-configuração-do-ambiente-env)
  - [5. Infraestrutura (Docker)](#5-infraestrutura-docker)
- [💻 Ordem de Execução](#-ordem-de-execução)
  - [Passo 1: Ingestão do PDF](#passo-1-ingestão-do-pdf)
  - [Passo 2: Chat Interativo](#passo-2-chat-interativo)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [⚙️ Configurações Avançadas](#-configurações-avançadas)
- [🔍 Detalhes Técnicos](#-detalhes-técnicos)
- [🎮 Comandos do Chat](#-comandos-do-chat)

---

## 🎯 Objetivo do Projeto

O sistema é capaz de processar documentos PDF, dividi-los em fragmentos (chunks), gerar representações vetoriais (embeddings) e armazená-los em um banco de dados **PostgreSQL** com a extensão **pgVector**. O usuário interage via CLI, recebendo respostas baseadas **estritamente** no contexto dos documentos fornecidos, evitando alucinações.

---

## 🛠 Tecnologias Obrigatórias

Conforme os requisitos do projeto, as seguintes tecnologias são fundamentais:

- **Linguagem**: Python 3.10+
- **Framework**: LangChain
- **Banco de Dados**: PostgreSQL + pgVector
- **Infraestrutura**: Docker & Docker Compose
- **Modelos de IA**:
  - **Google Gemini**: `models/embedding-001` e `gemini-2.5-flash-lite`
  - **OpenAI**: `text-embedding-3-small` e `gpt-5-nano` (configurável)

---

## 🚀 Guia de Início Rápido

Siga os passos abaixo para configurar o sistema em seu ambiente local do zero.

### 1. Clonar o Projeto

Primeiro, faça o download do código-fonte para sua máquina:

```bash
git clone https://github.com/Berchon/mba-ia-desafio-ingestao-busca.git
cd mba-ia-desafio-ingestao-busca
```

### 2. Ambiente Virtual

Crie e ative um ambiente virtual para isolar as dependências do projeto:

```bash
# Criar o ambiente
python3 -m venv venv

# Ativar (Linux/macOS)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

### 3. Instalação de Dependências

Instale todos os pacotes necessários:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configuração do Ambiente (.env)

O sistema utiliza um arquivo `.env` para carregar chaves de API e configurações de banco de dados.

1.  Crie o arquivo `.env` a partir do template:
    ```bash
    cp .env.example .env
    ```
2.  Abra o arquivo `.env` e insira sua **API Key** (Google ou OpenAI):

```env
# Exemplo de configuração mínima
GOOGLE_API_KEY='sua-chave-aqui'
DATABASE_URL='postgresql://postgres:postgres@localhost:5432/rag'
PG_VECTOR_COLLECTION_NAME='documentos'
```

### 5. Infraestrutura (Docker)

Suba o container do banco de dados PostgreSQL com suporte a vetores:

```bash
docker compose up -d
```

> **Dica**: Utilize `docker compose ps` para garantir que o container está saudável.

---

## 💻 Ordem de Execução

Após a configuração do ambiente, siga esta ordem para rodar o sistema:

### Passo 1: Ingestão do PDF

O sistema processará o arquivo `document.pdf` (ou o que estiver configurado no `.env`). O texto será dividido em **chunks de 1000 caracteres** com **overlap de 150**.

```bash
python src/ingest.py
```

**O que o script faz?**
- Lê o PDF e divide em blocos de texto.
- Gera os embeddings vetoriais.
- Salva tudo no PGVector.
- Exibe estatísticas (páginas, chunks, tempo).

### Passo 2: Chat Interativo

Inicie o terminal de chat para fazer perguntas sobre o conteúdo do PDF:

```bash
python src/chat.py
```

**Exemplo de interação:**
```bash
> Qual o faturamento da Empresa SuperTechIABrazil?
🔍 Recuperando informações...
🧠 Gerando melhor resposta...

RESPOSTA: O faturamento foi de 10 milhões de reais.
```

---

## 📂 Estrutura do Projeto

O projeto segue a estrutura obrigatória e organizada para escalabilidade:

```text
├── src/
│   ├── chat.py           # CLI principal de interação
│   ├── ingest.py         # Script ETL (Extração, Transformação, Carga)
│   ├── search.py         # Lógica de busca e chain RAG
│   ├── database.py       # Gerenciamento de conexão e repositório
│   ├── config.py         # Centralização de variáveis de ambiente
│   ├── cli/              # Módulos auxiliares da interface CLI
│   └── *_manager.py      # Gestores de Singletons (LLM/Embeddings)
├── docs/                 # Documentação (PRD, Spec, Requisitos)
├── prompts/              # Templates de prompt customizáveis
├── tests/                # Suite de testes E2E completa
├── docker-compose.yml    # Configuração do banco vetorial
├── requirements.txt      # Lista de dependências
├── .env.example          # Template de ambiente
└── document.pdf          # PDF padrão para teste
```

---

## ⚙️ Configurações Avançadas

Você pode customizar o comportamento do sistema via flags de linha de comando:

- **Mudar Provedor**: `python src/chat.py --provider openai`
- **Modo Silencioso**: `python src/chat.py --quiet`
- **Modo Verboso (Fontes)**: `python src/chat.py --verbose`
- **Customizar Parâmetros**: `python src/chat.py --top-k 5 --temperature 0.2`

---

## 🔍 Detalhes Técnicos

### Estratégia de RAG
- **Recuperação**: Busca por similaridade de cosseno buscando os **10 resultados mais relevantes (k=10)**.
- **Robustez**: Caso a LLM falhe, o sistema possui um **fallback** que exibe os trechos de texto brutos recuperados do banco.
- **Determinismo**: IDs de chunks baseados no nome do arquivo para evitar duplicidade em re-ingestões.

### Prompt de Segurança
O prompt utilizado (conforme `requisitos.md`) proíbe o uso de conhecimento externo, garantindo que a resposta venha **estritamente do CONTEXTO**.

---

## 🎮 Comandos do Chat

Dentro do ambiente interativo, você pode usar os seguintes comandos:

| Comando | Atalho | Ação |
| :--- | :--- | :--- |
| `help` | `h` | Exibe o menu de ajuda |
| `add <path>` | `a` | Adiciona um novo PDF à base |
| `stats` | `s` | Mostra estatísticas do banco de dados |
| `remove <nome>` | `r` | Remove um documento específico da base |
| `clear` | `c` | Limpa toda a base de dados vetorial |
| `history` | `hist` | Mostra o histórico de comandos digitados |
| `sair` | `q` | Encerra a aplicação graciosamente |

---

**Desenvolvido como projeto educacional por [Berchon]**  
*MBA em IA para Desenvolvedores - Full Cycle*