# 🎮 Prisoner Dilemma — Pipeline Data Engineering

## Contexte
Simulation du dilemme du prisonnier itératif inspiré du tournoi d'Axelrod (1981).
Pipeline data complet : génération → Bronze → Silver → Gold.

## Stack technique
- **Python + Polars** → simulation et transformation
- **Ollama (llama3)** → agents IA (empathique, calculateur)
- **dbt + DuckDB** → couche Gold (8 tables d'indicateurs)
- **Prefect** → orchestration du pipeline
- **Parquet (zstd)** → stockage Bronze/Silver

## Architecture

## Stratégies simulées
| Stratégie | Type | Description |
|---|---|---|
| always_cooperate | Codée | Coopère toujours |
| always_defect | Codée | Trahit toujours |
| tit_for_tat | Codée | Copie le dernier coup adverse |
| grim_trigger | Codée | Trahit après 1ère trahison définitivement |
| random | Codée | Choisit aléatoirement |
| empathique | 🤖 IA (llama3) | Profil coopératif et pardonnant |
| calculateur | 🤖 IA (llama3) | Profil opportuniste et rationnel |

## Tables Gold (DuckDB)
| Table | Description |
|---|---|
| classement | Ranking final des stratégies |
| cooperation_rate | Taux de coopération par stratégie |
| evolution_par_tour | Evolution comportement tour par tour |
| match_summary | Résumé et gagnant de chaque match |
| comportement_par_tour | Tendance temporelle de coopération |
| matrice_confrontation | Score de chaque stratégie contre chaque autre |
| indicateurs_avances | Taux pardon, trahison consécutive, réactivité |
| nash_equilibre | Type d'équilibre pour chaque paire de stratégies |

## Installation

### Prérequis
- Python 3.12+
- Ollama avec llama3 (`ollama pull llama3`)
- dbt-duckdb

### Setup
```bash
git clone https://github.com/TON_USERNAME/prisoner-dilemma.git
cd prisoner-dilemma
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancer le pipeline complet
```bash
# 1. Simulation (Bronze)
python3 simulate.py

# 2. Transformation Silver
python3 transform_silver.py

# 3. Gold dbt
cd prisoner_dilemma
dbt run
cd ..

# 4. Orchestration complète avec Prefect
python3 pipeline_prefect.py
```

## Résultats (stratégies codées uniquement)
| Rang | Stratégie | Score total | Taux coopération |
|---|---|---|---|
| 1 | always_defect | 1996 | 0% |
| 2 | grim_trigger | 1946 | 33.67% |
| 3 | tit_for_tat | 1834 | 61.88% |
| 4 | always_cooperate | 1527 | 100% |
| 5 | random | 1437 | 48.38% |

## Conclusion
Sans agents IA, `always_defect` domine à court terme.
Avec agents IA (Ollama), on s'attend à voir émerger des comportements
coopératifs similaires à la conclusion d'Axelrod :
**la coopération émerge spontanément à long terme.**
