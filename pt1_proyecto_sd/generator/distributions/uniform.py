import numpy as np

def generate_uniform(low=1.0, high=3.0):
    """Genera intervalos con distribución uniforme"""
    return float(np.random.uniform(low, high))