{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
)

SELECT
    tour,
    ROUND(AVG(CASE WHEN choix_j1 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_coop_j1,
    ROUND(AVG(CASE WHEN choix_j2 = 'C' THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_coop_j2,
    ROUND(AVG(CASE WHEN cooperation_mutuelle THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_coop_mutuelle,
    ROUND(AVG(CASE WHEN trahison_j1 THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_trahison_j1,
    ROUND(AVG(CASE WHEN trahison_j2 THEN 1.0 ELSE 0.0 END) * 100, 2) AS taux_trahison_j2,
    ROUND(AVG(gain_j1), 2) AS gain_moyen_j1,
    ROUND(AVG(gain_j2), 2) AS gain_moyen_j2
FROM base
GROUP BY tour
ORDER BY tour
