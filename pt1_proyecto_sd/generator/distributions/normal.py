import numpy as np
import random

def generate_normal():
    # Media más alta → menos requests → menos repeticiones
    return float(np.random.normal(2.5, 0.6))