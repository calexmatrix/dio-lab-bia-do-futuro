# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala a dependência necessária
RUN pip install openai streamlit pandas plotly pytest pytest-html

# O comando de execução será definido no docker-compose ou via terminal
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]
