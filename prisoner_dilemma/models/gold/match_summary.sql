{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
),

resultats AS (
    SELECT
        match,
        strategy_j1,
        strategy_j2,
        SUM(gain_j1)  AS score_final_j1,
        SUM(gain_j2)  AS score_final_j2,
        COUNT(*)      AS nb_tours,
        ROUND(AVG(CASE WHEN choix_j1 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS coop_j1,
        ROUND(AVG(CASE WHEN choix_j2 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS coop_j2,
        ROUND(AVG(CASE WHEN cooperation_mutuelle THEN 1.0 ELSE 0.0 END) * 100, 2) AS coop_mutuelle_pct
    FROM base
    GROUP BY match, strategy_j1, strategy_j2
)

SELECT
    match,
    strategy_j1,
    strategy_j2,
    score_final_j1,
    score_final_j2,
    nb_tours,
    coop_j1,
    coop_j2,
    coop_mutuelle_pct,
    CASE
        WHEN score_final_j1 > score_final_j2 THEN strategy_j1
        WHEN score_final_j2 > score_final_j1 THEN strategy_j2
        ELSE 'égalité'
    END AS gagnant
FROM resultats
ORDER BY match
