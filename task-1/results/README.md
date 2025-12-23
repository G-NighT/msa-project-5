# Task 1 — Выбор и реализация решения для пакетной обработки данных

## Выбранное решение

**Apache Airflow** как инструмент оркестрации пакетной обработки данных (batch pipelines).

### Почему Airflow

- Поддерживает построение гибких пайплайнов (DAG) с ветвлениями, условиями, группировками шагов.
- Есть встроенный UI, история запусков, логи, SLA/алерты и интеграция с мониторингом.
- Встроенные механизмы **retry**, **fallback** через ветвления/trigger_rule, колбэки.
- Встроенные уведомления (в т.ч. email) и богатая экосистема операторов/провайдеров.
- Подходит для объёма ~1 млн записей за запуск: Airflow оркестрирует шаги, а тяжёлые вычисления могут выполняться во внешних системах (Spark/BigQuery/Redshift).

## Интеграции с источниками/системами

### BigQuery

Используется провайдер Google (`apache-airflow-providers-google`):

- `BigQueryInsertJobOperator`, `BigQueryGetDataOperator`
- `BigQueryHook`
  Это ускоряет разработку за счёт готовых операторов/хуков.

### Redshift

Используется провайдер Amazon (`apache-airflow-providers-amazon`):

- `RedshiftSQLOperator`, `RedshiftDataOperator`
  Также возможен доступ через `PostgresHook` (совместимый протокол).

### Kafka

Возможны интеграции через провайдер Kafka (`apache-airflow-providers-apache-kafka`) и/или подход:

- сенсоры/таски на чтение/публикацию
- запуск DAG по событию извне через REST API Airflow (если консьюмер Kafka работает отдельным сервисом)

### Spark

Используется провайдер Spark (`apache-airflow-providers-apache-spark`):

- `SparkSubmitOperator`
  Также часто применяют `KubernetesPodOperator` для Spark on K8s.

## Ветвления, условия и event-triggers

- Ветвления и условия: `BranchPythonOperator`, `ShortCircuitOperator`, `trigger_rule`.
- Триггеры: расписание, ручной запуск, запуск через REST API, сенсоры (файл/таблица/сообщение), dataset-triggers (в зависимости от версии Airflow).

## Retry / fallback / email

- Retry: `retries`, `retry_delay`, `retry_exponential_backoff`.
- Fallback: альтернативные ветки + `trigger_rule`.
- Email: `EmailOperator` и/или `email_on_failure`, `email_on_retry`.

## Развёртывание в облаке

Возможные варианты:

1. Managed Airflow (MWAA / Cloud Composer) — снижает затраты на эксплуатацию.
2. Kubernetes + Helm Chart:
   - webserver/scheduler/workers (KubernetesExecutor или CeleryExecutor),
   - секреты через K8s Secrets/Vault/Secret Manager,
   - логи в объектное хранилище и централизованный сбор (ELK/Cloud logging).

---

# POC (локальная демонстрация)

Локально поднято через Docker Compose:

- Airflow (webserver + scheduler)
- PostgreSQL (источник данных)
- MailHog (SMTP-сервер для перехвата email)

Пайплайн `batch_poc` содержит:

1. Чтение заказов из Postgres
2. Чтение статусов доставок из CSV
3. Анализ + объединение данных и генерация отчёта
4. Ветвление по условию (есть ли FAILED)
5. Email-уведомление при успешном завершении
6. Retry-политика на “нестабильном” шаге (падает 1 раз, затем проходит на retry)

## Как запустить

Из директории `task-1/results/`:

```bash
docker compose up airflow-init
docker compose up -d
```
