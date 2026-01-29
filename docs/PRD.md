# Product Requirements Document (PRD)
## Sistema RAG - Evolução v0.6.0

**Versão do PRD:** 2.0  
**Data:** 2026-01-29  
**Baseado em:** Functional Specification As-Is v2.0 (Estado Atual: v0.5.0)  
**Objetivo:** Definir requisitos para a próxima evolução do sistema

---

## 1. Visão do Produto

### 1.1 Problema que o Produto Resolve

O sistema RAG atual é uma solução CLI robusta e profissional para consulta semântica de documentos PDF. Após múltiplas iterações de desenvolvimento, o sistema evoluiu significativamente além dos requisitos mínimos, incorporando funcionalidades de nível empresarial como:

- ✅ Suporte multi-provedor (Google Gemini e OpenAI)
- ✅ Sistema de fallback robusto para falhas de LLM
- ✅ Templates de prompt customizáveis
- ✅ Histórico de comandos com navegação persistente
- ✅ Timeouts configuráveis
- ✅ Suite completa de testes E2E (88 casos de teste)

No entanto, ainda existem limitações que impactam casos de uso avançados:

1. **Falta de Contexto Conversacional**: Cada pergunta é isolada, impedindo diálogos naturais com perguntas de follow-up que referenciam conversas anteriores
2. **Limitação de Formatos**: Suporte apenas a PDFs restringe casos de uso comuns (DOCX, TXT, Markdown, HTML)
3. **Observabilidade Limitada**: Logs básicos dificultam análise de performance e troubleshooting em ambientes de produção
4. **Performance Subótima**: Embeddings são recalculados para perguntas repetidas, gerando custos e latência desnecessários
5. **Interface CLI Única**: Ausência de API REST limita integração com outras aplicações

### 1.2 Público-Alvo

- **Usuários Finais**: Profissionais que precisam consultar documentos regularmente (pesquisadores, analistas, consultores, advogados)
- **Desenvolvedores**: Equipes que integram busca semântica em aplicações corporativas
- **Operadores**: Usuários técnicos que gerenciam e monitoram o sistema em produção
- **Integradores**: Desenvolvedores que precisam consumir o sistema via API REST

### 1.3 Objetivo da Próxima Fase

Transformar o sistema de uma ferramenta CLI profissional para uma **plataforma de busca semântica enterprise-ready**, através de:

1. **Histórico Conversacional**: Permitir diálogos contextuais com memória de conversas anteriores
2. **Suporte a Múltiplos Formatos**: Expandir para DOCX, TXT, Markdown, HTML além de PDF
3. **Observabilidade Profissional**: Logs estruturados (JSON), métricas de performance, rastreamento distribuído
4. **Cache Inteligente**: Reduzir latência e custos através de cache de embeddings
5. **API REST**: Expor funcionalidades via HTTP para integração com outras aplicações

**Meta de Versão**: v0.6.0 (Minor release - novas funcionalidades compatíveis)

---

## 2. Contexto Atual (Resumo)

### 2.1 Principais Capacidades Existentes

✅ **Ingestão Robusta de PDFs**
- Carregamento, chunking (1000 chars, overlap 150)
- Geração de embeddings com suporte multi-provedor
- Armazenamento em PGVector com IDs determinísticos
- Limpeza automática de dados antigos antes de re-ingestão
- Confirmação de sobrescrita para evitar perda acidental de dados
- Barra de progresso visual e estatísticas pós-ingestão

✅ **Busca Semântica Avançada**
- Similarity search (top-k configurável)
- Geração de respostas via LLM com template customizável
- Sistema de fallback robusto (retorna chunks se LLM falhar)
- Timeout configurável para evitar travamentos
- Retorno de fontes utilizadas (metadados)

✅ **Interface CLI Profissional**
- Chat interativo com comandos avançados (add, remove, clear, stats, help, history)
- Histórico de comandos com navegação por setas (↑/↓) e persistência entre sessões
- Modos de operação: quiet, verbose
- Atalhos de comandos (h, a, c, s, r)
- Indicadores de progresso visual
- Tratamento robusto de erros

✅ **Suporte Multi-Provedor**
- Google Gemini e OpenAI com detecção automática
- Troca dinâmica via flag `--provider`
- Validação estrita de API keys

✅ **Gerenciamento de Documentos**
- Remoção por arquivo específico
- Limpeza total da base
- Estatísticas detalhadas (total de chunks, arquivos únicos, lista de fontes)

✅ **Configurabilidade Avançada**
- Parâmetros configuráveis via CLI: chunk-size, chunk-overlap, top-k, temperature, search-timeout
- Templates de prompt customizáveis via arquivo externo
- Configuração centralizada em `Config` class

✅ **Qualidade de Código**
- Type hints completos
- Docstrings detalhadas (Args/Returns/Raises/Examples)
- Arquitetura modular (padrão Repository, Singleton)
- Tratamento específico de exceções (SQLAlchemyError, IOError, etc.)
- Suite completa de testes E2E (88 casos de teste, 14 fases)

### 2.2 Principais Limitações Atuais

❌ **Sem Histórico Conversacional**: Cada pergunta é independente, não há memória de diálogos anteriores  
❌ **Apenas PDFs**: Não suporta DOCX, TXT, Markdown, HTML  
❌ **Observabilidade Básica**: Logs não estruturados, sem métricas de performance, sem rastreamento distribuído  
❌ **Sem Cache de Embeddings**: Recalcula embeddings para perguntas idênticas  
❌ **Apenas CLI**: Não há API REST para integração com outras aplicações  
❌ **Sem Busca Híbrida**: Apenas busca semântica (sem busca por palavras-chave/BM25)  
❌ **Sem Persistência de Conversas**: Histórico de comandos é persistido, mas não o contexto conversacional  
❌ **Sem Multi-tenancy**: Sistema assume coleção única, sem suporte a workspaces/namespaces  

---

## 3. Objetivos do PRD

### 3.1 O que se Pretende Melhorar

#### 3.1.1 Experiência do Usuário
- Permitir diálogos contextuais com histórico conversacional (memória de perguntas e respostas anteriores)
- Reduzir latência de respostas através de cache inteligente de embeddings
- Expandir formatos de documento suportados (DOCX, TXT, MD, HTML)
- Fornecer API REST para integração com outras aplicações

