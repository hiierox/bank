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
## Проверка работоспособности
Пробросить порт сервисов на localhost ВМ
```bash
kubectl port-forward <pod_name> <vm_port>:8000
```
Затем пробросить с ВМ на локальную машину либо через вкладку ports в vscode, либо через ssh:
```bash
ssh -L <local_port>:localhost:<vm_port> username@vm_ip
```