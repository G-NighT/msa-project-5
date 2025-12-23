INSERT INTO orders(order_id, user_id, amount, created_at) VALUES
(1001, 501, 1200.50, NOW() - INTERVAL '2 days'),
(1002, 502,  250.00, NOW() - INTERVAL '1 day'),
(1003, 503,  999.99, NOW() - INTERVAL '3 hours')
ON CONFLICT (order_id) DO NOTHING;
