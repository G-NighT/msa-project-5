# Task 4 — Реализация ETL с использованием Spring Batch

## Что сделано

Реализован POC ETL-процесса на базе Spring Batch:

- Source: `product-data.csv` (CSV файл)
- Enrichment: таблица `loyality_data` в PostgreSQL
- Target: таблица `products` в PostgreSQL

ETL логика:

1. Spring Batch читает записи из `product-data.csv`
2. Для каждой записи ищет `loyality_data` по `productSku`
3. Если запись найдена — обновляет поле `productData` значением `loyalityData`
4. Сохраняет итоговые данные в таблицу `products`

## Архитектура

- ADR: `ADR.md`
- C4 To-Be диаграмма: `c4-to-be.puml`

## Как запустить (локально)

Из директории `task-4/initial` (код/compose правился в initial):

1. Собрать jar:

```bash
./gradlew clean bootJar
```

2. Запустить PostgreSQL и приложение:

```bash
docker compose up --build
```

PostgreSQL инициализируется init-скриптами (schema + загрузка loyality_data).
После старта Spring Batch выполняет job и завершает контейнер приложения с кодом 0 (ожидаемо для batch).

## Проверка результата

Подключение к БД внутри контейнера:

```bash
docker compose exec postgresdb psql -U postgres -d productsdb -c "\dt"
docker compose exec postgresdb psql -U postgres -d productsdb -c "SELECT * FROM products;"
docker compose exec postgresdb psql -U postgres -d productsdb -c "SELECT * FROM loyality_data;"
```

## Скриншоты демонстрации

`1 - docker desktop containers.png` — контейнеры в Docker Desktop
`2 - batch logs job завершена.png` — логи Spring Batch (Transforming…, JOB FINISHED…)
`3 - список таблиц в бд.png` — список таблиц в БД (`\dt`)
`4 - таблица продуктов.png` — результат `SELECT * FROM products` (видно, что данные обновлены)
