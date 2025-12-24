## Верхнеуровневый план конфигурации и имплементации

### Шаг 1. Подготовить экспортёр

- Реализовать маленький сервис/скрипт (Python/Go/Java), который:

  - подключается к Postgres (SSL/secret),
  - выполняет запросы (с JOIN),
  - формирует CSV и (опционально) XLSX,
  - пишет файлы локально во временный каталог,
  - загружает файлы в Object Storage (S3/GCS/MinIO),
  - возвращает ненулевой exit code при ошибке (для алертов/ретраев).

- Добавить параметры через env:

  - `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`
  - `STORAGE_BUCKET`, `STORAGE_PREFIX`
  - `OUTPUT_FORMATS=csv,xlsx`
  - `RUN_DATE` (по умолчанию текущая)

### Шаг 2. Упаковать в Docker образ

- Multi-stage build (если Go/Java) или лёгкий python-образ.
- Логи в stdout/stderr.
- Healthcheck не обязателен (т.к. job), но можно.

### Шаг 3. Настроить доступы и секреты

- Kubernetes Secret для Postgres credentials.
- Secret/IRSA/Workload Identity для доступа к Object Storage.
- ConfigMap для не секретных настроек (bucket/prefix/форматы).

### Шаг 4. Создать CronJob манифест

- `schedule: "0 6 * * *"`
- `concurrencyPolicy: Forbid` (чтобы не было параллельных запусков)
- `startingDeadlineSeconds` (например, 300)
- `successfulJobsHistoryLimit / failedJobsHistoryLimit`
- `backoffLimit` (ретраи на уровне job)
- requests/limits по CPU/RAM (малые)

### Шаг 5. Хранение результатов

- Object Storage, как единый источник истины для прайсов.
- (Опционально) писать в Postgres таблицу `export_runs`:
  - run_id, дата, статус, количество файлов, ошибки.

### Шаг 6. Уведомления

- Вариант A: экспортёр сам отправляет email/сообщение (SMTP/Slack webhook).
- Вариант B: алерты по метрикам/событиям job в Prometheus Alertmanager.

### Шаг 7. Наблюдаемость

- Логи: stdout → Fluent Bit/Vector → ELK.
- Метрики (опционально): `export_duration_seconds`, `export_files_total`, `export_failed_total`.
- Дашборд: успех/ошибки по дням, длительность, объём файлов.

### Шаг 8. Тестирование/валидация

- Прогон вручную: создать `job` из шаблона CronJob.
- Проверить:

  - файлы появились в storage,
  - формат CSV/XLS корректный,
  - уведомление пришло,
  - ошибки корректно фейлят job.
