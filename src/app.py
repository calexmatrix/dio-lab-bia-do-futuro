import os
import re
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# --- Configuração do Cliente LLM ---
# O script usa a biblioteca 'openai', que é compatível com vários serviços.
#
# 1. Para usar a API da OpenAI:
#    - Instale: pip install openai
#    - Defina sua chave de API no terminal:
#      (Linux/macOS) export OPENAI_API_KEY='sua-chave-aqui'
#      (Windows)     set OPENAI_API_KEY=sua-chave-aqui
#    - O cliente será inicializado automaticamente com a chave.
#
# 2. Para usar um modelo local (ex: Llama 3 via Ollama no Docker):
#    - Instale: pip install openai
#    - Rode o Ollama: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
#    - Baixe o modelo: docker exec -it ollama ollama pull llama3
#    - Descomente as linhas abaixo para apontar para o servidor local:
#
# client = OpenAI(
#     base_url='http://localhost:11434/v1',
#     api_key='ollama',  # 'ollama' é a chave padrão para o servidor local
# ) 
# MODELO = "llama3" # Nome do modelo que você baixou no Ollama
# -------------------------------------------------------------------

# Configurações via Variáveis de Ambiente (padrão Docker) ou Fallback
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY")
MODELO = os.getenv("MODELO", "gpt-4o-mini")

try:
    # Inicializa o cliente com as configurações detectadas
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    print(f"Cliente inicializado. Conectado a: {BASE_URL}")
    print(f"Modelo selecionado: {MODELO}")
except Exception as e:
    print(f"Erro ao inicializar o cliente: {e}")
    exit()

def load_system_prompt(filepath="../docs/03-prompts.md"):
    """
    Carrega o system prompt de um arquivo markdown, extraindo o conteúdo
    do primeiro bloco de código.
    """
    # Resolve o caminho absoluto baseado na localização deste script (src/app.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regex para encontrar o conteúdo dentro do primeiro bloco de código ```...```
        match = re.search(r"```\n(.*?)\n```", content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        print("Aviso: Bloco de System Prompt não encontrado no formato esperado.")
        return "Você é um assistente útil."
    except FileNotFoundError:
        print(f"Erro: Arquivo de prompt não encontrado em '{filepath}'.")
        return None

def load_transactions(filepath="../data/transacoes.csv"):
    """
    Carrega as transações do arquivo CSV e retorna um DataFrame.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)

    try:
        # Tenta ler o CSV. Assume separador ',' e colunas 'categoria' e 'valor'
        df = pd.read_csv(full_path)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Erro ao ler arquivo de transações: {e}")
        return None

def load_json(filepath):
    """
    Carrega dados de um arquivo JSON.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filepath)

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao ler arquivo JSON '{filepath}': {e}")
        return None

def main():
    """Função principal que executa a interface web com Streamlit."""
    st.set_page_config(page_title="Caca - Assistente Financeiro", page_icon="💰")
    
    st.title("💰 Caca - Assistente Financeiro")
    st.caption("Especialista em organização e segurança patrimonial")

    system_prompt = load_system_prompt()

    # --- Carregamento de Contexto Adicional (Perfil e Produtos) ---
    perfil = load_json("../data/perfil_investidor.json")
    if perfil:
        system_prompt += f"\n\nPerfil do Investidor:\n{json.dumps(perfil, ensure_ascii=False, indent=2)}"

    produtos = load_json("../data/produtos_financeiros.json")
    if produtos:
        system_prompt += f"\n\nProdutos Financeiros Disponíveis:\n{json.dumps(produtos, ensure_ascii=False, indent=2)}"

    # --- Carregamento e Exibição de Dados Financeiros ---
    df = load_transactions()
    if df is not None and not df.empty:
        # Verifica se as colunas necessárias existem para o cálculo
        if 'categoria' in df.columns and 'valor' in df.columns:
            try:
                df_filtered = df.copy()
                
                # Filtro de Data
                if 'data' in df.columns:
                    st.sidebar.header("📅 Filtro de Data")
                    min_date = df['data'].min().date()
                    max_date = df['data'].max().date()
                    
                    start_date = st.sidebar.date_input("Data Inicial", min_date, min_value=min_date, max_value=max_date)
                    end_date = st.sidebar.date_input("Data Final", max_date, min_value=min_date, max_value=max_date)
                    
                    mask = (df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)
                    df_filtered = df.loc[mask]

                st.sidebar.header("📊 Resumo de Gastos")
                # Agrupa por categoria e soma os valores
                gastos_por_categoria = df_filtered.groupby('categoria')['valor'].sum().reset_index()
                st.sidebar.dataframe(gastos_por_categoria, hide_index=True)
                
                # Gráfico de Pizza
                fig = px.pie(
                    gastos_por_categoria,
                    values='valor',
                    names='categoria',
                    title='Distribuição de Gastos',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                st.sidebar.plotly_chart(fig, width="stretch")

                # Formata os gastos para incluir no prompt
                gastos_str = "\n".join([f"{cat}: R${val:.2f}" for cat, val in zip(gastos_por_categoria['categoria'], gastos_por_categoria['valor'])])
                system_prompt += f"\n\nResumo de Gastos:\n{gastos_str}"
            except Exception as e:
                st.sidebar.error(f"Erro ao processar dados de transações: {e}")
                
        else:
            st.sidebar.warning("O arquivo CSV precisa ter colunas 'categoria' e 'valor'.")
            
    # Inicializa o histórico de chat na sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []
        if system_prompt:
            st.session_state.messages.append({"role": "system", "content": system_prompt})
    elif system_prompt and len(st.session_state.messages) > 0:
        # Se já existe histórico, atualiza o system prompt (primeira mensagem) com os novos dados carregados
        if st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0]["content"] = system_prompt

    # Botão para limpar o histórico na barra lateral
    if st.sidebar.button("Limpar Histórico"):
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": system_prompt})

    # Prepara o texto para download
    historico_texto = ""
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            nome = "Você" if msg["role"] == "user" else "Caca"
            historico_texto += f"{nome}: {msg['content']}\n{'-' * 40}\n"

    st.sidebar.download_button(
        label="📥 Baixar Conversa",
        data=historico_texto,
        file_name="historico_conversa.txt",
        mime="text/plain"
    )

    # Exibe as mensagens anteriores (exceto o system prompt)
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Campo de entrada do usuário
    if prompt := st.chat_input("Digite sua dúvida financeira..."):
        # Adiciona e exibe mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gera e exibe resposta do assistente
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=MODELO,
                messages=st.session_state.messages,
                stream=True, # Resposta em tempo real
                temperature=0.7
            )
            response = st.write_stream(stream)
        
        # Salva resposta no histórico
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()