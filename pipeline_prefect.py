from prefect import flow, task
import subprocess
import os

PROJECT = "/home/nadege/Downloads/prisoner-dilemma"

@task(name="Bronze — Simulation tournoi")
def bronze():
    print("🎮 Simulation en cours...")
    result = subprocess.run(
        ["python3", f"{PROJECT}/simulate.py"],
        cwd=PROJECT
    )
    if result.returncode == 0:
        print("✅ Bronze terminé")
    else:
        raise Exception("❌ Erreur Bronze")

@task(name="Silver — Nettoyage données")
def silver():
    print("🥈 Nettoyage Silver...")
    result = subprocess.run(
        ["python3", f"{PROJECT}/transform_silver.py"],
        cwd=PROJECT
    )
    if result.returncode == 0:
        print("✅ Silver terminé")
    else:
        raise Exception("❌ Erreur Silver")

@task(name="Gold — dbt run")
def gold():
    print("🥇 Transformation Gold...")
    result = subprocess.run(
        ["dbt", "run"],
        cwd=f"{PROJECT}/prisoner_dilemma"
    )
    if result.returncode == 0:
        print("✅ Gold terminé")
    else:
        raise Exception("❌ Erreur Gold")

@flow(name="Pipeline Prisoner Dilemma")
def prisoner_pipeline():
    bronze()
    silver()
    gold()

if __name__ == "__main__":
    prisoner_pipeline()
