# Task 5 — Мониторинг / Оповещения / Логирование (POC)

## Что сделано

- Spring Batch-приложение экспортирует стандартные метрики через Spring Boot Actuator + Micrometer на `/actuator/prometheus`.
- Prometheus забирает метрики (scrape) с приложения.
- Grafana отображает ключевые метрики (дашборд сохранён в JSON).
- Централизованное логирование: приложение пишет JSON-логи в файл, Filebeat отправляет их в Logstash, далее в Elasticsearch, просмотр — в Kibana.
- Оповещения: настроены правила Prometheus (пример: AppDown). Срабатывание показано остановкой контейнера `app`.

## Как запустить

Из папки `task-5/initial`:

```bash
docker compose up --build
```

## Полезные ссылки

- Проверка здоровья приложения: [http://localhost:8080/actuator/health](http://localhost:8080/actuator/health)
- Метрики в формате Prometheus: [http://localhost:8080/actuator/prometheus](http://localhost:8080/actuator/prometheus)
- Prometheus UI: [http://localhost:9090](http://localhost:9090)
- Grafana UI: [http://localhost:3000](http://localhost:3000)
- Kibana UI: [http://localhost:5601](http://localhost:5601)
- Elasticsearch API: [http://localhost:9200](http://localhost:9200)

## Артефакты в репозитории

- скриншоты с демонстрацией запуска, метрик, targets, alerts, Grafana и Kibana
- `11.2 - App dashboard-1766725189660.json` — экспортированный дашборд Grafana
- `metrics.md` — какие метрики выбраны и почему
- `logging-and-alerting.md` — обоснование логирования и оповещений
- `c4-task5-observability.puml` — обновлённая архитектура с мониторингом и логированием