#### 3.1.2 Observabilidade e Monitoramento
- Logs estruturados em formato JSON para análise automatizada
- Métricas de performance (latência, throughput, cache hit rate)
- Rastreamento distribuído com request IDs
- Dashboard de métricas (opcional, via Prometheus/Grafana)

#### 3.1.3 Performance e Custos
- Cache de embeddings para reduzir chamadas de API (até 50% de redução de custos)
- Otimização de operações repetidas
- Monitoramento de custos de API

#### 3.1.4 Integrabilidade
- API REST para consumo por outras aplicações
- Documentação OpenAPI/Swagger
- Suporte a autenticação básica (API keys)

### 3.2 O que NÃO é Objetivo deste Ciclo

❌ **Interface Web Completa**: Apenas API REST, sem frontend (pode ser v0.7.0)  
❌ **Autenticação Avançada**: Apenas API keys básicas, sem OAuth/SAML (pode ser v0.7.0)  
❌ **Múltiplas Coleções/Workspaces**: Sistema continua com coleção única (pode ser v0.7.0)  
❌ **Busca Híbrida**: Apenas busca semântica, sem BM25/keyword search (pode ser v0.8.0)  
❌ **OCR para PDFs Escaneados**: Apenas PDFs com texto nativo (pode ser v0.8.0)  
❌ **Suporte a Imagens**: Apenas texto extraído de documentos (pode ser v0.9.0)  
❌ **Persistência de Conversas**: Histórico conversacional apenas em memória (pode ser v0.7.0)  
❌ **Modo Append na Ingestão**: Manter comportamento de substituição (pode ser v0.7.0)  
❌ **Validação de Duplicatas**: Detecção de chunks duplicados fica para futuro  

---

## 4. Requisitos Funcionais

### 4.1 RF-001: Histórico Conversacional (Chat Memory)

#### Descrição
O sistema deve manter contexto de perguntas e respostas anteriores durante uma sessão de chat, permitindo perguntas de follow-up que referenciam conversas anteriores.

#### Justificativa
- **Problema**: Usuários precisam reformular perguntas de forma autossuficiente, impedindo diálogos naturais
- **Impacto**: Melhora significativamente a experiência do usuário, permitindo conversas mais naturais e produtivas
- **Valor**: Alto - feature mais solicitada e de maior impacto na UX

#### Fluxo Esperado

**Cenário 1: Pergunta de Follow-up**
1. Usuário pergunta: "Qual o faturamento da empresa X?"
2. Sistema responde: "O faturamento foi de 10 milhões de reais"
3. Usuário pergunta: "E qual foi o crescimento em relação ao ano anterior?"
4. Sistema usa contexto da pergunta anterior para entender "ano anterior" e "crescimento"
5. Sistema responde com base no contexto acumulado

**Cenário 2: Referência a Resposta Anterior**
1. Usuário pergunta: "Quais são os principais produtos?"
2. Sistema lista produtos A, B, C
3. Usuário pergunta: "Quantos clientes tem o produto A?"
4. Sistema entende que "produto A" refere-se à resposta anterior

**Cenário 3: Limpeza de Histórico**
1. Usuário usa comando `clear-history` ou `reset-context`
2. Sistema limpa contexto conversacional (mantém histórico de comandos)
3. Após limpeza, sistema volta a tratar perguntas como independentes

**Cenário 4: Limite de Contexto**
1. Usuário faz 15 perguntas em sequência
2. Sistema mantém apenas as últimas 10 mensagens (sliding window)
3. Mensagens mais antigas são descartadas automaticamente

#### Critérios de Aceitação

**Given** o chat está ativo e o usuário fez uma pergunta anterior  
**When** o usuário faz uma pergunta de follow-up que referencia a conversa anterior  
**Then** o sistema deve:
- Incluir as últimas N perguntas e respostas no contexto do prompt enviado à LLM
- Gerar resposta que considera o contexto histórico
- Manter histórico apenas na sessão atual (não persistir entre sessões)
- Exibir indicador visual de que contexto está sendo usado (ex: "💬 Usando contexto de 3 mensagens anteriores")

**Given** o histórico contém mais de X mensagens (configurável, padrão: 10)  
**When** uma nova pergunta é feita  
**Then** o sistema deve:
- Manter apenas as últimas X mensagens (sliding window)
- Descartar mensagens mais antigas para não exceder limites de token
- Logar warning se contexto estiver próximo do limite

**Given** o usuário executa comando `clear-history` ou `reset-context`  
**When** o comando é confirmado  
**Then** o sistema deve:
- Limpar todo o histórico conversacional da sessão atual
- Manter histórico de comandos (não afeta `.chat_history`)
- Continuar funcionando normalmente (sem contexto conversacional)
- Exibir confirmação: "✓ Contexto conversacional limpo"

**Given** modo verbose está ativo  
**When** uma pergunta usa contexto conversacional  
**Then** o sistema deve:
- Exibir número de mensagens no contexto (ex: "💬 Contexto: 3 mensagens")
- Exibir tokens utilizados pelo contexto (ex: "📊 Tokens de contexto: 450/4000")

