{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

raw AS (
    SELECT
        strategy_j1 AS strategy,
        COUNT(*) AS nb_tours,
        ROUND(AVG(CASE WHEN choix_j1 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_cooperation,
        ROUND(AVG(CASE WHEN choix_j1 = 'D' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_trahison,
        SUM(gain_j1) AS score_total,
        ROUND(AVG(gain_j1), 2) AS score_moyen
    FROM base
    GROUP BY strategy_j1

    UNION ALL

    SELECT
        strategy_j2 AS strategy,
        COUNT(*) AS nb_tours,
        ROUND(AVG(CASE WHEN choix_j2 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_cooperation,
        ROUND(AVG(CASE WHEN choix_j2 = 'D' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_trahison,
        SUM(gain_j2) AS score_total,
        ROUND(AVG(gain_j2), 2) AS score_moyen
    FROM base
    GROUP BY strategy_j2
)

SELECT
    strategy,
    SUM(nb_tours)                                    AS nb_tours,
    ROUND(AVG(taux_cooperation), 2)                  AS taux_cooperation,
    ROUND(AVG(taux_trahison), 2)                     AS taux_trahison,
    SUM(score_total)                                 AS score_total,
    ROUND(AVG(score_moyen), 2)                       AS score_moyen
FROM raw
GROUP BY strategy
ORDER BY taux_cooperation DESC
