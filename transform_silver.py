import polars as pl
import glob
import os

# Lire tous les fichiers Bronze
files = glob.glob("bronze/*.parquet")
print(f"📂 {len(files)} fichiers Bronze trouvés")

df = pl.concat([pl.read_parquet(f) for f in files])

# Nettoyage Silver
df_silver = df.with_columns([
    # Booléen coopération
    (pl.col("choix_j1") == "C").alias("coopere_j1"),
    (pl.col("choix_j2") == "C").alias("coopere_j2"),

    # Les deux coopèrent
    ((pl.col("choix_j1") == "C") & (pl.col("choix_j2") == "C")).alias("cooperation_mutuelle"),

    # Trahison unilatérale
    ((pl.col("choix_j1") == "D") & (pl.col("choix_j2") == "C")).alias("trahison_j1"),
    ((pl.col("choix_j1") == "C") & (pl.col("choix_j2") == "D")).alias("trahison_j2"),
])

# Sauvegarde Silver
os.makedirs("silver", exist_ok=True)
output = "silver/tournament_clean.parquet"
df_silver.write_parquet(output, compression="zstd")

print(f"✅ {len(df_silver)} lignes nettoyées")
print(f"📦 Silver → {output}")
print(df_silver.head(5))
