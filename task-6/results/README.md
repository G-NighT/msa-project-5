# Task6 — Настройка трейсинга запросов (traceId/spanId) + отображение в ELK

## Цель задания

1. Доработать Spring Batch-приложение так, чтобы ETL job **не запускался при старте приложения**, а запускался **по API endpoint**.
2. Реализовать клиент, который вызывает endpoint запуска job.
3. Настроить логирование запросов с трейсингом: **traceId, spanId, URI** должны попадать в логи.
4. Продемонстрировать, что эти логи **видны в Kibana (ELK)**.

---

## Что сделано

### 1) API для запуска job

Добавлен REST endpoint:

- `POST /api/jobs/import-products` — запускает Spring Batch job `importProductJob` через `JobLauncher`.

Ответ:

- `200 OK` + JSON со статусом (`COMPLETED`/`FAILED`) и `jobExecutionId`.

### 2) Клиент для запуска job

В директории `results/` лежит простой клиент:

- `run_job.py` — делает `POST` запрос на `http://localhost:8080/api/jobs/import-products`

### 3) Трейсинг в логах

Для каждого HTTP-запроса генерируются и логируются:

- `traceId`
- `spanId`
- `uri`

Поля добавляются в MDC (через HTTP filter), а `logback-spring.xml` пишет логи в JSON так, чтобы filebeat мог без проблем их собирать.

### 4) Централизованные логи в ELK

- приложение пишет логи в файл (например: `/var/log/batch/app.log`)
- filebeat читает файл и отправляет в Logstash/Elasticsearch
- в Kibana видны события и поля `traceId/spanId/uri`

---

## Как запустить

Запускать из папки `task-6/initial`

### 1) Собрать jar (если нужно)

```bash
./gradlew clean bootJar
```

### 2) Поднять стенд

```bash
docker compose up --build
```

Проверяем, что сервисы поднялись:

```bash
docker compose ps
```

---

## Полезные URL

- Приложение: `http://localhost:8080`
- Health: `http://localhost:8080/actuator/health`
- Метрики: `http://localhost:8080/actuator/prometheus`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- Kibana: `http://localhost:5601`
- Elasticsearch: `http://localhost:9200`

---

## Что важно по заданию

- Основной акцент сделан на **трейсинг в логах** и доставку логов в ELK.
- traceId/spanId генерируются на каждый запрос и проходят через весь запросный контекст.
- Kibana подтверждает, что централизованное логирование работает, и trace-поля доступны для фильтрации/поиска.
