{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

scores AS (
    SELECT
        strategy_j1 AS strategy_a,
        strategy_j2 AS strategy_b,
        ROUND(AVG(gain_j1), 2) AS score_a,
        ROUND(AVG(gain_j2), 2) AS score_b
    FROM base
    GROUP BY strategy_j1, strategy_j2
)

SELECT
    strategy_a,
    strategy_b,
    score_a,
    score_b,
    CASE
        WHEN score_a >= 2.5 AND score_b >= 2.5 THEN 'Equilibre cooperatif'
        WHEN score_a <= 1.5 AND score_b <= 1.5 THEN 'Equilibre de trahison mutuelle'
        WHEN score_a >= 3.0 AND score_b <= 1.0 THEN 'Exploitation'
        WHEN score_a <= 1.0 AND score_b >= 3.0 THEN 'Exploitation inverse'
        ELSE 'Equilibre mixte'
    END AS type_equilibre
FROM scores
ORDER BY strategy_a, strategy_b
