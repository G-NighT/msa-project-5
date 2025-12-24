# Task 3 — Distributed Scheduling с k8s CronJob

## Идея решения

Используем Kubernetes CronJob для ежедневного запуска экспортёра данных из PostgreSQL в CSV.
Для демонстрации экспортируем одну таблицу `shipments`.

- CronJob запускается каждый день в 20:00: `schedule: "0 20 * * *"`
- Экспорт выполняется через `COPY table TO STDOUT WITH CSV HEADER` (psycopg2), что подходит для больших таблиц (потоково, без загрузки в память).
- CSV складывается в PVC (`export-data`), а также первые строки печатаются в логи (удобно для скриншотов).

## Что в репозитории

- `exporter/` — Docker-образ экспортёра (Python)
- `k8s/` — манифесты для MiniKube: Postgres + CronJob + PVC

## Запуск в MiniKube

### 1) Старт MiniKube

```bash
minikube start
kubectl create ns analytics || true
```

### 2) Собрать образ экспортёра внутри MiniKube

```bash
eval $(minikube docker-env)
docker build -t shipment-exporter:0.1 ./exporter
```

### 3) Применить манифесты

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-postgres-pvc.yaml
kubectl apply -f k8s/02-postgres-initdb-configmap.yaml
kubectl apply -f k8s/03-postgres-deployment.yaml
kubectl apply -f k8s/04-export-pvc.yaml
kubectl apply -f k8s/05-cronjob-export.yaml
```

### 4) Дождаться готовности Postgres

```bash
kubectl -n analytics rollout status deploy/postgres
```

### 5) Запуск Job вручную из CronJob (чтобы не ждать 20:00)

```bash
kubectl -n analytics create job --from=cronjob/shipments-export shipments-export-manual-1
kubectl -n analytics wait --for=condition=complete job/shipments-export-manual-1 --timeout=120s
```

### 6) Посмотреть логи экспортёра

```bash
POD=$(kubectl -n analytics get pods -l job-name=shipments-export-manual-1 -o jsonpath='{.items[0].metadata.name}')
kubectl -n analytics logs $POD
```

В логах видно:

- путь к CSV
- первые строки CSV
