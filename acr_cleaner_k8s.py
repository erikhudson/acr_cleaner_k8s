import subprocess
import json
import os

# Função para obter os Azure Container Registries disponíveis
def get_acrs():
    command = "az acr list --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao listar ACRs: {result.stderr}")
        return []
    return json.loads(result.stdout)

# Função para obter os repositórios de um ACR
def get_repositories(acr_name):
    command = f"az acr repository list --name {acr_name} --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao listar repositórios no ACR {acr_name}: {result.stderr}")
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da lista de repositórios para {acr_name}: {e}")
        return []

# Função para obter as tags de um repositório
def get_tags(acr_name, repository):
    command = f"az acr repository show-tags --name {acr_name} --repository {repository} --orderby time_desc --output json"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao listar tags para {repository} no ACR {acr_name}: {result.stderr}")
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON das tags para {repository} no ACR {acr_name}: {e}")
        return []

# Função para deletar tags antigas
def delete_tags(acr_name, repository, tags_to_keep):
    tags = get_tags(acr_name, repository)
    if len(tags) > tags_to_keep:
        tags_to_delete = tags[tags_to_keep:]
        for tag in tags_to_delete:
            command = f"az acr repository delete --name {acr_name} --image {repository}:{tag} --yes"
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                print(f"Deleted {repository}:{tag}")
            else:
                print(f"Erro ao deletar {repository}:{tag}: {result.stderr}")
    else:
        print(f"No tags to delete for {repository}")

# Função de autenticação via Service Principal
def login_with_service_principal():
    client_id = os.getenv("SP_APP_ID")
    client_secret = os.getenv("SP_PASSWORD")
    tenant_id = os.getenv("SP_TENANT_ID")

    if not client_id or not client_secret or not tenant_id:
        print("As credenciais do Service Principal não foram definidas corretamente.")
        return False

    command = f"az login --service-principal --username {client_id} --password {client_secret} --tenant {tenant_id}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Erro ao autenticar com Service Principal: {result.stderr}")
        return False

    print("Autenticado com sucesso usando Service Principal")
    return True

# Função principal para executar o processo de limpeza
def main():
    # Primeiro, tenta autenticar com o Service Principal
    if not login_with_service_principal():
        print("Falha na autenticação com Service Principal. Encerrando...")
        exit(1)

    # Obtém os nomes dos ACRs e o número de tags a manter
    acr_names = os.getenv("ACR_NAMES", "CSStagAcr").split(',')
    tags_to_keep = int(os.getenv("TAGS_TO_KEEP", 3))

    # Executa o processo de limpeza para cada ACR
    for acr_name in acr_names:
        print(f"Iniciando limpeza para o ACR: {acr_name}")
        repositories = get_repositories(acr_name)
        if not repositories:
            print(f"Nenhum repositório encontrado no ACR {acr_name}")
            continue
        for repo in repositories:
            print(f"Limpando repositório: {repo}")
            delete_tags(acr_name, repo, tags_to_keep)
        print(f"Limpeza concluída para o ACR: {acr_name}")

# Execução do script
if __name__ == "__main__":
    main()