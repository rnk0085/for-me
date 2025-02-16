import pytest
from src.utils.random_utils import random_true_with_probability

def test_random_true_with_probability():
    """確率に基づくランダム判定のテスト"""
    ### Given
    test_cases = [
        (0.0, False),  # 0%の確率
        (1.0, True),   # 100%の確率
    ]

    ### When/Then
    for probability, expected in test_cases:
        result = random_true_with_probability(probability)
        assert result == expected

    # 中間の確率のテスト
    results = [random_true_with_probability(0.5) for _ in range(1000)]
    true_ratio = sum(results) / len(results)
    assert 0.4 <= true_ratio <= 0.6  # 50%±10%の範囲内であることを確認 