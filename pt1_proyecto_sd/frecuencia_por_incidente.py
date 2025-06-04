import pandas as pd
import matplotlib.pyplot as plt

# Leer archivo procesado
FILE_PATH = "pig/data/results/por_comuna_tipo/part-r-00000"
df = pd.read_csv(FILE_PATH, names=["comuna", "tipo_incidente", "cantidad"])

# Eliminar encabezado repetido si existe
df = df[df["comuna"] != "comuna"]

# Asegurar tipo numérico para cantidad
df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

# Agrupar por tipo de incidente y sumar ocurrencias
frecuencia_tipos = df.groupby("tipo_incidente")["cantidad"].sum().sort_values(ascending=False)


plt.figure(figsize=(8, 5))
frecuencia_tipos.plot(kind="bar", color="cornflowerblue", edgecolor="black")

plt.title("Frecuencia total por tipo de incidente", fontsize=14)
plt.xlabel("Tipo de incidente", fontsize=12)
plt.ylabel("Cantidad total", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.savefig("frecuencia_por_tipo_incidente.png", dpi=300)
plt.show()
