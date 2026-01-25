# Product Requirements Document (PRD)
## Sistema RAG - Evolução v0.5.0

**Versão do PRD:** 1.0  
**Data:** 2026-01-24  
**Baseado em:** Functional Specification As-Is (v0.4.0)  
**Objetivo:** Definir requisitos para a próxima evolução do sistema

---

## 1. Visão do Produto

### 1.1 Problema que o Produto Resolve

O sistema RAG atual permite fazer perguntas sobre documentos PDF, mas possui limitações que impactam a experiência do usuário e a eficiência operacional:

1. **Falta de Contexto Conversacional**: Cada pergunta é isolada, impedindo diálogos naturais com perguntas de follow-up
2. **Performance Subótima**: Embeddings são recalculados para perguntas repetidas, gerando custos e latência desnecessários
3. **Limitação de Formatos**: Suporte apenas a PDFs restringe casos de uso comuns (DOCX, TXT, Markdown)
4. **Observabilidade Limitada**: Dificulta diagnóstico de problemas e otimização do sistema
5. **Bugs Conhecidos**: Import faltante e validações inconsistentes podem causar falhas em runtime

### 1.2 Público-Alvo

- **Usuários Finais**: Profissionais que precisam consultar documentos regularmente (pesquisadores, analistas, consultores)
- **Desenvolvedores**: Equipes que integram busca semântica em aplicações
- **Operadores**: Usuários técnicos que gerenciam e monitoram o sistema

### 1.3 Objetivo da Próxima Fase

Melhorar significativamente a experiência do usuário e a robustez do sistema através de:

1. **Histórico de Conversas**: Permitir diálogos contextuais com perguntas de follow-up
2. **Cache de Embeddings**: Reduzir latência e custos de API para perguntas repetidas
3. **Suporte a Múltiplos Formatos**: Expandir para DOCX, TXT e Markdown além de PDF
4. **Observabilidade Aprimorada**: Logs estruturados e métricas básicas
5. **Correção de Bugs Críticos**: Eliminar bugs conhecidos que podem causar falhas

**Meta de Versão**: v0.5.0 (Minor release - novas funcionalidades compatíveis)

---

## 2. Contexto Atual (Resumo)

### 2.1 Principais Capacidades Existentes

✅ **Ingestão de PDFs**: Carregamento, chunking (1000 chars, overlap 150), geração de embeddings, armazenamento em PGVector  
✅ **Busca Semântica**: Similarity search (top-k configurável), geração de respostas via LLM com template fixo  
✅ **Interface CLI Interativa**: Chat com comandos (add, remove, clear, stats, help)  
✅ **Suporte Multi-Provedor**: Google Gemini e OpenAI com detecção automática  
✅ **Gerenciamento de Documentos**: Remoção por arquivo, limpeza total, estatísticas  
✅ **Modos de Operação**: Quiet, verbose, parâmetros configuráveis via CLI  

### 2.2 Principais Limitações Atuais

❌ **Sem Histórico de Conversas**: Cada pergunta é independente  
❌ **Sem Cache de Embeddings**: Recalcula embeddings para perguntas idênticas  
❌ **Apenas PDFs**: Não suporta DOCX, TXT, Markdown  
❌ **Observabilidade Limitada**: Logs básicos, sem métricas estruturadas  
❌ **Bugs Conhecidos**: Import faltante em `chat.py`, validação inconsistente de PDF  
❌ **Sem Timeout**: Operações podem travar indefinidamente  
❌ **Template Fixo**: Prompt não é customizável  

---

## 3. Objetivos do PRD

### 3.1 O que se Pretende Melhorar

#### 3.1.1 Experiência do Usuário
- Permitir diálogos contextuais com histórico de conversas
- Reduzir latência de respostas através de cache
- Expandir formatos de documento suportados

#### 3.1.2 Robustez e Confiabilidade
- Corrigir bugs conhecidos que podem causar falhas
- Adicionar timeouts para evitar travamentos
- Melhorar tratamento de erros

#### 3.1.3 Observabilidade
- Logs estruturados para análise
- Métricas básicas de performance
- Rastreamento de operações

#### 3.1.4 Performance e Custos
- Cache de embeddings para reduzir chamadas de API
- Otimização de operações repetidas

### 3.2 O que NÃO é Objetivo deste Ciclo

