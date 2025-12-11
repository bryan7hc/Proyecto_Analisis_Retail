-- sql/create_indexes.sql
-- Ejecutar en psql o pgAdmin
CREATE INDEX IF NOT EXISTS idx_superstore_order_date ON superstore_clean (order_date);
CREATE INDEX IF NOT EXISTS idx_superstore_order_year ON superstore_clean (order_year);
CREATE INDEX IF NOT EXISTS idx_superstore_region ON superstore_clean (region);
CREATE INDEX IF NOT EXISTS idx_superstore_category ON superstore_clean (category);
CREATE INDEX IF NOT EXISTS idx_superstore_product ON superstore_clean (product_name);
CREATE INDEX IF NOT EXISTS idx_superstore_customer ON superstore_clean (customer_id);
0