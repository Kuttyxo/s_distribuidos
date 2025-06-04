import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Ruta al archivo generado por Pig
FILE_PATH = Path("pig/data/results/por_dia/part-r-00000")

# Cargar datos
df = pd.read_csv(FILE_PATH, names=["fecha", "total_incidentes"], skiprows=1)


# Asegurarse de que fecha es tipo datetime
df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d")

# Ordenar por fecha
df.sort_values("fecha", inplace=True)

# Calcular estadísticas
promedio = df["total_incidentes"].mean()
desviacion = df["total_incidentes"].std()
umbral_pico = promedio + 1.5 * desviacion

# Detectar días pico
df["pico"] = df["total_incidentes"] > umbral_pico

# Mostrar resultados
print("\n📊 Resumen de evolución diaria:")
print(df)

print(f"\n📈 Promedio de incidentes por día: {promedio:.2f}")
print(f"📉 Desviación estándar: {desviacion:.2f}")
print(f"🔺 Umbral de pico: {umbral_pico:.2f}")
print(f"\n🚨 Días con picos de incidentes:\n{df[df['pico']]}")

plt.figure(figsize=(10, 6))
plt.plot(df["fecha"], df["total_incidentes"], label="Incidentes por día", marker="o")
plt.axhline(umbral_pico, color="red", linestyle="--", label="Umbral de pico")
plt.scatter(df[df["pico"]]["fecha"], df[df["pico"]]["total_incidentes"], color="red", label="Picos detectados")
plt.title("Evolución de incidentes diarios")
plt.xlabel("Fecha")
plt.ylabel("Número de incidentes")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("evolucion_incidentes.png", dpi=300)
plt.show()