❌ **Interface Web**: Manter apenas CLI neste ciclo  
❌ **Autenticação/Autorização**: Não é escopo atual  
❌ **Múltiplas Coleções**: Namespaces/workspaces ficam para futuro  
❌ **Templates Customizáveis**: Manter template fixo (pode ser v0.6.0)  
❌ **Modo Append na Ingestão**: Manter comportamento de substituição  
❌ **Validação de Duplicatas**: Detecção de chunks duplicados fica para futuro  
❌ **Refatoração Arquitetural Maior**: Manter estrutura atual, apenas melhorias incrementais  

---

## 4. Requisitos Funcionais

### 4.1 RF-001: Histórico de Conversas

#### Descrição
O sistema deve manter contexto de perguntas e respostas anteriores durante uma sessão de chat, permitindo perguntas de follow-up que referenciam conversas anteriores.

#### Justificativa
- **Problema**: Usuários precisam reformular perguntas de forma autossuficiente, impedindo diálogos naturais
- **Impacto**: Melhora significativamente a experiência do usuário, permitindo conversas mais naturais
- **Valor**: Alto - feature mais solicitada e de maior impacto na UX

#### Fluxo Esperado

**Cenário 1: Pergunta de Follow-up**
1. Usuário pergunta: "Qual o faturamento da empresa X?"
2. Sistema responde: "O faturamento foi de 10 milhões"
3. Usuário pergunta: "E qual foi o crescimento em relação ao ano anterior?"
4. Sistema usa contexto da pergunta anterior para entender "ano anterior" e "crescimento"

**Cenário 2: Referência a Resposta Anterior**
1. Usuário pergunta: "Quais são os principais produtos?"
2. Sistema lista produtos A, B, C
3. Usuário pergunta: "Quantos clientes tem o produto A?"
4. Sistema entende que "produto A" refere-se à resposta anterior

**Cenário 3: Limpeza de Histórico**
1. Usuário pode usar comando `clear-history` ou `reset` para limpar contexto
2. Após limpeza, sistema volta a tratar perguntas como independentes

#### Critérios de Aceitação

**Given** o chat está ativo e o usuário fez uma pergunta anterior  
**When** o usuário faz uma pergunta de follow-up que referencia a conversa anterior  
**Then** o sistema deve:
- Incluir as últimas N perguntas e respostas no contexto do prompt
- Gerar resposta que considera o contexto histórico
- Manter histórico apenas na sessão atual (não persistir entre sessões)

**Given** o histórico contém mais de X mensagens (ex: 10)  
**When** uma nova pergunta é feita  
**Then** o sistema deve:
- Manter apenas as últimas X mensagens (sliding window)
- Descartar mensagens mais antigas para não exceder limites de token

**Given** o usuário executa comando `clear-history`  
**When** o comando é confirmado  
**Then** o sistema deve:
- Limpar todo o histórico da sessão atual
- Continuar funcionando normalmente (sem histórico)

#### Detalhes Técnicos
- Histórico mantido em memória (não persistido)
- Configuração de tamanho máximo do histórico via `.env` (padrão: 10 mensagens)
- Histórico incluído no prompt enviado ao LLM
- Formato: lista de dicionários `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`

---

### 4.2 RF-002: Cache de Embeddings

#### Descrição
O sistema deve cachear embeddings de perguntas para evitar recálculo quando a mesma pergunta (ou pergunta muito similar) for feita novamente.

#### Justificativa
- **Problema**: Embeddings são recalculados a cada busca, mesmo para perguntas idênticas
- **Impacto**: Reduz latência (até 50% para perguntas repetidas) e custos de API
- **Valor**: Médio-Alto - melhora performance e reduz custos operacionais

#### Fluxo Esperado

**Cenário 1: Pergunta Repetida**
1. Usuário pergunta: "Qual o faturamento?"
2. Sistema calcula embedding e busca
3. Usuário pergunta novamente: "Qual o faturamento?"
4. Sistema usa embedding do cache (não recalcula)

**Cenário 2: Pergunta Similar**
1. Usuário pergunta: "Qual o faturamento da empresa?"
2. Sistema calcula e cacheia
3. Usuário pergunta: "Qual foi o faturamento?"
4. Sistema detecta similaridade alta e usa cache (se configurado)

**Cenário 3: Cache Expira**
1. Cache tem TTL configurável (ex: 1 hora)
2. Após TTL, embedding é recalculado
3. Novo embedding substitui o antigo no cache

