import pandas as pd
import matplotlib.pyplot as plt

# Ruta del archivo CSV ya procesado
FILE_PATH = "pig/data/results/por_comuna_tipo/part-r-00000"

# Leer datos (sin encabezado)
df = pd.read_csv(FILE_PATH, names=["comuna", "tipo_incidente", "cantidad"])


df = df[df["comuna"] != "comuna"]

# Convertir columna cantidad a entero
df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)

# Pivot para crear la tabla comuna vs tipo_incidente
conteo_comuna_tipo = df.pivot_table(index="comuna", columns="tipo_incidente", values="cantidad", aggfunc="sum", fill_value=0)

# Ordenar por total de incidentes (suma por fila)
conteo_comuna_tipo["total"] = conteo_comuna_tipo.sum(axis=1)
conteo_comuna_tipo = conteo_comuna_tipo.sort_values(by="total", ascending=False).drop(columns="total")

# Crear gráfico apilado
plt.figure(figsize=(14, 7))
conteo_comuna_tipo.plot(
    kind="bar",
    stacked=True,
    colormap="tab20",
    figsize=(14, 7),
    width=0.8,
    edgecolor="black"
)

plt.title("Distribución de incidentes por comuna y tipo", fontsize=16)
plt.xlabel("Comuna", fontsize=12)
plt.ylabel("Cantidad de incidentes", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.legend(title="Tipo de incidente", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
plt.savefig("incidentes_comuna_tipo.png", dpi=300)
plt.show()
