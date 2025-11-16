# Развертывание в kubernetes

_Склонировать репозиторий на вм_
### Применение манифестов
Из директории main_shift_project
#### user-data-service
```bash
kubectl apply -f services/user-data-service/manifests/secret.yaml
kubectl apply -f services/user-data-service/manifests/configmap.yaml 
kubectl apply -f services/user-data-service/manifests/service.yaml 
kubectl apply -f services/user-data-service/manifests/deployment.yaml --validate=false
```
Время ожидания готовности в зависимости от занятости ВМ 1-3 минуты
#### scoring-service
```bash
kubectl apply -f services/scoring-service/manifests/configmap.yaml 
kubectl apply -f services/scoring-service/manifests/service.yaml 
kubectl apply -f services/scoring-service/manifests/deployment.yaml --validate=false
```

#### flow-selection-service
```bash
kubectl apply -f services/flow-service/manifests/secret.yaml
kubectl apply -f services/flow-service/manifests/configmap.yaml 
kubectl apply -f services/flow-service/manifests/service.yaml 
kubectl apply -f services/flow-service/manifests/deployment.yaml --validate=false
```
## Тестирование
У меня не возникли сложности с пробросом портов на локальную машину, поэтому на случай, если у вас тоже возникнут с этим проблемы - вот быстрые варианты запросов:
##### Просто через curl на ВМ по IP пода, полученного через describe

```bash
curl -X 'GET' \
  'http://<POD_IP>:8000/ready' \
  -H 'accept: application/json'
```  

##### Либо вариант поинтереснее через скрипт:
1. В bash вставляется сам скрипт
```bash
PYTHON_COMMAND="""
import asyncio
import httpx
import sys

async def request_to_any_address(url):
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
            print(f'URL: {url}, status: {response.status_code}, body: {response.text}')
            if response.status_code != 200:
                sys.exit(1)
    except Exception as e:
        print(f'URL: {url}, ERROR: {e}')
        sys.exit(1)

if __name__ == '__main__':
    target_url = sys.argv[1]
    asyncio.run(request_to_any_address(target_url))
"""
```
2. `kubectl exec <pod_name> --python3 -c "$PYTHON_COMMAND" "http://<GET запрос к любому сервису>`
где <pod_name> это имя пода от которого будут идти запросы
Пример url: http://user-data-service-kbatrakov:8000/api/products