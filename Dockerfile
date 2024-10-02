FROM python:3.12.3-slim

WORKDIR /app

COPY . /app

# Instalando dependências do sistema (Azure CLI e outras ferramentas necessárias)
RUN apt-get update && apt-get install -y curl apt-transport-https lsb-release gnupg \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg \
    && install -o root -g root -m 644 microsoft.gpg /usr/share/keyrings/ \
    && sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list' \
    && apt-get update && apt-get install -y azure-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm microsoft.gpg

#RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "acr_cleaner_k8s.py"]