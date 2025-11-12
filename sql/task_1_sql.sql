-- Описание:
--  • Топ-3 города по продажам за каждый месяц
--  • Доля города от суммы продаж месяца (в процентах)
--  • Нарастающий итог продаж по городам (накопительное значение по месяцам для каждого города)
--
--  Я выбрал CTE и оконные функции: сначала агрегирую по (месяц, город),
--  затем считаю месячные итоги, дальше — ранжирую и считаю cumulative sum.
--  ROUND использую только на финальной выборке, чтобы проценты выглядели аккуратно.

WITH month_city AS (
  SELECT
    date_trunc('month', s.sale_date)::date AS month,
    u.city,
    SUM(s.amount) AS city_month_amount
  FROM sales s
  JOIN users u ON u.id = s.user_id
  GROUP BY 1, 2
),
month_total AS (
  SELECT
    month,
    SUM(city_month_amount) AS month_total_amount
  FROM month_city
  GROUP BY 1
),
ranked AS (
  SELECT
    mc.month,
    mc.city,
    mc.city_month_amount,
    mt.month_total_amount,
    100.0 * mc.city_month_amount / NULLIF(mt.month_total_amount, 0) AS city_share_pct,
    ROW_NUMBER() OVER (PARTITION BY mc.month ORDER BY mc.city_month_amount DESC) AS rn,
    -- Нарастающий итог по городам: для каждого города суммируем его продажи по месяцам
    SUM(mc.city_month_amount) OVER (
      PARTITION BY mc.city
      ORDER BY mc.month
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS city_cumulative_amount
  FROM month_city mc
  JOIN month_total mt USING (month)
)
SELECT
  month,
  city,
  city_month_amount,
  month_total_amount,
  ROUND(city_share_pct, 2) AS city_share_pct,
  city_cumulative_amount
FROM ranked
WHERE rn <= 3
ORDER BY month, city_month_amount DESC, city;
