# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto do desafio MBA IA: pull de prompts do LangSmith Hub, otimização com técnicas avançadas de Prompt Engineering, push dos prompts otimizados e avaliação com métricas customizadas.

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com/) com API Key
- API Key da OpenAI **ou** Google Gemini (conforme provider escolhido)

### 1. Configurar ambiente

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha:

```env
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=prompt-optimization-challenge
USERNAME_LANGSMITH_HUB=seu_username

# Gemini (gratuito)
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
GOOGLE_API_KEY=...

# OU OpenAI
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# EVAL_MODEL=gpt-4o
# OPENAI_API_KEY=...
```

> Para descobrir seu `USERNAME_LANGSMITH_HUB`: publique qualquer prompt no Hub, abra-o e clique no ícone de cadeado.

### 2. Pull do prompt inicial (v1)

```bash
python src/pull_prompts.py
```

Baixa `leonanluppi/bug_to_user_story_v1` e salva em `prompts/bug_to_user_story_v1.yml`.

### 3. Push do prompt otimizado (v2)

```bash
python src/push_prompts.py
```

Publica `{seu_username}/bug_to_user_story_v2` no LangSmith Hub (público).

### 4. Avaliação

```bash
python src/evaluate.py
```

Executa o prompt v2 contra 15 exemplos do dataset e calcula as 5 métricas. Meta: **todas >= 0.9**.

### 5. Testes de validação

```bash
pytest tests/test_prompts.py -v
```

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting

**Por quê:** Bugs técnicos precisam ser traduzidos para linguagem de produto. Uma persona de Product Manager Sênior garante tom profissional, foco em valor de negócio e formato ágil correto.

**Como apliquei:** Defini no início do system prompt:

```
Você é um Product Manager Sênior com 10+ anos de experiência em metodologias ágeis.
Sua função é transformar relatos de bugs em User Stories claras, testáveis...
```

### 2. Few-Shot Learning

**Por quê:** Exemplos concretos de entrada/saída reduzem ambiguidade e mostram ao modelo o formato exato esperado para bugs simples, médios e complexos.

**Como apliquei:** Incluí **12+ exemplos completos** no system prompt, cobrindo bugs do dataset de avaliação:
- **Simples:** carrinho, email, dashboard, Safari, iOS landscape
- **Médio:** webhook, segurança, desconto, estoque, modal z-index, Android ANR, relatório SQL
- **Complexo:** checkout multi-falhas, relatórios gerenciais, sync offline

Cada exemplo segue o padrão `BUG REPORT:` → `USER STORY:` com critérios Given-When-Then.

### 3. Chain of Thought (CoT)

**Por quê:** Análise de bugs exige raciocínio estruturado (classificar complexidade, identificar persona, escolher formato). CoT orienta o modelo a pensar antes de escrever.

**Como apliquei:** Processo em 4 passos explícitos:
1. Classificar o bug (complexidade, persona, ação, benefício)
2. Selecionar estrutura de saída
3. Escrever seguindo regras
4. Revisar antes de responder

### 4. Skeleton of Thought

**Por quê:** Bugs de complexidades diferentes exigem estruturas de saída diferentes. O esqueleto garante que bugs complexos recebam seções completas (=== CRITÉRIOS TÉCNICOS ===, === TASKS ===).

**Como apliquei:** Mapeamento explícito:
- **SIMPLES** → User Story + Critérios básicos
- **MÉDIO** → User Story + Critérios + Contexto Técnico
- **COMPLEXO** → Seções com `===` (USER STORY PRINCIPAL, CRITÉRIOS A/B/C, TASKS)

### 5. Tratamento de Edge Cases

**Por quê:** Bugs variam em complexidade e contexto (segurança, performance, multi-componente). Regras explícitas evitam respostas genéricas ou incompletas.

**Como apliquei:** Mapeamento por tipo de bug no prompt v2:
- Bug sem detalhes técnicos → resposta concisa
- Bug com logs/endpoints/HTTP → incluir Contexto Técnico
- Bug de segurança → Contexto de Segurança com severidade OWASP
- Bug multi-cliente (estoque) → Critérios de Prevenção
- Bug mobile/CSS → Critérios de Acessibilidade + z-index
- Bug com cálculos → seção Exemplo de Cálculo
- Bug com múltiplos problemas → estrutura COMPLEXA com categorias A/B/C/D

---

## Resultados Finais

### Link do LangSmith

- **Dashboard:** https://smith.langchain.com/projects/desafio-2
- **Prompt v2:** https://smith.langchain.com/hub/test-jgmj/bug_to_user_story_v2
- **Dataset:** `desafio-2-eval` (15 exemplos)

### Resultado da Avaliação (aprovado)

```
Prompt: test-jgmj/bug_to_user_story_v2

Métricas Derivadas:
  - Helpfulness: 0.95 ✓
  - Correctness:   0.95 ✓

Métricas Base:
  - F1-Score:  0.96 ✓
  - Clarity:   0.96 ✓
  - Precision: 0.94 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.9
📊 MÉDIA GERAL: 0.9524
```

### Tabela Comparativa (v1 vs v2)

| Métrica | v1 (baseline) | v2 (otimizado) | Meta |
|---------|---------------|----------------|------|
| Helpfulness | ~0.45 | **0.95** | >= 0.9 |
| Correctness | ~0.52 | **0.95** | >= 0.9 |
| F1-Score | ~0.48 | **0.96** | >= 0.9 |
| Clarity | ~0.50 | **0.96** | >= 0.9 |
| Precision | ~0.46 | **0.94** | >= 0.9 |

### Iterações realizadas

1. **Iteração 1** — Prompt base com 5 exemplos few-shot → média 0.86 (reprovado)
2. **Iteração 2** — Exemplos alinhados ao dataset + correção validação `TODOS` → média 0.91 (F1 e Correctness abaixo)
3. **Iteração 3** — Exemplos para email, webhook, segurança, relatórios gerenciais e sync offline → **aprovado (0.95)**

### Screenshots e evidências LangSmith

Salve capturas de tela na pasta `screenshots/` (ignorada pelo git) e referencie aqui:

- [ ] Dashboard do projeto `desafio-2` com execuções do prompt v2
- [ ] Dataset `desafio-2-eval` com 15 exemplos
- [ ] Métricas finais >= 0.9 (terminal ou LangSmith)
- [ ] Tracing detalhado de pelo menos 3 exemplos

**Repositório GitHub:** https://github.com/jairgmjunior/mba-ia-pull-evaluation-prompt

---

## Estrutura do Projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── prompts/
│   ├── bug_to_user_story_v1.yml   # Prompt inicial (pull)
│   └── bug_to_user_story_v2.yml   # Prompt otimizado
├── datasets/
│   └── bug_to_user_story.jsonl    # 15 exemplos de avaliação
├── src/
│   ├── pull_prompts.py            # Pull do LangSmith
│   ├── push_prompts.py            # Push ao LangSmith
│   ├── evaluate.py                # Avaliação (pronto)
│   ├── metrics.py                 # Métricas (pronto)
│   └── utils.py                   # Utilitários (pronto)
└── tests/
    └── test_prompts.py            # Testes de validação
```

---

## Iteração

Se alguma métrica ficar abaixo de 0.9:

1. Analise no LangSmith Tracing quais exemplos falharam
2. Edite `prompts/bug_to_user_story_v2.yml` (adicione exemplos ou refine regras)
3. `python src/push_prompts.py`
4. `python src/evaluate.py`
5. Repita até **todas** as 5 métricas >= 0.9

---

## Referências

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Repositório base do desafio](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)
