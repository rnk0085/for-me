import random

def random_true_with_probability(probability: float) -> bool:
    """引数の確率でTrueを返す"""
    return random.random() <= probability