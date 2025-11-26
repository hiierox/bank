# Мониторинг
Если еще кто-то будет смотреть, то вот нюансы:
_Метрики_.  Для сервисов скоринга и флоу доходят до графаны, но почему-то не отображаются.  
_Трейсинг_. Из консьюмера пришлось убрать создание спана, так как с ним консьюмер отказывается работать, поэтому прямого трейса скоринг-кафка-дата-бд нет
# Развертывание в kubernetes
(сейчас запущены все поды)
_Склонировать репозиторий на вм_
### Применение манифестов
Из директории main_shift_project  
Имя релиза = имя пода
#### user-data-service
```bash
kubectl apply -f services/user-data-service/manifests/secret.yaml
helm install user-data-service-kbatrakov services/user-data-service/user-data-service-chart
```
Время ожидания готовности в зависимости от занятости ВМ 1-3 минуты
#### scoring-service
```bash
helm install scoring-service-kbatrakov services/scoring-service/scoring-service-chart
```

#### flow-selection-service
```bash
kubectl apply -f services/flow-service/manifests/secret.yaml
helm install flow-selection-service-kbatrakov services/flow-service/flow-service-chart
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