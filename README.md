
# ACR Cleaner Deployment Guide

Este documento fornece as instruções detalhadas para a configuração e execução de um processo de limpeza automatizada do **Azure Container Registry (ACR)** usando um **Service Principal** e Kubernetes.

## 1. Pré-requisitos

- **Azure CLI** instalado e autenticado.
- **Cluster AKS** ativo e configurado.
- Acesso ao **Azure Container Registry (ACR)**.
- **kubectl** configurado e com acesso ao seu cluster AKS.

## 2. Criando um Service Principal

Primeiro, crie um **Service Principal** com as permissões necessárias para acessar e deletar imagens do **ACR**.

### Comando para criar o Service Principal:

```bash
az ad sp create-for-rbac --name "acr-cleaner-sp" --role "AcrPull" --scopes /subscriptions/<subscription-id>/resourceGroups/RG-CS-Staging/providers/Microsoft.ContainerRegistry/registries/CSStagAcr
```

Este comando cria o Service Principal com a permissão de leitura (**AcrPull**) para listar os repositórios e imagens no ACR. Ele retornará as seguintes informações:

- **appId**: ID do aplicativo (Service Principal)
- **password**: Senha do aplicativo (Client Secret)
- **tenant**: ID do locatário (Tenant ID)

### Concedendo permissão de deletar imagens:

Após a criação, adicione a permissão de deletar (**AcrDelete**) para o Service Principal:

```bash
az role assignment create --assignee <appId> --role "AcrDelete" --scope /subscriptions/<subscription-id>/resourceGroups/RG-CS-Staging/providers/Microsoft.ContainerRegistry/registries/CSStagAcr
```

Substitua `<appId>` pelo valor de `appId` retornado no passo anterior.

Para Listar as roles existentes:

```bash
az role assignment list --assignee  --scope /subscriptions/<subscription-id>/resourceGroups/RG-CS-Staging/providers/Microsoft.ContainerRegistry/registries/CSStagAcr
```

## 3. Configurando o Kubernetes

### 3.1 Atualize o arquivo YAML do CronJob

No arquivo `acr-cleaner-cronjob.yaml`, certifique-se de que as credenciais do **Service Principal** estejam configuradas como variáveis de ambiente:

```yaml
env:
  - name: SP_APP_ID
    value: "<appId>"
  - name: SP_PASSWORD
    value: "<password>"
  - name: SP_TENANT_ID
    value: "<tenantId>"
```

Substitua os valores `<appId>`, `<password>` e `<tenantId>` pelos valores retornados na criação do **Service Principal**.

### 3.2 Aplicando o CronJob

Com o arquivo atualizado, aplique o **CronJob** no seu cluster **AKS**:

```bash
kubectl apply -f acr-cleaner-cronjob.yaml
```

### 3.3 Testando manualmente

Para testar o Job imediatamente, você pode criar um **Job** manual a partir do CronJob:

```bash
kubectl create job --from=cronjob/acr-cleaner-cronjob acr-cleaner-test-job
```

### 3.4 Verificando os logs

Após criar o Job, você pode verificar os logs do pod criado para garantir que o processo de limpeza do ACR está funcionando corretamente:

```bash
kubectl logs <acr-cleaner-pod-name>
```

Substitua `<acr-cleaner-pod-name>` pelo nome do pod retornado no comando anterior.

## 4. Verificando no ACR

Após a execução do Job, você pode verificar diretamente no **ACR** se as imagens antigas foram removidas conforme esperado. Para listar as tags restantes de um repositório específico, use:

```bash
az acr repository show-tags --name CSStagAcr --repository <repository-name> --output table
```

Substitua `<repository-name>` pelo nome do repositório que deseja verificar.

## Conclusão

Seguindo esses passos, você terá um processo automatizado de limpeza de imagens antigas no ACR utilizando o Kubernetes e um Service Principal para autenticação.
