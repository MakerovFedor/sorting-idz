import random

import pytest

from experiments import DISTRIBUTIONS, generate_data, is_nondecreasing
from sorts import SORTS


@pytest.mark.parametrize("name", list(SORTS))
@pytest.mark.parametrize("source", [[], [7], [1, 1, 1, 1], [2, 1],
                                    [0, -4, 5, 3, -4, 1], [2.5, -1.0, 2.5]])
def test_edge_cases(name, source):
    original = source.copy()
    result, comparisons, operations = SORTS[name](source.copy())
    assert result == sorted(original)  # sorted здесь только эталон в тесте, НЕ в алгоритме.
    assert comparisons >= 0 and operations >= 0


@pytest.mark.parametrize("name", list(SORTS))
@pytest.mark.parametrize("distribution", list(DISTRIBUTIONS))
def test_distributions(name, distribution):
    source = generate_data(35, distribution, 143)
    original = source.copy()
    result, _, _ = SORTS[name](source.copy())
    assert result == sorted(original)
    assert source == original  # Копирование защищает экспериментальные данные.


def test_stupid_restarts_and_sorted_is_linear():
    _, comparisons, swaps = SORTS["Stupid Sort"]([3, 2, 1])
    assert comparisons > 2
    assert swaps == 3
    assert SORTS["Stupid Sort"]([1, 2, 3])[1:] == (2, 0)


def test_insertion_sorted_no_writes():
    _, comparisons, writes = SORTS["Insertion Sort"]([1, 2, 3, 4])
    assert comparisons == 3
    assert writes == 0


def test_random_medium():
    rng = random.Random(88)
    for name in SORTS:
        n = 70 if name == "Stupid Sort" else 1500
        arr = [rng.randint(-10, 10) for _ in range(n)]
        result, _, _ = SORTS[name](arr.copy())
        assert is_nondecreasing(result)
        assert result == sorted(arr)