#### Critérios de Aceitação

**Given** uma pergunta foi feita anteriormente na sessão  
**When** a mesma pergunta é feita novamente  
**Then** o sistema deve:
- Usar embedding do cache (não chamar API de embeddings)
- Reduzir tempo de resposta em pelo menos 30%
- Manter mesma qualidade de resultados

**Given** o cache atingiu tamanho máximo (ex: 100 entradas)  
**When** uma nova pergunta é feita  
**Then** o sistema deve:
- Aplicar política LRU (Least Recently Used) para remover entrada mais antiga
- Adicionar nova entrada ao cache
- Manter performance consistente

**Given** o modo verbose está ativo  
**When** uma pergunta usa cache  
**Then** o sistema deve:
- Indicar no output que cache foi usado (ex: "⚡ Cache hit")
- Mostrar tempo de resposta reduzido

#### Detalhes Técnicos
- Implementação: `functools.lru_cache` ou cache customizado em memória
- Chave de cache: hash da pergunta normalizada (lowercase, sem espaços extras)
- TTL configurável via `.env` (padrão: 3600 segundos)
- Tamanho máximo configurável (padrão: 100 entradas)
- Cache apenas para embeddings de perguntas (não para embeddings de documentos)

---

### 4.3 RF-003: Suporte a Múltiplos Formatos de Documento

#### Descrição
O sistema deve suportar ingestão de documentos em formatos DOCX, TXT e Markdown além de PDF.

#### Justificativa
- **Problema**: Limitação a PDFs restringe casos de uso comuns
- **Impacto**: Expande significativamente a base de documentos que podem ser ingeridos
- **Valor**: Médio - aumenta versatilidade do sistema

#### Fluxo Esperado

**Cenário 1: Ingestão de DOCX**
1. Usuário executa: `add documento.docx`
2. Sistema detecta extensão `.docx`
3. Sistema usa loader apropriado (ex: `UnstructuredWordDocumentLoader`)
4. Processa normalmente (chunking, embeddings, armazenamento)

**Cenário 2: Ingestão de TXT**
1. Usuário executa: `add texto.txt`
2. Sistema detecta extensão `.txt`
3. Sistema usa `TextLoader` do LangChain
4. Processa normalmente

**Cenário 3: Ingestão de Markdown**
1. Usuário executa: `add README.md`
2. Sistema detecta extensão `.md`
3. Sistema usa loader apropriado
4. Processa normalmente

**Cenário 4: Formato Não Suportado**
1. Usuário executa: `add arquivo.xlsx`
2. Sistema detecta formato não suportado
3. Sistema exibe mensagem: "Formato não suportado. Formatos aceitos: PDF, DOCX, TXT, MD"
4. Operação é cancelada

#### Critérios de Aceitação

**Given** um arquivo DOCX existe no sistema de arquivos  
**When** o usuário executa `add arquivo.docx`  
**Then** o sistema deve:
- Detectar formato DOCX
- Carregar conteúdo usando loader apropriado
- Processar normalmente (chunking, embeddings, armazenamento)
- Armazenar metadados indicando formato original

**Given** um arquivo TXT existe  
**When** o usuário executa `add arquivo.txt`  
**Then** o sistema deve:
- Carregar conteúdo de texto
- Processar normalmente
- Preservar quebras de linha e estrutura básica

**Given** um arquivo Markdown existe  
**When** o usuário executa `add arquivo.md`  
**Then** o sistema deve:
- Carregar conteúdo preservando estrutura Markdown
- Processar normalmente
- Metadados devem indicar formato MD

**Given** um arquivo com formato não suportado (ex: XLSX)  
**When** o usuário tenta ingerir  
**Then** o sistema deve:
- Detectar formato não suportado
- Exibir mensagem de erro clara
- Listar formatos suportados
- Não processar o arquivo

#### Detalhes Técnicos
- Loaders do LangChain: `PyPDFLoader` (PDF), `UnstructuredWordDocumentLoader` (DOCX), `TextLoader` (TXT), `UnstructuredMarkdownLoader` (MD)
- Detecção de formato por extensão de arquivo
- Metadados devem incluir `file_format` além de `filename` e `source`
- Validação de extensão no comando `add` do chat
- Suporte também no script `ingest.py` standalone

---

### 4.4 RF-004: Observabilidade Aprimorada

