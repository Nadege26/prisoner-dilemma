{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

scores AS (
    SELECT strategy_j1 AS strategy, SUM(gain_j1) AS score_total, COUNT(*) AS nb_tours
    FROM base GROUP BY strategy_j1
    UNION ALL
    SELECT strategy_j2 AS strategy, SUM(gain_j2) AS score_total, COUNT(*) AS nb_tours
    FROM base GROUP BY strategy_j2
),

aggregated AS (
    SELECT
        strategy,
        SUM(score_total)              AS score_total,
        SUM(nb_tours)                 AS nb_tours,
        ROUND(SUM(score_total) * 1.0 / SUM(nb_tours), 2) AS score_moyen_par_tour
    FROM scores
    GROUP BY strategy
)

SELECT
    ROW_NUMBER() OVER (ORDER BY score_total DESC) AS rang,
    strategy,
    score_total,
    nb_tours,
    score_moyen_par_tour
FROM aggregated
ORDER BY score_total DESC
