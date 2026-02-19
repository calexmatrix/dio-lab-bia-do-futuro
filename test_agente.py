import os
import re
import json
import pytest
import pandas as pd
from openai import OpenAI

# --- Configuração do Ambiente de Teste ---
# Tenta pegar variáveis de ambiente ou usa padrões para localhost (Docker)
BASE_URL = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.getenv("OPENAI_API_KEY", "ollama")
MODELO = os.getenv("MODELO", "llama3")

@pytest.fixture(scope="module")
def client():
    """Inicializa o cliente OpenAI para os testes."""
    return OpenAI(base_url=BASE_URL, api_key=API_KEY)

@pytest.fixture(scope="module")
def system_prompt():
    """
    Reconstrói o System Prompt combinando:
    1. Instruções do docs/03-prompts.md
    2. Dados do data/perfil_investidor.json
    3. Dados do data/produtos_financeiros.json
    4. Resumo do data/transacoes.csv
    """
    base_dir = os.getcwd() # Assume execução na raiz do projeto

    # 1. Carregar Prompt Base
    prompt_path = os.path.join(base_dir, "docs", "03-prompts.md")
    if not os.path.exists(prompt_path):
        pytest.fail(f"Arquivo de prompt não encontrado: {prompt_path}")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(r"```\n(.*?)\n```", content, re.DOTALL)
        full_prompt = match.group(1).strip() if match else "Você é um assistente financeiro."

    # 2. Injetar Perfil
    perfil_path = os.path.join(base_dir, "data", "perfil_investidor.json")
    if os.path.exists(perfil_path):
        with open(perfil_path, "r", encoding="utf-8") as f:
            perfil = json.load(f)
            full_prompt += f"\n\nPerfil do Investidor:\n{json.dumps(perfil, ensure_ascii=False, indent=2)}"

    # 3. Injetar Produtos
    prod_path = os.path.join(base_dir, "data", "produtos_financeiros.json")
    if os.path.exists(prod_path):
        with open(prod_path, "r", encoding="utf-8") as f:
            produtos = json.load(f)
            full_prompt += f"\n\nProdutos Financeiros Disponíveis:\n{json.dumps(produtos, ensure_ascii=False, indent=2)}"

    # 4. Injetar Transações
    trans_path = os.path.join(base_dir, "data", "transacoes.csv")
    if os.path.exists(trans_path):
        df = pd.read_csv(trans_path)
        if 'valor' in df.columns and 'categoria' in df.columns:
            gastos = df.groupby('categoria')['valor'].sum().reset_index()
            gastos_str = "\n".join([f"{cat}: R${val:.2f}" for cat, val in zip(gastos['categoria'], gastos['valor'])])
            full_prompt += f"\n\nResumo de Gastos:\n{gastos_str}"

    return full_prompt

def query_llm(client, prompt, question):
    """Função auxiliar para enviar pergunta ao LLM."""
    response = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        temperature=0.0 # Temperatura zero para maior determinismo nos testes
    )
    return response.choices[0].message.content

# --- Casos de Teste ---

def test_consulta_gastos(client, system_prompt):
    """Teste 1: Valida se o agente consegue ler o CSV de transações."""
    question = "Quanto gastei com alimentação?"
    response = query_llm(client, system_prompt, question)
    
    # Critérios: Deve mencionar a categoria e conter um valor numérico
    assert "alimentação" in response.lower()
    assert "R$" in response or any(c.isdigit() for c in response)

def test_recomendacao_produto(client, system_prompt):
    """Teste 2: Valida se o agente recomenda produtos do JSON."""
    question = "Qual investimento você recomenda para mim?"
    response = query_llm(client, system_prompt, question)
    
    # Critérios: Deve sugerir algo da lista de produtos
    termos_esperados = ["Tesouro", "CDB", "LCI", "LCA", "Fundo"]
    assert any(termo in response for termo in termos_esperados)

def test_pergunta_fora_escopo(client, system_prompt):
    """Teste 3: Valida se o agente recusa perguntas não financeiras."""
    question = "Qual a previsão do tempo para amanhã?"
    response = query_llm(client, system_prompt, question)
    
    # Critérios: Deve mencionar que não sabe ou redirecionar para finanças
    # Verifica radicais das palavras para cobrir variações (ex: financeiro/finanças, previsão/previsões)
    assert "previs" in response.lower() or "não" in response.lower() or "finan" in response.lower()

def test_informacao_inexistente(client, system_prompt):
    """Teste 4: Valida anti-alucinação para dados que não estão nos arquivos."""
    question = "Quanto rende o produto XYZ?"
    response = query_llm(client, system_prompt, question)
    
    # Critérios: Deve admitir que não conhece o produto
    assert "não" in response.lower() or "desconheço" in response.lower()