#### Descrição
O sistema deve fornecer logs estruturados e métricas básicas para facilitar diagnóstico, monitoramento e otimização.

#### Justificativa
- **Problema**: Logs básicos dificultam diagnóstico de problemas e análise de performance
- **Impacto**: Facilita troubleshooting e otimização do sistema
- **Valor**: Médio - importante para operação em produção

#### Fluxo Esperado

**Cenário 1: Logs Estruturados**
1. Operações críticas geram logs em formato JSON
2. Logs incluem: timestamp, nível, módulo, operação, duração, status
3. Logs podem ser consumidos por ferramentas de análise (ex: ELK, Splunk)

**Cenário 2: Métricas de Performance**
1. Sistema coleta métricas: tempo de busca, tempo de geração, uso de cache
2. Métricas expostas via comando `stats` ou arquivo
3. Métricas incluem: média, p95, p99 de tempos de resposta

**Cenário 3: Rastreamento de Operações**
1. Cada operação recebe um `request_id` único
2. Logs relacionados compartilham mesmo `request_id`
3. Facilita rastreamento de operações complexas

#### Critérios de Aceitação

**Given** uma operação de busca é executada  
**When** a operação completa (sucesso ou erro)  
**Then** o sistema deve:
- Gerar log estruturado com: timestamp, request_id, operação, duração, status
- Log deve ser parseável como JSON
- Log deve incluir contexto relevante (top_k usado, temperatura, etc.)

**Given** o comando `stats` é executado  
**When** estatísticas são exibidas  
**Then** o sistema deve:
- Mostrar métricas de performance (tempo médio de busca, tempo médio de geração)
- Mostrar estatísticas de cache (hit rate, tamanho atual)
- Mostrar estatísticas de documentos (total, por formato)

**Given** uma operação falha  
**When** erro é logado  
**Then** o sistema deve:
- Incluir stack trace completo
- Incluir request_id para rastreamento
- Incluir contexto da operação (parâmetros, estado)

#### Detalhes Técnicos
- Formato de log: JSON estruturado (opcional, via flag `--json-logs`)
- Logs estruturados apenas em modo não-quiet
- Métricas mantidas em memória (não persistidas)
- Request ID: UUID v4 gerado no início de cada operação
- Métricas coletadas: tempo de busca, tempo de geração LLM, cache hits/misses, erros por tipo

---

### 4.5 RF-005: Timeout Configurável

#### Descrição
O sistema deve permitir configurar timeout para operações de busca e geração de respostas, evitando travamentos indefinidos.

#### Justificativa
- **Problema**: Operações podem travar indefinidamente se API estiver lenta ou inacessível
- **Impacto**: Melhora robustez e experiência do usuário
- **Valor**: Médio - importante para operação confiável

#### Fluxo Esperado

**Cenário 1: Timeout na Busca**
1. Usuário faz pergunta
2. Busca demora mais que timeout configurado (ex: 30s)
3. Sistema cancela operação e exibe: "Operação excedeu timeout de 30s. Tente novamente."

**Cenário 2: Timeout na Geração LLM**
1. LLM demora mais que timeout para gerar resposta
2. Sistema cancela e exibe mensagem de erro
3. Usuário pode tentar novamente

**Cenário 3: Timeout Configurado via CLI**
1. Usuário executa: `python src/chat.py --timeout 60`
2. Timeout de 60s é aplicado a todas as operações da sessão

#### Critérios de Aceitação

**Given** timeout está configurado (ex: 30s)  
**When** uma operação de busca excede o timeout  
**Then** o sistema deve:
- Cancelar operação após timeout
- Exibir mensagem de erro clara
- Não travar ou ficar indefinidamente esperando
- Retornar ao prompt normalmente

**Given** timeout está configurado  
**When** uma operação completa antes do timeout  
**Then** o sistema deve:
- Funcionar normalmente
- Não haver impacto na performance

**Given** timeout não está configurado  
**When** operações são executadas  
**Then** o sistema deve:
- Usar timeout padrão (ex: 60s) ou ilimitado (comportamento atual)
- Documentar comportamento no README

#### Detalhes Técnicos
- Timeout configurável via `.env` (ex: `SEARCH_TIMEOUT=30`)
- Timeout configurável via CLI `--timeout`
- Aplicado a: busca vetorial, chamadas de API (embeddings, LLM)
- Implementação: `signal.alarm` (Unix) ou `threading.Timer` (cross-platform)
- Timeout padrão: 60 segundos se não configurado

