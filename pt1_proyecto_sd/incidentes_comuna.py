import pandas as pd
import matplotlib.pyplot as plt

# Leer datos procesados
FILE_PATH = "pig/data/results/por_comuna_tipo/part-r-00000"
df = pd.read_csv(FILE_PATH, names=["comuna", "tipo_incidente", "cantidad"])

# Eliminar encabezado repetido si existe
df = df[df["comuna"] != "comuna"]

# Asegurar tipo numérico en cantidad
df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

# Agrupar por comuna sumando todos los incidentes
total_por_comuna = df.groupby("comuna")["cantidad"].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
total_por_comuna.plot(kind="bar", color="cornflowerblue", edgecolor="black")

plt.title("Total de incidentes por comuna", fontsize=14)
plt.xlabel("Comuna", fontsize=12)
plt.ylabel("Cantidad total", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.tight_layout()
plt.savefig("total_incidentes_por_comuna.png", dpi=300)
plt.show()
