{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

avec_precedent AS (
    SELECT *,
        LAG(choix_j1) OVER (PARTITION BY match ORDER BY tour) AS choix_j1_precedent,
        LAG(choix_j2) OVER (PARTITION BY match ORDER BY tour) AS choix_j2_precedent
    FROM base
)

SELECT
    strategy_j1 AS strategy,
    ROUND(AVG(CASE
        WHEN choix_j1_precedent = 'D' AND choix_j2_precedent = 'D'
        AND choix_j1 = 'C' THEN 1.0 ELSE 0.0
    END) * 100, 2) AS taux_pardon,
    ROUND(AVG(CASE
        WHEN choix_j1_precedent = 'D' AND choix_j1 = 'D' THEN 1.0 ELSE 0.0
    END) * 100, 2) AS trahison_consecutive,
    ROUND(AVG(CASE
        WHEN choix_j2_precedent = 'D' AND choix_j1 = 'D' THEN 1.0 ELSE 0.0
    END) * 100, 2) AS reactivite_trahison
FROM avec_precedent
WHERE choix_j1_precedent IS NOT NULL
GROUP BY strategy_j1
ORDER BY taux_pardon DESC