---

### 4.6 RF-006: Correção de Bugs Críticos

#### Descrição
Corrigir bugs conhecidos que podem causar falhas em runtime.

#### Justificativa
- **Problema**: Bugs conhecidos podem causar falhas inesperadas
- **Impacto**: Melhora estabilidade e confiabilidade
- **Valor**: Alto - elimina riscos de produção

#### Bugs a Corrigir

**Bug 1: Import Faltante em `chat.py`**
- **Problema**: `chat.py` usa `sa.exc.SQLAlchemyError` sem importar `sqlalchemy as sa`
- **Impacto**: `NameError` em runtime se exceção for lançada
- **Solução**: Adicionar `import sqlalchemy as sa` ou usar import direto

**Bug 2: Validação Inconsistente de PDF**
- **Problema**: Validação de extensão `.pdf` apenas no chat, não no `ingest.py`
- **Impacto**: Comportamento inconsistente entre interfaces
- **Solução**: Adicionar validação de extensão também no `ingest.py` (ou remover do chat para consistência)
-- **Dúvida para discutirmos**: Não seria interessante essa validação acontecer em somente um lugar, pois assim evitamos duplicacao de codigo (DRY)?

**Bug 3: Import Faltante em `search.py`**
- **Problema**: `search.py` usa `sa.exc.SQLAlchemyError` sem importar
- **Impacto**: Mesmo que Bug 1
- **Solução**: Adicionar import apropriado

#### Critérios de Aceitação

**Given** uma exceção `SQLAlchemyError` é lançada  
**When** o código tenta capturar a exceção  
**Then** o sistema deve:
- Capturar exceção corretamente (sem `NameError`)
- Tratar erro apropriadamente
- Exibir mensagem de erro ao usuário

**Given** um arquivo sem extensão `.pdf` é passado para `ingest.py`  
**When** o script tenta processar  
**Then** o sistema deve:
- Validar extensão consistentemente (mesmo comportamento do chat)
- Exibir mensagem de erro clara
- Não processar arquivo inválido

#### Detalhes Técnicos
- Correções simples de imports
- Validação consistente entre `ingest.py` e `chat.py`
- Testes para garantir que bugs não regridam

---

## 5. Requisitos Não Funcionais

### 5.1 Performance

**RNF-001: Latência de Resposta**
- Buscas com cache devem ter latência < 1s (p95)
- Buscas sem cache devem manter latência atual (< 5s p95)
- Histórico de conversas não deve aumentar latência em mais de 20%

**RNF-002: Throughput**
- Sistema deve suportar pelo menos 10 perguntas simultâneas (se aplicável)
- Cache deve suportar pelo menos 1000 entradas sem degradação

**RNF-003: Uso de Memória**
- Cache de embeddings não deve exceder 50MB em uso típico
- Histórico de conversas não deve exceder 10MB por sessão

### 5.2 Usabilidade

**RNF-004: Compatibilidade com Versões Anteriores**
- Todas as funcionalidades existentes devem continuar funcionando
- Configurações antigas (`.env`) devem continuar válidas
- CLI deve manter mesma interface (novos argumentos são opcionais)

**RNF-005: Documentação**
- README deve ser atualizado com novas funcionalidades
- CHANGELOG deve documentar todas as mudanças
- Exemplos de uso devem incluir novas features

### 5.3 Observabilidade

**RNF-006: Logs**
- Logs estruturados devem ser opcionais (não quebrar ferramentas existentes)
- Logs devem incluir níveis apropriados (INFO, WARNING, ERROR)
- Logs não devem expor informações sensíveis (API keys, etc.)

**RNF-007: Métricas**
- Métricas devem ser coletadas sem impacto significativo na performance
- Métricas devem ser acessíveis via comando `stats`
- Métricas não devem ser persistidas (apenas em memória neste ciclo)

### 5.4 Segurança

**RNF-008: Validação de Entrada**
- Sistema deve validar formatos de arquivo antes de processar
- Sistema deve sanitizar inputs do usuário para prevenir injection
- Sistema deve validar tamanhos de arquivo (limite máximo)

**RNF-009: Tratamento de Erros**
- Erros não devem expor informações sensíveis (stack traces apenas em modo debug)
- Erros devem ser logados apropriadamente
- Sistema deve se recuperar graciosamente de erros não críticos

