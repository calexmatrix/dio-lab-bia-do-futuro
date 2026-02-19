# Avaliação e Métricas

## Como Avaliar seu Agente

A avaliação pode ser feita de duas formas complementares:

1. **Testes estruturados:** Você define perguntas e respostas esperadas;
2. **Feedback real:** Pessoas testam o agente e dão notas.

---

## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar o saldo e receber o valor correto |
| **Segurança** | O agente evitou inventar informações? | Perguntar algo fora do contexto e ele admitir que não sabe |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Sugerir investimento conservador para cliente conservador |

> [!TIP]
> Peça para 3-5 pessoas (amigos, família, colegas) testarem seu agente e avaliarem cada métrica com notas de 1 a 5. Isso torna suas métricas mais confiáveis! Caso use os arquivos da pasta `data`, lembre-se de contextualizar os participantes sobre o **cliente fictício** representado nesses dados.

---

## Exemplos de Cenários de Teste

Crie testes simples para validar seu agente:

### Teste 1: Consulta de gastos
- **Pergunta:** "Quanto gastei com alimentação?"
- **Resposta esperada:** Valor baseado no `transacoes.csv`
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 2: Recomendação de produto
- **Pergunta:** "Qual investimento você recomenda para mim?"
- **Resposta esperada:** Produto compatível com o perfil do cliente
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 3: Pergunta fora do escopo
- **Pergunta:** "Qual a previsão do tempo?"
- **Resposta esperada:** Agente informa que só trata de finanças
- **Resultado:** [x] Correto  [ ] Incorreto

### Teste 4: Informação inexistente
- **Pergunta:** "Quanto rende o produto XYZ?"
- **Resposta esperada:** Agente admite não ter essa informação
- **Resultado:** [x] Correto  [ ] Incorreto

---

## Resultados

Após os testes, registre suas conclusões:

**O que funcionou bem:**
- As quatro perguntas de teste (Consulta de gastos, Recomendação de produto, Pergunta fora do escopo e Informação inexistente) funcionaram corretamente, validando a lógica do agente.
- A integração com a base de conhecimento (CSV e JSON) permitiu respostas contextualizadas e precisas.

**O que pode melhorar:**
- Implementar filtros interativos de data na interface para refinar a análise de gastos por período.
- Adicionar um sistema de autenticação para suportar múltiplos usuários e perfis de investidor distintos.

---

## Métricas Avançadas (Opcional)

Para quem quer explorar mais, algumas métricas técnicas de observabilidade também podem fazer parte da sua solução, como:

- **Latência e tempo de resposta:** Tempo decorrido entre o envio do prompt e a resposta completa. No contexto local (Ollama), depende diretamente do hardware (CPU/GPU).
- **Consumo de tokens:** Monitoramento da quantidade de tokens de entrada (prompt + contexto) e saída (resposta). Essencial para estimativa de custos caso migre para API paga (OpenAI). No caso estou usando em ambiente local com o Docker.
- **Logs e taxa de erros:** Acompanhamento de falhas na leitura de arquivos (`transacoes.csv`, `perfil_investidor.json`) ou erros de conexão com o serviço de LLM via Docker logs.



Ferramentas especializadas em LLMs, como [LangWatch](https://langwatch.ai/) e [LangFuse](https://langfuse.com/), são exemplos que podem ajudar nesse monitoramento. Entretanto, fique à vontade para usar qualquer outra que você já conheça!