#### Detalhes Técnicos
- **Implementação**: Classe `ConversationMemory` em `src/conversation_memory.py`
- **Formato**: Lista de dicionários `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
- **Armazenamento**: Apenas em memória (não persistido entre sessões)
- **Tamanho máximo**: Configurável via `.env` (`CONVERSATION_HISTORY_SIZE`, padrão: 10 mensagens)
- **Integração**: Histórico incluído no prompt enviado ao LLM via `ConversationBufferMemory` do LangChain
- **Comandos**: `clear-history`, `reset-context`, `show-context` (exibe contexto atual)

---

### 4.2 RF-002: Suporte a Múltiplos Formatos de Documento

#### Descrição
O sistema deve suportar ingestão de documentos em formatos DOCX, TXT, Markdown e HTML além de PDF.

#### Justificativa
- **Problema**: Limitação a PDFs restringe casos de uso comuns (documentação técnica em MD, contratos em DOCX, artigos em HTML)
- **Impacto**: Expande significativamente a base de documentos que podem ser ingeridos
- **Valor**: Alto - aumenta versatilidade e aplicabilidade do sistema

#### Fluxo Esperado

**Cenário 1: Ingestão de DOCX**
1. Usuário executa: `add contrato.docx`
2. Sistema detecta extensão `.docx`
3. Sistema usa loader apropriado (`UnstructuredWordDocumentLoader`)
4. Processa normalmente (chunking, embeddings, armazenamento)
5. Metadados incluem `file_format: "docx"`

**Cenário 2: Ingestão de TXT**
1. Usuário executa: `add notas.txt`
2. Sistema detecta extensão `.txt`
3. Sistema usa `TextLoader` do LangChain
4. Processa normalmente, preservando quebras de linha

**Cenário 3: Ingestão de Markdown**
1. Usuário executa: `add README.md`
2. Sistema detecta extensão `.md`
3. Sistema usa `UnstructuredMarkdownLoader`
4. Processa normalmente, preservando estrutura de headers

**Cenário 4: Ingestão de HTML**
1. Usuário executa: `add artigo.html`
2. Sistema detecta extensão `.html`
3. Sistema usa `UnstructuredHTMLLoader`
4. Remove tags HTML, processa apenas texto

**Cenário 5: Formato Não Suportado**
1. Usuário executa: `add planilha.xlsx`
2. Sistema detecta formato não suportado
3. Sistema exibe: "❌ Formato não suportado. Formatos aceitos: PDF, DOCX, TXT, MD, HTML"
4. Operação é cancelada

**Cenário 6: Detecção Automática de Encoding (TXT)**
1. Usuário ingere arquivo TXT com encoding UTF-8
2. Sistema detecta encoding automaticamente
3. Se falhar, tenta encodings comuns (UTF-8, Latin-1, CP1252)
4. Se todos falharem, exibe erro claro

#### Critérios de Aceitação

**Given** um arquivo DOCX existe no sistema de arquivos  
**When** o usuário executa `add arquivo.docx`  
**Then** o sistema deve:
- Detectar formato DOCX
- Carregar conteúdo usando `UnstructuredWordDocumentLoader`
- Processar normalmente (chunking, embeddings, armazenamento)
- Armazenar metadados: `file_format: "docx"`, `filename`, `source`
- Preservar formatação básica (parágrafos, listas)

**Given** um arquivo TXT existe  
**When** o usuário executa `add arquivo.txt`  
**Then** o sistema deve:
- Detectar encoding automaticamente
- Carregar conteúdo de texto
- Processar normalmente
- Preservar quebras de linha e estrutura básica

**Given** um arquivo Markdown existe  
**When** o usuário executa `add arquivo.md`  
**Then** o sistema deve:
- Carregar conteúdo preservando estrutura Markdown
- Processar headers, listas, code blocks
- Metadados devem indicar `file_format: "md"`

**Given** um arquivo HTML existe  
**When** o usuário executa `add arquivo.html`  
**Then** o sistema deve:
- Remover tags HTML
- Extrair apenas texto visível
- Processar normalmente
- Metadados devem indicar `file_format: "html"`

**Given** um arquivo com formato não suportado (ex: XLSX, PPTX)  
**When** o usuário tenta ingerir  
**Then** o sistema deve:
- Detectar formato não suportado
- Exibir mensagem de erro clara
- Listar formatos suportados
- Não processar o arquivo

**Given** comando `stats` é executado  
**When** há documentos de múltiplos formatos  
**Then** o sistema deve:
- Exibir estatísticas por formato (ex: "3 PDFs, 2 DOCX, 1 MD")
- Mostrar total de chunks por formato

#### Detalhes Técnicos
- **Loaders**: 
  - PDF: `PyPDFLoader`
  - DOCX: `UnstructuredWordDocumentLoader` (requer `python-docx` ou `unstructured`)
  - TXT: `TextLoader` (com detecção automática de encoding)
  - Markdown: `UnstructuredMarkdownLoader`
  - HTML: `UnstructuredHTMLLoader`
- **Detecção de formato**: Por extensão de arquivo (case-insensitive)
- **Metadados**: Campo `file_format` adicionado a todos os chunks
- **Validação**: Função `validate_file_format(filepath)` em `src/ingest.py`
- **Suporte**: CLI (`chat.py`) e script standalone (`ingest.py`)
- **Dependências**: Atualizar `requirements.txt` com `python-docx`, `unstructured`, `markdown`

---

### 4.3 RF-003: Observabilidade Profissional

#### Descrição
O sistema deve fornecer logs estruturados (JSON), métricas de performance e rastreamento distribuído para facilitar diagnóstico, monitoramento e otimização em ambientes de produção.

#### Justificativa
- **Problema**: Logs básicos dificultam diagnóstico de problemas, análise de performance e troubleshooting em produção
- **Impacto**: Facilita operação profissional do sistema, reduz MTTR (Mean Time To Recovery)
- **Valor**: Alto - essencial para ambientes de produção

#### Fluxo Esperado

**Cenário 1: Logs Estruturados (JSON)**
1. Sistema executa operação de busca
2. Log é gerado em formato JSON:
   ```json
   {
     "timestamp": "2026-01-29T03:00:00Z",
     "level": "INFO",
     "request_id": "req-abc123",
     "module": "search",
     "operation": "semantic_search",
     "duration_ms": 1234,
     "status": "success",
     "metadata": {
       "top_k": 10,
       "temperature": 0.0,
       "cache_hit": false,
       "chunks_retrieved": 10,
       "llm_tokens": 450
     }
   }
   ```
3. Logs podem ser consumidos por ferramentas (ELK, Splunk, CloudWatch)

**Cenário 2: Métricas de Performance**
1. Sistema coleta métricas em tempo real
2. Comando `stats --metrics` exibe:
   ```
   📊 Métricas de Performance (última hora):
   - Buscas realizadas: 150
   - Latência média: 1.2s (p50), 2.5s (p95), 4.1s (p99)
   - Cache hit rate: 35%
   - Erros: 2 (1.3%)
   - Tokens consumidos: 45,000
   ```

**Cenário 3: Rastreamento Distribuído**
1. Usuário faz pergunta
2. Sistema gera `request_id` único (UUID)
3. Todos os logs relacionados compartilham mesmo `request_id`
4. Facilita rastreamento de operações complexas

**Cenário 4: Exportação de Métricas**
1. Sistema expõe métricas via endpoint `/metrics` (formato Prometheus)
2. Métricas incluem: `rag_search_duration_seconds`, `rag_cache_hit_total`, `rag_errors_total`
3. Pode ser integrado com Prometheus/Grafana

#### Critérios de Aceitação

**Given** flag `--json-logs` está ativa  
**When** uma operação é executada  
**Then** o sistema deve:
- Gerar logs em formato JSON válido
- Incluir: timestamp, level, request_id, module, operation, duration, status
- Incluir metadados relevantes (top_k, temperature, cache_hit, etc.)
- Logs devem ser parseáveis por ferramentas de análise

**Given** comando `stats --metrics` é executado  
**When** estatísticas são exibidas  
**Then** o sistema deve:
- Mostrar métricas de performance (latência p50/p95/p99)
- Mostrar estatísticas de cache (hit rate, tamanho atual)
- Mostrar estatísticas de documentos (total, por formato)
- Mostrar estatísticas de erros (total, por tipo)
- Mostrar consumo de tokens (total, média por busca)

**Given** uma operação é executada  
**When** a operação inicia  
**Then** o sistema deve:
- Gerar `request_id` único (UUID v4)
- Incluir `request_id` em todos os logs relacionados
- Incluir `request_id` na resposta (modo verbose)

**Given** uma operação falha  
**When** erro é logado  
**Then** o sistema deve:
- Incluir stack trace completo (apenas em modo debug)
- Incluir `request_id` para rastreamento
- Incluir contexto da operação (parâmetros, estado)
- Categorizar erro (tipo, severidade)

**Given** API REST está ativa (RF-005)  
**When** endpoint `/metrics` é acessado  
**Then** o sistema deve:
- Retornar métricas em formato Prometheus
- Incluir: `rag_search_duration_seconds`, `rag_cache_hit_total`, `rag_errors_total`, `rag_documents_total`
- Atualizar métricas em tempo real

#### Detalhes Técnicos
- **Logs estruturados**: Opcional via flag `--json-logs` (não quebra ferramentas existentes)
- **Formato**: JSON Lines (um JSON por linha)
- **Biblioteca**: `python-json-logger` ou implementação customizada
- **Métricas**: Classe `MetricsCollector` em `src/metrics.py`
- **Armazenamento**: Métricas mantidas em memória (não persistidas neste ciclo)
- **Request ID**: UUID v4 gerado no início de cada operação
- **Exportação**: Endpoint `/metrics` (formato Prometheus) se API REST estiver ativa
- **Configuração**: `ENABLE_JSON_LOGS`, `ENABLE_METRICS` em `.env`

---

### 4.4 RF-004: Cache Inteligente de Embeddings

#### Descrição
O sistema deve cachear embeddings de perguntas para evitar recálculo quando a mesma pergunta (ou pergunta muito similar) for feita novamente, reduzindo latência e custos de API.

#### Justificativa
- **Problema**: Embeddings são recalculados a cada busca, mesmo para perguntas idênticas
- **Impacto**: Reduz latência (até 50% para perguntas repetidas) e custos de API (até 40% de redução)
- **Valor**: Alto - melhora performance e reduz custos operacionais

#### Fluxo Esperado

**Cenário 1: Pergunta Repetida (Cache Hit)**
1. Usuário pergunta: "Qual o faturamento?"
2. Sistema calcula embedding e busca (cache miss)
3. Sistema armazena embedding no cache
4. Usuário pergunta novamente: "Qual o faturamento?"
5. Sistema usa embedding do cache (cache hit)
6. Latência reduzida de 2.5s para 1.2s

**Cenário 2: Pergunta Similar (Opcional)**
1. Usuário pergunta: "Qual o faturamento da empresa?"
2. Sistema calcula e cacheia
3. Usuário pergunta: "Qual foi o faturamento?"
4. Sistema detecta similaridade alta (>95%) e usa cache (se configurado)

**Cenário 3: Cache Expira (TTL)**
1. Cache tem TTL configurável (ex: 1 hora)
2. Após TTL, embedding é recalculado
3. Novo embedding substitui o antigo no cache

**Cenário 4: Cache Cheio (LRU)**
1. Cache atinge tamanho máximo (ex: 100 entradas)
2. Nova pergunta é feita
3. Sistema remove entrada menos recentemente usada (LRU)
4. Adiciona nova entrada ao cache

**Cenário 5: Indicador de Cache (Verbose)**
1. Modo verbose está ativo
2. Pergunta usa cache
3. Sistema exibe: "⚡ Cache hit - Latência reduzida em 52%"

#### Critérios de Aceitação

**Given** uma pergunta foi feita anteriormente na sessão  
**When** a mesma pergunta é feita novamente  
**Then** o sistema deve:
- Usar embedding do cache (não chamar API de embeddings)
- Reduzir tempo de resposta em pelo menos 30%
- Manter mesma qualidade de resultados
- Incrementar métrica `cache_hit_total`

**Given** o cache atingiu tamanho máximo (configurável, padrão: 100)  
**When** uma nova pergunta é feita  
**Then** o sistema deve:
- Aplicar política LRU (Least Recently Used)
- Remover entrada mais antiga
- Adicionar nova entrada ao cache
- Manter performance consistente

**Given** modo verbose está ativo  
**When** uma pergunta usa cache  
**Then** o sistema deve:
- Indicar no output: "⚡ Cache hit"
- Mostrar tempo de resposta reduzido
- Mostrar economia de tempo (ex: "52% mais rápido")

**Given** comando `stats --cache` é executado  
**When** estatísticas são exibidas  
**Then** o sistema deve:
- Mostrar cache hit rate (ex: "35%")
- Mostrar tamanho atual do cache (ex: "45/100 entradas")
- Mostrar economia de custos estimada (ex: "~$2.50 economizados")

**Given** TTL do cache expirou (configurável, padrão: 3600s)  
**When** pergunta é feita  
**Then** o sistema deve:
- Recalcular embedding
- Atualizar entrada no cache com novo timestamp
- Resetar TTL

#### Detalhes Técnicos
- **Implementação**: Classe `EmbeddingCache` em `src/embedding_cache.py`
- **Backend**: `functools.lru_cache` ou cache customizado em memória (dict + OrderedDict)
- **Chave de cache**: Hash SHA-256 da pergunta normalizada (lowercase, sem espaços extras, sem pontuação)
- **TTL**: Configurável via `.env` (`EMBEDDING_CACHE_TTL`, padrão: 3600 segundos)
- **Tamanho máximo**: Configurável via `.env` (`EMBEDDING_CACHE_SIZE`, padrão: 100 entradas)
- **Política de evicção**: LRU (Least Recently Used)
- **Escopo**: Apenas embeddings de perguntas (não embeddings de documentos)
- **Persistência**: Apenas em memória (não persistido entre sessões neste ciclo)
- **Métricas**: `cache_hit_total`, `cache_miss_total`, `cache_size`, `cache_evictions_total`

---

### 4.5 RF-005: API REST

#### Descrição
O sistema deve expor suas funcionalidades via API REST HTTP para permitir integração com outras aplicações, mantendo compatibilidade com a interface CLI existente.

#### Justificativa
- **Problema**: Apenas CLI limita integração com outras aplicações (web apps, mobile apps, microservices)
- **Impacto**: Expande significativamente os casos de uso e permite arquiteturas modernas
- **Valor**: Alto - essencial para integração enterprise

#### Fluxo Esperado

**Cenário 1: Busca via API**
1. Cliente HTTP faz POST para `/api/v1/search`
   ```json
   {
     "question": "Qual o faturamento?",
     "top_k": 10,
     "temperature": 0.0,
     "use_context": true
   }
   ```
2. Sistema processa busca
3. Sistema retorna resposta:
   ```json
   {
     "request_id": "req-abc123",
     "answer": "O faturamento foi de 10 milhões",
     "sources": [
       {"filename": "relatorio.pdf", "page": 5, "chunk_index": 12}
     ],
     "metadata": {
       "duration_ms": 1234,
       "cache_hit": false,
       "chunks_retrieved": 10,
       "llm_tokens": 450
     }
   }
   ```

**Cenário 2: Ingestão via API**
1. Cliente faz POST para `/api/v1/documents` com multipart/form-data
2. Sistema recebe arquivo e metadados
3. Sistema processa ingestão em background (async)
4. Sistema retorna:
   ```json
   {
     "job_id": "job-xyz789",
     "status": "processing",
     "message": "Documento em processamento"
   }
   ```
5. Cliente pode consultar status via GET `/api/v1/jobs/job-xyz789`

**Cenário 3: Listagem de Documentos**
1. Cliente faz GET para `/api/v1/documents`
2. Sistema retorna lista:
   ```json
   {
     "total": 5,
     "documents": [
       {
         "source": "relatorio.pdf",
         "format": "pdf",
         "chunks": 67,
         "ingested_at": "2026-01-29T03:00:00Z"
       }
     ]
   }
   ```

**Cenário 4: Autenticação (API Key)**
1. Cliente faz request sem header `X-API-Key`
2. Sistema retorna 401 Unauthorized
3. Cliente adiciona header `X-API-Key: sk-abc123`
4. Sistema valida API key e processa request

**Cenário 5: Rate Limiting**
1. Cliente faz 100 requests em 1 minuto
2. Sistema retorna 429 Too Many Requests
3. Header `Retry-After` indica quando tentar novamente

#### Critérios de Aceitação

**Given** API REST está ativa  
**When** cliente faz POST para `/api/v1/search` com pergunta válida  
**Then** o sistema deve:
- Processar busca semântica
- Retornar resposta em formato JSON
- Incluir `request_id`, `answer`, `sources`, `metadata`
- Retornar status 200 OK

**Given** cliente faz POST para `/api/v1/documents` com arquivo válido  
**When** arquivo é recebido  
**Then** o sistema deve:
- Validar formato de arquivo
- Processar ingestão em background (async)
- Retornar `job_id` e status "processing"
- Retornar status 202 Accepted

**Given** cliente faz GET para `/api/v1/jobs/{job_id}`  
**When** job existe  
**Then** o sistema deve:
- Retornar status do job ("processing", "completed", "failed")
- Incluir progresso (ex: "45/67 chunks processados")
- Incluir erros se houver

**Given** cliente faz request sem `X-API-Key`  
**When** autenticação é obrigatória  
**Then** o sistema deve:
- Retornar status 401 Unauthorized
- Incluir mensagem de erro clara

**Given** cliente excede rate limit (configurável, ex: 60 req/min)  
**When** request é feito  
**Then** o sistema deve:
- Retornar status 429 Too Many Requests
- Incluir header `Retry-After` com tempo de espera

**Given** API REST está ativa  
**When** cliente acessa `/api/v1/docs`  
**Then** o sistema deve:
- Retornar documentação OpenAPI/Swagger
- Documentação deve ser interativa (Swagger UI)

#### Detalhes Técnicos
- **Framework**: FastAPI (async, auto-documentação OpenAPI, validação Pydantic)
- **Endpoints**:
  - `POST /api/v1/search`: Busca semântica
  - `POST /api/v1/documents`: Upload de documento
  - `GET /api/v1/documents`: Listar documentos
  - `DELETE /api/v1/documents/{source}`: Remover documento
  - `GET /api/v1/jobs/{job_id}`: Status de job
  - `GET /api/v1/stats`: Estatísticas do sistema
  - `GET /api/v1/metrics`: Métricas (formato Prometheus)
  - `GET /api/v1/docs`: Documentação OpenAPI
- **Autenticação**: API keys via header `X-API-Key` (validação em middleware)
- **Rate Limiting**: `slowapi` ou `fastapi-limiter` (configurável via `.env`)
- **Async**: Ingestão de documentos em background (Celery ou FastAPI BackgroundTasks)
- **CORS**: Configurável via `.env` (`CORS_ORIGINS`)
- **Porta**: Configurável via `.env` (`API_PORT`, padrão: 8000)
- **Execução**: `uvicorn src.api:app --host 0.0.0.0 --port 8000`
- **Compatibilidade**: CLI continua funcionando normalmente (não afeta)

---

## 5. Requisitos Não Funcionais

### 5.1 Performance

**RNF-001: Latência de Resposta**
- Buscas com cache devem ter latência < 1s (p95)
- Buscas sem cache devem manter latência atual (< 5s p95)
- Histórico conversacional não deve aumentar latência em mais de 20%
- API REST deve ter latência similar à CLI (< 5s p95)

**RNF-002: Throughput**
- API REST deve suportar pelo menos 100 requests/min por instância
- Cache deve suportar pelo menos 1000 entradas sem degradação
- Sistema deve suportar ingestão de arquivos até 50MB

**RNF-003: Uso de Memória**
- Cache de embeddings não deve exceder 100MB em uso típico
- Histórico conversacional não deve exceder 10MB por sessão
- API REST não deve exceder 500MB de memória por instância

### 5.2 Usabilidade

**RNF-004: Compatibilidade com Versões Anteriores**
- Todas as funcionalidades CLI existentes devem continuar funcionando
- Configurações antigas (`.env`) devem continuar válidas
- CLI deve manter mesma interface (novos argumentos são opcionais)
- Histórico de comandos existente deve continuar funcionando

**RNF-005: Documentação**
- README deve ser atualizado com novas funcionalidades
- CHANGELOG deve documentar todas as mudanças
- Exemplos de uso devem incluir novas features
- API REST deve ter documentação OpenAPI/Swagger completa

**RNF-006: Facilidade de Uso**
- Histórico conversacional deve ser transparente (ativado automaticamente)
- Cache deve ser transparente (ativado automaticamente)
- API REST deve ter defaults sensatos (não requer configuração extensa)

### 5.3 Observabilidade

**RNF-007: Logs**
- Logs estruturados devem ser opcionais (não quebrar ferramentas existentes)
- Logs devem incluir níveis apropriados (DEBUG, INFO, WARNING, ERROR)
- Logs não devem expor informações sensíveis (API keys, conteúdo de documentos)
- Logs devem ser parseáveis por ferramentas de análise (ELK, Splunk)

**RNF-008: Métricas**
- Métricas devem ser coletadas sem impacto significativo na performance (< 5% overhead)
- Métricas devem ser acessíveis via comando `stats` e endpoint `/metrics`
- Métricas não devem ser persistidas (apenas em memória neste ciclo)
- Métricas devem incluir: latência, throughput, cache hit rate, erros, tokens consumidos

**RNF-009: Rastreamento**
- Todas as operações críticas devem ter `request_id` único
- Logs relacionados devem compartilhar mesmo `request_id`
- `request_id` deve ser retornado ao cliente (API REST e CLI verbose)

### 5.4 Segurança

**RNF-010: Validação de Entrada**
- Sistema deve validar formatos de arquivo antes de processar
- Sistema deve sanitizar inputs do usuário para prevenir injection
- Sistema deve validar tamanhos de arquivo (limite máximo: 50MB)
- API REST deve validar payloads JSON (Pydantic schemas)

**RNF-011: Autenticação**
- API REST deve suportar autenticação via API keys
- API keys devem ser armazenadas de forma segura (hashed)
- Sistema deve suportar múltiplas API keys (para diferentes clientes)
- Rate limiting deve ser aplicado por API key

**RNF-012: Tratamento de Erros**
- Erros não devem expor informações sensíveis (stack traces apenas em modo debug)
- Erros devem ser logados apropriadamente
- Sistema deve se recuperar graciosamente de erros não críticos
- API REST deve retornar códigos HTTP apropriados (400, 401, 404, 500, etc.)

### 5.5 Escalabilidade

**RNF-013: Horizontal Scaling**
- API REST deve ser stateless (exceto cache em memória)
- Sistema deve suportar múltiplas instâncias (load balancer)
- Cache deve ser compartilhável entre instâncias (Redis, opcional)

**RNF-014: Limites**
- Sistema deve suportar até 10.000 chunks por coleção
- Sistema deve suportar até 100 documentos por coleção
- Cache deve suportar até 1000 entradas
- Histórico conversacional deve suportar até 20 mensagens

---

## 6. Métricas de Sucesso

### 6.1 Métricas de Produto

**MS-001: Adoção de Histórico Conversacional**
- **Meta**: 60% dos usuários fazem pelo menos uma pergunta de follow-up por sessão
- **Medição**: Logs de uso do histórico (ativado quando > 1 pergunta na sessão)

**MS-002: Eficiência do Cache**
- **Meta**: Cache hit rate > 30% em uso típico
- **Medição**: Razão entre cache hits e total de buscas

**MS-003: Expansão de Formatos**
- **Meta**: Pelo menos 30% dos novos documentos ingeridos são não-PDF (DOCX, TXT, MD, HTML)
- **Medição**: Estatísticas de formatos ingeridos (via comando `stats`)

**MS-004: Adoção de API REST**
- **Meta**: Pelo menos 20% das buscas são feitas via API REST (vs CLI)
- **Medição**: Logs de uso de API vs CLI

### 6.2 Métricas Técnicas

**MS-005: Performance**
- **Meta**: Redução de 40% na latência média para perguntas com cache
- **Medição**: Comparação de tempos antes/depois (p50, p95, p99)

**MS-006: Estabilidade**
- **Meta**: Uptime > 99.5% (API REST)
- **Medição**: Monitoramento de disponibilidade

**MS-007: Observabilidade**
- **Meta**: 100% das operações críticas geram logs estruturados
- **Medição**: Auditoria de logs gerados

**MS-008: Redução de Custos**
- **Meta**: Redução de 35% em custos de API (embeddings) através de cache
- **Medição**: Comparação de custos antes/depois

### 6.3 Métricas de Experiência do Usuário

**MS-009: Satisfação com Diálogos**
- **Meta**: Usuários conseguem fazer perguntas de follow-up com sucesso (> 80% de sucesso)
- **Medição**: Análise de logs de conversas (perguntas de follow-up que geram respostas relevantes)

**MS-010: Facilidade de Integração**
- **Meta**: Desenvolvedores conseguem integrar API REST em < 30 minutos
- **Medição**: Feedback de desenvolvedores, análise de documentação

**MS-011: Diversidade de Formatos**
- **Meta**: Pelo menos 4 formatos diferentes ingeridos por usuário ativo
- **Medição**: Análise de metadados de documentos

---

## 7. Riscos e Premissas

### 7.1 Riscos Técnicos

**Risco 1: Complexidade do Histórico Conversacional**
- **Descrição**: Implementação pode ser mais complexa que esperado, especialmente gerenciamento de tokens e contexto
- **Probabilidade**: Média
- **Impacto**: Alto
- **Mitigação**: 
  - Implementar sliding window simples inicialmente
  - Limitar tamanho máximo do histórico (10 mensagens)
  - Testar com diferentes tamanhos de contexto
  - Usar `ConversationBufferMemory` do LangChain (já testado)

**Risco 2: Performance do Cache**
- **Descrição**: Cache pode não trazer benefícios esperados se perguntas raramente se repetem
- **Probabilidade**: Baixa
- **Impacto**: Médio
- **Mitigação**: 
  - Implementar cache simples inicialmente
  - Coletar métricas de hit rate
  - Otimizar baseado em dados reais
  - Considerar cache de chunks (além de embeddings)

**Risco 3: Dependências de Loaders**
- **Descrição**: Loaders para DOCX/HTML podem ter dependências adicionais ou problemas de compatibilidade
- **Probabilidade**: Média
- **Impacto**: Médio
- **Mitigação**: 
  - Testar loaders antes de implementar
  - Documentar dependências adicionais claramente
  - Ter fallback para PDF se outros formatos falharem
  - Usar `unstructured` library (já testada)

**Risco 4: Escalabilidade da API REST**
- **Descrição**: API REST pode não escalar adequadamente sob carga alta
- **Probabilidade**: Baixa
- **Impacto**: Alto
- **Mitigação**: 
  - Usar FastAPI (async, alta performance)
  - Implementar rate limiting desde o início
  - Testar com ferramentas de load testing (Locust, k6)
  - Documentar limites de escalabilidade

**Risco 5: Overhead de Observabilidade**
- **Descrição**: Logs estruturados e métricas podem impactar performance
- **Probabilidade**: Baixa
- **Impacto**: Baixo
- **Mitigação**: 
  - Implementar logs estruturados como opcional
  - Coletar métricas de forma assíncrona quando possível
  - Medir impacto antes de ativar por padrão
  - Usar bibliotecas otimizadas (`python-json-logger`)

### 7.2 Riscos de Produto

**Risco 6: Expectativas de Histórico Persistente**
- **Descrição**: Usuários podem esperar histórico conversacional persistente entre sessões
- **Probabilidade**: Média
- **Impacto**: Médio
- **Mitigação**: 
  - Documentar claramente que histórico é apenas por sessão
  - Considerar persistência em ciclo futuro (v0.7.0) se houver demanda
  - Fornecer comando para exportar conversas (opcional)

**Risco 7: Complexidade de API para Usuários Não Técnicos**
- **Descrição**: API REST pode ser complexa para usuários não técnicos
- **Probabilidade**: Baixa
- **Impacto**: Baixo
- **Mitigação**: 
  - Manter CLI como interface principal para usuários finais
  - API REST é para integradores/desenvolvedores
  - Fornecer exemplos de código (Python, JavaScript, cURL)
  - Documentação OpenAPI/Swagger interativa

**Risco 8: Adoção de Múltiplos Formatos**
- **Descrição**: Usuários podem não adotar novos formatos se PDF já atende
- **Probabilidade**: Baixa
- **Impacto**: Baixo
- **Mitigação**: 
  - Documentar casos de uso para cada formato
  - Fornecer exemplos de documentos em diferentes formatos
  - Coletar feedback de usuários sobre formatos desejados

### 7.3 Premissas Assumidas

**Premissa 1**: Usuários têm Python 3.10+ e podem instalar dependências adicionais (ex: `python-docx`, `unstructured`)  
**Premissa 2**: Ambiente de execução suporta operações assíncronas (para API REST e timeouts)  
**Premissa 3**: APIs de embeddings/LLM continuam disponíveis e com mesmas interfaces  
**Premissa 4**: Usuários não precisam de histórico conversacional persistente entre sessões neste ciclo  
**Premissa 5**: Formato de logs estruturados (JSON) é aceitável para ferramentas existentes  
**Premissa 6**: Rate limiting básico (por IP ou API key) é suficiente para este ciclo  
**Premissa 7**: Cache em memória é suficiente (Redis pode ser adicionado em v0.7.0)  

---

## 8. Fora de Escopo

### 8.1 Explicitamente Fora de Escopo

❌ **Interface Web Completa**: Apenas API REST, sem frontend HTML/JS (pode ser v0.7.0)  
❌ **Autenticação Avançada**: Apenas API keys básicas, sem OAuth/SAML/JWT (pode ser v0.7.0)  
❌ **Persistência de Histórico Conversacional**: Histórico apenas em memória (pode ser v0.7.0)  
❌ **Múltiplas Coleções/Workspaces**: Sistema continua com coleção única (pode ser v0.7.0)  
❌ **Busca Híbrida**: Apenas busca semântica, sem BM25/keyword search (pode ser v0.8.0)  
❌ **OCR para PDFs Escaneados**: Apenas PDFs com texto nativo (pode ser v0.8.0)  
❌ **Suporte a Imagens**: Apenas texto extraído de documentos (pode ser v0.9.0)  
❌ **Modo Append na Ingestão**: Continua substituindo documentos completamente (pode ser v0.7.0)  
❌ **Validação de Duplicatas**: Detecção de chunks duplicados não é escopo  
❌ **Cache Distribuído**: Cache apenas em memória, sem Redis/Memcached (pode ser v0.7.0)  
❌ **Exportação de Conversas**: Histórico não é exportável neste ciclo  
❌ **Multi-idioma**: Suporte apenas a português (como atual)  
❌ **Suporte a Planilhas**: XLSX/CSV não são suportados (pode ser v0.8.0)  
❌ **Suporte a Apresentações**: PPTX não é suportado (pode ser v0.8.0)  
❌ **Webhooks**: Notificações de eventos não são suportadas (pode ser v0.7.0)  

### 8.2 Considerações para Ciclos Futuros

**v0.7.0 (Futuro Próximo)**:
- Persistência de histórico conversacional entre sessões
- Múltiplas coleções/workspaces (multi-tenancy)
- Interface web básica (frontend)
- Autenticação avançada (OAuth, JWT)
- Cache distribuído (Redis)
- Modo append na ingestão (incremental)

**v0.8.0+ (Futuro Médio)**:
- Busca híbrida (semântica + BM25)
- OCR para PDFs escaneados
- Suporte a planilhas (XLSX, CSV)
- Suporte a apresentações (PPTX)
- Exportação de conversas (JSON, Markdown)

**v0.9.0+ (Futuro Longo)**:
- Suporte a imagens em documentos (multimodal)
- Busca por imagens (CLIP embeddings)
- Análise de gráficos e tabelas
- Multi-idioma (i18n)
- Webhooks e notificações

---

## 9. Dependências e Pré-requisitos

### 9.1 Dependências Técnicas

**Bibliotecas Python (Novas)**:
- `fastapi` - Framework para API REST
- `uvicorn` - ASGI server para FastAPI
- `pydantic` - Validação de dados
- `python-json-logger` - Logs estruturados
- `python-docx` ou `unstructured` - Loader para DOCX
- `markdown` - Loader para Markdown (se necessário)
- `slowapi` ou `fastapi-limiter` - Rate limiting
- `prometheus-client` - Exportação de métricas

**Bibliotecas Python (Existentes)**:
- `langchain` - Framework RAG
- `langchain-postgres` - Vector store
- `langchain-google-genai` - Google Gemini
- `langchain-openai` - OpenAI
- `pypdf` - PDF loader
- `psycopg2-binary` - PostgreSQL driver
- `python-dotenv` - Variáveis de ambiente

### 9.2 Dependências de Infraestrutura

- **PostgreSQL + pgVector**: Já configurado (sem mudanças)
- **APIs Externas**: Google Gemini / OpenAI (sem mudanças)
- **Servidor HTTP**: Uvicorn para API REST (novo)

### 9.3 Dependências de Equipe

- **Desenvolvimento**: 1-2 desenvolvedores Python (backend)
- **QA**: Testes de funcionalidades novas + testes de API
- **Documentação**: Atualização de README, CHANGELOG, OpenAPI docs
- **DevOps**: Configuração de servidor para API REST (opcional)

---

## 10. Plano de Implementação (Alto Nível)

### 10.1 Fase 1: Cache de Embeddings (Sprint 1)
**Duração**: 1 semana  
**Prioridade**: Alta  
- Implementar classe `EmbeddingCache`
- Adicionar métricas de cache (hit rate, size)
- Integrar com `search.py`
- Testes de performance
- Documentação

### 10.2 Fase 2: Histórico Conversacional (Sprint 2)
**Duração**: 1-2 semanas  
**Prioridade**: Alta  
- Implementar classe `ConversationMemory`
- Integrar histórico no prompt (LangChain `ConversationBufferMemory`)
- Adicionar comandos `clear-history`, `show-context`
- Testes de diálogos
- Documentação

### 10.3 Fase 3: Suporte a Múltiplos Formatos (Sprint 3)
**Duração**: 1 semana  
**Prioridade**: Alta  
- Adicionar loaders para DOCX, TXT, MD, HTML
- Atualizar validação de formatos
- Atualizar metadados (campo `file_format`)
- Testes de ingestão para cada formato
- Documentação

### 10.4 Fase 4: Observabilidade (Sprint 4)
**Duração**: 1-2 semanas  
**Prioridade**: Média  
- Implementar logs estruturados (JSON)
- Implementar classe `MetricsCollector`
- Adicionar rastreamento com `request_id`
- Atualizar comando `stats` com métricas
- Documentação

### 10.5 Fase 5: API REST (Sprint 5-6)
**Duração**: 2-3 semanas  
**Prioridade**: Alta  
- Implementar API REST com FastAPI
- Endpoints: `/search`, `/documents`, `/stats`, `/metrics`
- Autenticação via API keys
- Rate limiting
- Documentação OpenAPI/Swagger
- Testes de API (Postman, pytest)

### 10.6 Fase 6: Testes e Documentação (Sprint 7)
**Duração**: 1 semana  
**Prioridade**: Alta  
- Testes end-to-end completos
- Atualizar suite de testes E2E (adicionar novos casos)
- Atualizar README com novas funcionalidades
- Atualizar CHANGELOG
- Preparar release v0.6.0

**Total Estimado**: 7-9 semanas (sprints de 1 semana)

---

## 11. Aprovações e Stakeholders

### 11.1 Stakeholders

- **Product Manager**: Aprovação de requisitos e prioridades
- **Tech Lead**: Aprovação de abordagem técnica e arquitetura
- **Desenvolvedores**: Feedback sobre viabilidade e estimativas
- **QA**: Validação de critérios de aceitação e plano de testes
- **DevOps**: Validação de requisitos de infraestrutura (API REST)

### 11.2 Critérios de Aprovação

- ✅ Requisitos funcionais claros e testáveis
- ✅ Riscos identificados e mitigados
- ✅ Escopo realista para timeline proposto (7-9 semanas)
- ✅ Compatibilidade com sistema atual garantida (backward compatibility)
- ✅ Dependências técnicas identificadas e disponíveis
- ✅ Métricas de sucesso mensuráveis

---

**Fim do PRD**

**Próximos Passos**:
1. ✅ Revisão e aprovação do PRD pelo Product Manager
2. ⏳ Criação de issues/tarefas técnicas no GitHub
3. ⏳ Planejamento detalhado de sprints
4. ⏳ Kickoff de desenvolvimento (Sprint 1: Cache de Embeddings)
5. ⏳ Setup de ambiente de desenvolvimento (dependências, testes)