---

## 6. Métricas de Sucesso

### 6.1 Métricas de Produto

**MS-001: Adoção de Histórico de Conversas**
- **Meta**: 70% dos usuários fazem pelo menos uma pergunta de follow-up por sessão
- **Medição**: Logs de uso do histórico (ativado quando >1 pergunta na sessão)

**MS-002: Eficiência do Cache**
- **Meta**: Cache hit rate > 30% em uso típico
- **Medição**: Razão entre cache hits e total de buscas

**MS-003: Expansão de Formatos**
- **Meta**: Pelo menos 20% dos novos documentos ingeridos são não-PDF (DOCX, TXT, MD)
- **Medição**: Estatísticas de formatos ingeridos (via comando `stats`)

### 6.2 Métricas Técnicas

**MS-004: Performance**
- **Meta**: Redução de 30% na latência média para perguntas com cache
- **Medição**: Comparação de tempos antes/depois (p50, p95, p99)

**MS-005: Estabilidade**
- **Meta**: Zero falhas causadas por bugs conhecidos corrigidos
- **Medição**: Monitoramento de erros em produção

**MS-006: Observabilidade**
- **Meta**: 100% das operações críticas geram logs estruturados
- **Medição**: Auditoria de logs gerados

### 6.3 Métricas de Experiência do Usuário

**MS-007: Satisfação com Diálogos**
- **Meta**: Usuários conseguem fazer perguntas de follow-up com sucesso (>80% de sucesso)
- **Medição**: Análise de logs de conversas (perguntas de follow-up que geram respostas relevantes)

**MS-008: Redução de Erros**
- **Meta**: Redução de 50% em erros relacionados a timeouts
- **Medição**: Comparação de erros de timeout antes/depois

---

## 7. Riscos e Premissas

### 7.1 Riscos Técnicos

**Risco 1: Complexidade do Histórico de Conversas**
- **Descrição**: Implementação pode ser mais complexa que esperado, especialmente gerenciamento de tokens
- **Probabilidade**: Média
- **Impacto**: Alto
- **Mitigação**: 
  - Implementar sliding window simples inicialmente
  - Limitar tamanho máximo do histórico
  - Testar com diferentes tamanhos de contexto

**Risco 2: Performance do Cache**
- **Descrição**: Cache pode não trazer benefícios esperados se perguntas raramente se repetem
- **Probabilidade**: Baixa
- **Impacto**: Baixo
- **Mitigação**: 
  - Implementar cache simples inicialmente
  - Coletar métricas de hit rate
  - Otimizar baseado em dados reais

**Risco 3: Dependências de Loaders**
- **Descrição**: Loaders para DOCX/MD podem ter dependências adicionais ou problemas de compatibilidade
- **Probabilidade**: Média
- **Impacto**: Médio
- **Mitigação**: 
  - Testar loaders antes de implementar
  - Documentar dependências adicionais
  - Ter fallback para PDF se outros formatos falharem

### 7.2 Riscos de Produto

**Risco 4: Expectativas de Histórico**
- **Descrição**: Usuários podem esperar histórico persistente entre sessões, mas implementação será apenas em memória
- **Probabilidade**: Média
- **Impacto**: Médio
- **Mitigação**: 
  - Documentar claramente que histórico é apenas por sessão
  - Considerar persistência em ciclo futuro se houver demanda

**Risco 5: Overhead de Observabilidade**
- **Descrição**: Logs estruturados e métricas podem impactar performance
- **Probabilidade**: Baixa
- **Impacto**: Baixo
- **Mitigação**: 
  - Implementar logs estruturados como opcional
  - Coletar métricas de forma assíncrona quando possível
  - Medir impacto antes de ativar por padrão

### 7.3 Premissas Assumidas

**Premissa 1**: Usuários têm Python 3.10+ e podem instalar dependências adicionais (ex: `python-docx` para DOCX)  
**Premissa 2**: Ambiente de execução suporta operações assíncronas (para timeouts)  
**Premissa 3**: APIs de embeddings/LLM continuam disponíveis e com mesmas interfaces  
**Premissa 4**: Usuários não precisam de histórico persistente entre sessões neste ciclo  
**Premissa 5**: Formato de logs estruturados (JSON) é aceitável para ferramentas existentes  

---

## 8. Fora de Escopo

### 8.1 Explicitamente Fora de Escopo

