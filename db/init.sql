CREATE TABLE IF NOT EXISTS sales (
    id SERIAL PRIMARY KEY,
    city VARCHAR(50),
    sale_date DATE,
    amount NUMERIC(10,2)
);

INSERT INTO sales (city, sale_date, amount) VALUES
('Prague', '2025-10-01', 1200),
('Brno', '2025-10-02', 800),
('Ostrava', '2025-10-03', 450),
('Prague', '2025-10-04', 950),
('Brno', '2025-10-05', 700),
('Ostrava', '2025-10-06', 620),
('Prague', '2025-11-01', 1400),
('Brno', '2025-11-02', 900),
('Ostrava', '2025-11-03', 550);
