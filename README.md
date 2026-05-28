# 🎮 Prisoner Dilemma — Pipeline Data Engineering

> Reproduction du tournoi d'Axelrod (1981) avec agents IA locaux (Ollama/llama3)

## 📖 Contexte

En 1981, le politologue **Robert Axelrod** organisa un tournoi où des programmes
s'affrontaient dans le **dilemme du prisonnier itératif**.
Résultat inattendu : la stratégie la plus simple — **Tit for Tat** — surclassa toutes les autres,
prouvant que la coopération émerge spontanément à long terme.

Ce projet reproduit ce tournoi avec :
- 5 **stratégies codées** (algorithmiques)
- 2 **agents IA** pilotés par llama3 via Ollama

---

## 🏗️ Architecture

---

## 🧠 Stratégies simulées

| Stratégie | Type | Description |
|---|---|---|
| `always_cooperate` | Codée | Coopère toujours (C) |
| `always_defect` | Codée | Trahit toujours (D) |
| `tit_for_tat` | Codée | Copie le dernier coup adverse |
| `grim_trigger` | Codée | Trahit définitivement après 1ère trahison |
| `random` | Codée | Choisit C ou D aléatoirement |
| `empathique` | 🤖 IA (llama3) | Profil coopératif et pardonnant |
| `calculateur` | 🤖 IA (llama3) | Profil opportuniste et rationnel |

---

## 📊 Tables Gold (DuckDB)

| Table | Description |
|---|---|
| `classement` | Ranking final des stratégies |
| `cooperation_rate` | Taux de coopération par stratégie |
| `evolution_par_tour` | Evolution comportement tour par tour |
| `match_summary` | Résumé et gagnant de chaque match |
| `comportement_par_tour` | Tendance temporelle de coopération |
| `matrice_confrontation` | Heatmap score de chaque stratégie vs chaque autre |
| `indicateurs_avances` | Taux pardon, trahison consécutive, réactivité |
| `nash_equilibre` | Type d'équilibre pour chaque paire de stratégies |

---

## 🛠️ Stack technique

| Outil | Rôle |
|---|---|
| Python + Polars | Simulation et transformation |
| Ollama (llama3) | Agents IA locaux |
| dbt + DuckDB | Couche Gold |
| Prefect | Orchestration pipeline |
| Streamlit + Plotly | Dashboard de visualisation |
| Parquet (zstd) | Stockage Bronze/Silver |

---

## 🚀 Installation et utilisation

### Prérequis
- Python 3.12+
- Ollama avec llama3 : `ollama pull llama3`
- dbt-duckdb

### Setup
```bash
git clone https://github.com/Nadege26/prisoner-dilemma.git
cd prisoner-dilemma
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Lancer le pipeline complet
```bash
# Option 1 — Étape par étape
python3 simulate.py          # Bronze
python3 transform_silver.py  # Silver
cd prisoner_dilemma && dbt run && cd ..  # Gold

# Option 2 — Pipeline orchestré avec Prefect
python3 pipeline_prefect.py
```

### Lancer le dashboard
```bash
streamlit run dataviz/dashboard.py
```

---

## 📈 Résultats (avec agents IA)

| Rang | Stratégie | Type | Score total | Taux coopération |
|---|---|---|---|---|
| 1 | always_defect | Codée | ~2000 | 0% |
| 2 | grim_trigger | Codée | ~1950 | ~34% |
| 3 | tit_for_tat | Codée | ~1834 | ~62% |
| 4 | calculateur | 🤖 IA | ~variable | ~variable |
| 5 | empathique | 🤖 IA | ~variable | ~variable |
| 6 | always_cooperate | Codée | ~1527 | 100% |
| 7 | random | Codée | ~1437 | ~48% |

---

## 🔬 Conclusions

- **Court terme** : `always_defect` domine en exploitant les coopérateurs
- **Long terme** : `tit_for_tat` serait optimal (conclusion d'Axelrod)
- **Agents IA** : `empathique` tend vers la coopération, `calculateur` vers la trahison opportuniste
- **Equilibre de Nash** : émerge naturellement entre `tit_for_tat`, `grim_trigger` et `always_cooperate`

---

## 📁 Structure du projet
