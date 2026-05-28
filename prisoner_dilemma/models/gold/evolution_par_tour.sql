{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM read_parquet('/home/nadege/Downloads/prisoner-dilemma/silver/tournament_clean.parquet')
)

SELECT
    tour,
    match,
    strategy_j1,
    strategy_j2,
    choix_j1,
    choix_j2,
    gain_j1,
    gain_j2,
    score_j1,
    score_j2,
    cooperation_mutuelle,
    trahison_j1,
    trahison_j2
FROM base
ORDER BY match, tour