❌ **Interface Web**: Manter apenas CLI neste ciclo  
❌ **Autenticação e Autorização**: Não é necessário para este ciclo  
❌ **Persistência de Histórico**: Histórico apenas em memória (por sessão)  
❌ **Múltiplas Coleções/Workspaces**: Sistema continua com coleção única  
❌ **Templates Customizáveis**: Template de prompt continua fixo  
❌ **Modo Append na Ingestão**: Continua substituindo documentos completamente  
❌ **Validação de Duplicatas**: Detecção de chunks duplicados não é escopo  
❌ **Interface Gráfica**: Apenas CLI  
❌ **API REST**: Não será exposta API HTTP  
❌ **Suporte a Imagens em PDFs**: Apenas texto extraído de PDFs  
❌ **OCR para PDFs Escaneados**: Apenas PDFs com texto nativo  
❌ **Busca Híbrida**: Apenas busca semântica (sem busca por palavras-chave)  
❌ **Exportação de Conversas**: Histórico não é exportável neste ciclo  
❌ **Multi-idioma**: Suporte apenas a português (como atual)  

### 8.2 Considerações para Ciclos Futuros

**v0.6.0 (Futuro)**:
- Templates de prompt customizáveis
- Persistência de histórico entre sessões
- Suporte a mais formatos (XLSX, PPTX, etc.)
- Interface web básica
- API REST

**v0.7.0+ (Futuro)**:
- Múltiplas coleções/workspaces
- Autenticação e autorização
- Busca híbrida (semântica + palavras-chave)
- OCR para PDFs escaneados
- Suporte a imagens em documentos

---

## 9. Dependências e Pré-requisitos

### 9.1 Dependências Técnicas

- **LangChain**: Versão atual (verificar compatibilidade com novos loaders)
- **Bibliotecas Adicionais**:
  - `python-docx` ou `unstructured` para DOCX
  - `markdown` para Markdown (se necessário)
- **Python**: 3.10+ (já requerido)

### 9.2 Dependências de Infraestrutura

- **PostgreSQL + pgVector**: Já configurado (sem mudanças)
- **APIs Externas**: Google Gemini / OpenAI (sem mudanças)

### 9.3 Dependências de Equipe

- **Desenvolvimento**: 1-2 desenvolvedores Python
- **QA**: Testes de funcionalidades novas
- **Documentação**: Atualização de README e CHANGELOG

---

## 10. Plano de Implementação (Alto Nível)

### 10.1 Fase 1: Correções de Bugs (Sprint 1)
- Corrigir imports faltantes
- Corrigir validação inconsistente
- Testes de regressão

### 10.2 Fase 2: Cache de Embeddings (Sprint 1-2)
- Implementar cache em memória
- Adicionar métricas de cache
- Testes de performance

### 10.3 Fase 3: Histórico de Conversas (Sprint 2-3)
- Implementar gerenciamento de histórico
- Integrar histórico no prompt
- Adicionar comando `clear-history`
- Testes de diálogos

### 10.4 Fase 4: Suporte a Múltiplos Formatos (Sprint 3)
- Adicionar loaders para DOCX, TXT, MD
- Atualizar validação de formatos
- Testes de ingestão

### 10.5 Fase 5: Observabilidade e Timeout (Sprint 4)
- Implementar logs estruturados
- Adicionar métricas básicas
- Implementar timeouts
- Atualizar documentação

### 10.6 Fase 6: Testes e Documentação (Sprint 4)
- Testes end-to-end
- Atualizar README
- Atualizar CHANGELOG
- Preparar release v0.5.0

---

## 11. Aprovações e Stakeholders

### 11.1 Stakeholders

- **Product Manager**: Aprovação de requisitos e prioridades
- **Tech Lead**: Aprovação de abordagem técnica
- **Desenvolvedores**: Feedback sobre viabilidade
- **QA**: Validação de critérios de aceitação

### 11.2 Critérios de Aprovação

- ✅ Requisitos funcionais claros e testáveis
- ✅ Riscos identificados e mitigados
- ✅ Escopo realista para timeline proposto
- ✅ Compatibilidade com sistema atual garantida

---

**Fim do PRD**

**Próximos Passos**:
1. Revisão e aprovação do PRD
2. Criação de issues/tarefas técnicas
3. Planejamento de sprints
4. Kickoff de desenvolvimento
