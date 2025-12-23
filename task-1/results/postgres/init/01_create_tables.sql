-- Таблица заказов (пример для чтения из БД)
CREATE TABLE IF NOT EXISTS orders (
  order_id     BIGINT PRIMARY KEY,
  user_id      BIGINT NOT NULL,
  amount       NUMERIC(10,2) NOT NULL,
  created_at   TIMESTAMP NOT NULL
);
