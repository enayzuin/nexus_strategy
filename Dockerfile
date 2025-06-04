# Usa uma imagem oficial do Python como base
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de requirements
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código fonte para dentro do container
COPY . .

# Expõe a porta 8000 (igual a do Flask)
EXPOSE 8000

# Comando para iniciar o app
CMD ["python", "app/app.py"]
