# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

> [!TIP]
> **Quer um dataset mais robusto?** Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio.

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Foram utilizados os dados mockados padrão fornecidos no desafio. O arquivo `transacoes.csv` é processado pelo Pandas para garantir que a coluna de datas seja interpretada corretamente, permitindo filtragem temporal na interface.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos são carregados localmente via Python (bibliotecas `pandas` e `json`) no início da execução do Streamlit. O container Docker possui um volume mapeado para a pasta `data/`, permitindo acesso direto aos arquivos.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são injetados diretamente no **System Prompt** (contexto inicial do modelo) antes do início da conversa:
- **Transações:** São processadas para gerar um resumo financeiro agrupado por categoria (ex: "Alimentação: R$ 570,00"), que é inserido no prompt.
- **Perfil e Produtos:** O conteúdo dos arquivos JSON é convertido para texto e anexado ao prompt, permitindo que o agente consulte as regras de perfil e a lista de produtos permitidos para recomendações controladas.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
Dados do Cliente:
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
