
CREATE TABLE IF NOT EXISTS streaming_predictions (
    id SERIAL PRIMARY KEY,
    benefit_per_order DOUBLE PRECISION,
    sales_per_customer DOUBLE PRECISION,
    order_item_quantity INTEGER,
    order_item_product_price DOUBLE PRECISION,
    order_item_discount DOUBLE PRECISION,
    order_item_total DOUBLE PRECISION,
    order_profit_per_order DOUBLE PRECISION,
    distance DOUBLE PRECISION,
    category_name VARCHAR(100),
    order_region VARCHAR(100),
    shipping_mode VARCHAR(50),
    actual_late_delivery INTEGER,
    predicted_late_delivery DOUBLE PRECISION,
    event_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_event_time ON streaming_predictions(event_time);
CREATE INDEX IF NOT EXISTS idx_order_region ON streaming_predictions(order_region);
CREATE INDEX IF NOT EXISTS idx_category ON streaming_predictions(category_name);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE streaming_predictions TO admin;
GRANT ALL PRIVILEGES ON SEQUENCE streaming_predictions_id_seq TO admin;