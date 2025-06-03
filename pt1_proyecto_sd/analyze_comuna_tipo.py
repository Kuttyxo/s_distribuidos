import pandas as pd
import matplotlib.pyplot as plt

FILE_PATH = "pig/data/results/por_comuna_tipo/part-r-00000"

# Cargar datos
df = pd.read_csv(FILE_PATH, names=["comuna", "type", "cantidad"])

# Filtrar cabecera y entradas inválidas
df = df[(df["comuna"] != "comuna") & (df["type"] != "event_type")]
df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
df.dropna(inplace=True)

# Verifica que se cargaron datos
if df.empty:
    print("❌ No se cargaron datos válidos.")
    exit()

# --- Agrupar por comuna ---
comuna_totals = df.groupby("comuna")["cantidad"].sum().sort_values(ascending=False)

plt.figure(figsize=(12, 6))
comuna_totals.plot(kind="bar", color="skyblue")
plt.title("Total de incidentes por comuna")
plt.xlabel("Comuna")
plt.ylabel("Cantidad de incidentes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("por_comuna.png", dpi=300)
plt.show()

# --- Agrupar por tipo ---
tipo_totals = df.groupby("type")["cantidad"].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
tipo_totals.plot(kind="bar", color="salmon")
plt.title("Total de incidentes por tipo")
plt.xlabel("Tipo de incidente")
plt.ylabel("Cantidad de incidentes")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("por_tipo.png", dpi=300)
plt.show()
