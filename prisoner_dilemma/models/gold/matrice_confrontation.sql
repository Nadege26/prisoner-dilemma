{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

j1 AS (
    SELECT strategy_j1 AS strategy_a, strategy_j2 AS strategy_b,
           ROUND(AVG(gain_j1), 2) AS score_moyen
    FROM base
    GROUP BY strategy_j1, strategy_j2
),

j2 AS (
    SELECT strategy_j2 AS strategy_a, strategy_j1 AS strategy_b,
           ROUND(AVG(gain_j2), 2) AS score_moyen
    FROM base
    GROUP BY strategy_j2, strategy_j1
)

SELECT * FROM j1
UNION ALL
SELECT * FROM j2
ORDER BY strategy_a, strategy_b
