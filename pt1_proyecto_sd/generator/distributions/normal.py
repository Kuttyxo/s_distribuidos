import numpy as np

def generate_normal(mean=2.0, std_dev=0.5):
    """Genera intervalos con distribución normal"""
    while True:
        val = np.random.normal(mean, std_dev)
        if val > 0:  # Asegurar valores positivos
            return float(val)