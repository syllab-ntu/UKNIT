# seed_config.py
import random
import numpy as np  # remove if not using numpy

SEED = np.random.randint(0, 2**32 - 1)

def set_global_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    return seed