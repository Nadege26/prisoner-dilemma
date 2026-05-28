import random
import uuid
import requests
import polars as pl
from datetime import datetime

# ── Paramètres ────────────────────────────────────────────────────────────────
NB_TOURS    = 200
NB_TOURS_AI = 50
RUN_ID      = str(uuid.uuid4())[:8]
TIMESTAMP   = datetime.now().isoformat()
OLLAMA_URL  = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"

# ── Matrice de gains ──────────────────────────────────────────────────────────
GAINS = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1),
}

# ── Stratégies codées ─────────────────────────────────────────────────────────

def always_cooperate(history):
    return "C"

def always_defect(history):
    return "D"

def tit_for_tat(history):
    if not history:
        return "C"
    return history[-1]["opponent_choice"]

def grim_trigger(history):
    for h in history:
        if h["opponent_choice"] == "D":
            return "D"
    return "C"

def random_strategy(history):
    return random.choice(["C", "D"])

# ── Agents Ollama ─────────────────────────────────────────────────────────────

def ollama_decision(profile: str, history: list) -> str:
    last_moves = ""
    if history:
        last = history[-3:]
        last_moves = "\n".join([
            f"Tour {i+1}: moi={h['my_choice']}, adversaire={h['opponent_choice']}"
            for i, h in enumerate(last)
        ])
    else:
        last_moves = "Premier tour, pas d'historique."

    prompt = f"""Tu joues au dilemme du prisonnier itératif.
Profil : {profile}
Historique récent :
{last_moves}

Règles :
- C = Coopérer (gain mutuel modéré)
- D = Trahir (gain max si l'autre coopère, sinon perte)

Réponds UNIQUEMENT par C ou D, rien d'autre."""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3}
        }, timeout=30)
        text = response.json()["response"].strip().upper()
        for char in text:
            if char in ["C", "D"]:
                return char
        return "C"
    except Exception as e:
        print(f"Ollama erreur: {e} → défaut C")
        return "C"

def empathique(history):
    return ollama_decision(
        "Tu es empathique, tu préfères coopérer et établir la confiance. "
        "Tu pardonnes facilement les trahisons.",
        history
    )

def calculateur(history):
    return ollama_decision(
        "Tu es calculateur et rationnel. Tu maximises ton score. "
        "Tu trahis si c'est rentable, tu coopères si nécessaire.",
        history
    )

# ── Stratégies disponibles ────────────────────────────────────────────────────

STRATEGIES_CODEES = {
    "always_cooperate": always_cooperate,
    "always_defect":    always_defect,
    "tit_for_tat":      tit_for_tat,
    "grim_trigger":     grim_trigger,
    "random":           random_strategy,
}

# ── Désactivé temporairement pour tester le pipeline ──────────────────────────
STRATEGIES_AI = {}

ALL_STRATEGIES = {**STRATEGIES_CODEES, **STRATEGIES_AI}

# ── Simulation d'un match ─────────────────────────────────────────────────────

def simulate_match(name1, strat1, name2, strat2, nb_tours):
    history1, history2 = [], []
    rows = []

    for tour in range(1, nb_tours + 1):
        if tour % 25 == 0:
            print(f"    tour {tour}/{nb_tours}...")

        choix1 = strat1(history1)
        choix2 = strat2(history2)
        gain1, gain2 = GAINS[(choix1, choix2)]

        score1 = (rows[-1]["score_j1"] + gain1) if rows else gain1
        score2 = (rows[-1]["score_j2"] + gain2) if rows else gain2

        rows.append({
            "run_id":      RUN_ID,
            "timestamp":   TIMESTAMP,
            "match":       f"{name1}_vs_{name2}",
            "strategy_j1": name1,
            "strategy_j2": name2,
            "type_j1":     "ai" if name1 in STRATEGIES_AI else "coded",
            "type_j2":     "ai" if name2 in STRATEGIES_AI else "coded",
            "tour":        tour,
            "choix_j1":    choix1,
            "choix_j2":    choix2,
            "gain_j1":     gain1,
            "gain_j2":     gain2,
            "score_j1":    score1,
            "score_j2":    score2,
        })

        history1.append({"my_choice": choix1, "opponent_choice": choix2})
        history2.append({"my_choice": choix2, "opponent_choice": choix1})

    return rows

# ── Tournoi complet ───────────────────────────────────────────────────────────

def run_tournament():
    all_rows = []
    strategies = list(ALL_STRATEGIES.items())

    for i in range(len(strategies)):
        for j in range(i + 1, len(strategies)):
            name1, strat1 = strategies[i]
            name2, strat2 = strategies[j]

            is_ai_match = (name1 in STRATEGIES_AI or name2 in STRATEGIES_AI)
            nb_tours = NB_TOURS_AI if is_ai_match else NB_TOURS

            print(f"  ⚔️  {name1} vs {name2} ({nb_tours} tours)...")
            rows = simulate_match(name1, strat1, name2, strat2, nb_tours)
            all_rows.extend(rows)

    return all_rows

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🎮 Tournoi démarré — run_id: {RUN_ID}")
    print(f"⏱️  {datetime.now().strftime('%H:%M:%S')}\n")

    try:
        requests.get("http://localhost:11434", timeout=3)
        print("✅ Ollama connecté\n")
    except:
        print("⚠️  Ollama non disponible → agents IA désactivés\n")
        ALL_STRATEGIES = STRATEGIES_CODEES

    rows = run_tournament()

    df = pl.DataFrame(rows)
    output = f"bronze/tournament_{RUN_ID}.parquet"
    df.write_parquet(output, compression="zstd")

    print(f"\n✅ {len(rows)} tours simulés")
    print(f"📦 Bronze → {output}")
    print(f"\n📊 Aperçu :")
    print(df.head(5))
