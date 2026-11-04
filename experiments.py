"""Генерация пяти типов данных, воспроизводимые замеры и профилирование памяти."""

from __future__ import annotations

import csv
import random
import statistics
import time
import tracemalloc
from collections.abc import Callable, Iterable
from pathlib import Path

from sorts import OPERATION_LABELS, SORTS

DISTRIBUTIONS = {
    "random": "Случайный",
    "sorted": "Отсортированный",
    "reversed": "Обратно отсортированный",
    "nearly_sorted": "Почти отсортированный",
    "duplicates": "Много повторений",
}

# Сетки из ТЗ; отдельная сетка для Stupid из-за ограничения N <= 500.
FULL_SIZES = {
    "Stupid Sort": [100, 150, 200, 250, 300, 400, 500],
    "Insertion Sort": [100, 300, 600, 1000, 2000, 4000, 8000, 10000],
    "Quick Sort (Hoare)": [1000, 5000, 10000, 50000, 100000, 300000, 500000, 1000000],
}
# Небольшой режим для первого запуска и освоения ноутбука, не финальная сдача.
DEMO_SIZES = {
    "Stupid Sort": [20, 40, 60, 80, 100],
    "Insertion Sort": [100, 200, 400, 800, 1200],
    "Quick Sort (Hoare)": [100, 500, 1000, 3000, 6000],
}
# Дополнительная единая сетка для прямого сравнения на одном графике.
COMMON_SIZES = [50, 100, 150, 200, 300, 400, 500]


def generate_data(n: int, distribution: str, seed: int) -> list[int]:
    """Создаёт массив длины n; seed позволяет повторить случайные данные."""
    if n < 0:
        raise ValueError("Размер массива не может быть отрицательным")
    if distribution not in DISTRIBUTIONS:
        raise ValueError(f"Неизвестный тип данных: {distribution}")
    rng = random.Random(seed)
    if distribution == "random":
        return [rng.randint(-n, n) for _ in range(n)]
    if distribution == "sorted":
        return list(range(n))
    if distribution == "reversed":
        return list(range(n, 0, -1))
    if distribution == "duplicates":
        return [rng.randint(1, 5) for _ in range(n)]

    arr = list(range(n))
    # Перемешиваем значения только на случайно выбранных ~5% позиций.
    count = min(n, max(2, round(0.05 * n)))
    if count > 1:
        positions = rng.sample(range(n), count)
        selected = [arr[pos] for pos in positions]
        rng.shuffle(selected)
        for pos, value in zip(positions, selected):
            arr[pos] = value
    return arr


def is_nondecreasing(arr: list[int | float]) -> bool:
    """Проверка порядка без применения встроенной сортировки."""
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))


def benchmark(
    names: Iterable[str] | None = None,
    distributions: Iterable[str] | None = None,
    sizes: dict[str, list[int]] | None = None,
    repeats: int = 5,
    progress: Callable[[str], None] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Для каждой точки делает repeats независимых повторов.

    Генерация массива и его копирование происходят ВНЕ измеряемого времени.
    Возвращает (сырые замеры, статистика по группам).
    """
    if repeats < 2:
        raise ValueError("Для оценки разброса нужно как минимум 2 повтора")
    chosen = list(names) if names is not None else list(SORTS)
    kinds = list(distributions) if distributions is not None else list(DISTRIBUTIONS)
    grid = sizes if sizes is not None else FULL_SIZES
    raw: list[dict] = []
    summary: list[dict] = []

    for name in chosen:
        if name not in SORTS:
            raise ValueError(f"Неизвестная сортировка: {name}")
        for n in grid[name]:
            if name == "Stupid Sort" and n > 500:
                raise ValueError("Для Stupid Sort в ТЗ задано N <= 500")
            for kind in kinds:
                if kind not in DISTRIBUTIONS:
                    raise ValueError(f"Неизвестный тип данных: {kind}")
                point: list[dict] = []
                for repetition in range(repeats):
                    seed = 2026 + repetition * 1009 + n * 17
                    data = generate_data(n, kind, seed)
                    data_copy = data.copy()  # Копируем ДО включения таймера.
                    started = time.perf_counter()
                    result, comparisons, operations = SORTS[name](data_copy)
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    if not is_nondecreasing(result):
                        raise AssertionError(f"{name}: массив не отсортирован")
                    record = {
                        "algorithm": name, "distribution": kind, "n": n,
                        "repeat": repetition + 1, "seed": seed,
                        "time_ms": elapsed_ms, "comparisons": comparisons,
                        "operations": operations,
                        "operation_type": OPERATION_LABELS[name],
                    }
                    raw.append(record)
                    point.append(record)
                times = [r["time_ms"] for r in point]
                summary.append({
                    "algorithm": name, "distribution": kind, "n": n,
                    "mean_ms": statistics.mean(times),
                    "std_ms": statistics.stdev(times),
                    "mean_comparisons": statistics.mean(r["comparisons"] for r in point),
                    "mean_operations": statistics.mean(r["operations"] for r in point),
                    "operation_type": OPERATION_LABELS[name],
                    "repeats": repeats,
                })
                if progress is not None:
                    progress(f"{name}, {DISTRIBUTIONS[kind]}, N={n}: готово")
    return raw, summary


def memory_profile(
    names: Iterable[str] | None = None,
    distributions: Iterable[str] = ("random",),
    sizes: dict[str, list[int]] | None = None,
) -> list[dict]:
    """Пиковые Python-выделения ПОСЛЕ подготовки массива (не полная память процесса)."""
    chosen = list(names) if names is not None else list(SORTS)
    grid = sizes or {
        "Stupid Sort": [20, 50, 100, 200],
        "Insertion Sort": [100, 1000, 3000, 5000],
        "Quick Sort (Hoare)": [1000, 3000, 10000, 30000],
    }
    result = []
    for name in chosen:
        for kind in distributions:
            for n in grid[name]:
                if name == "Stupid Sort" and n > 500:
                    raise ValueError("Для Stupid Sort N <= 500")
                arr = generate_data(n, kind, seed=42)
                tracemalloc.start()  # Не учитывает уже созданный входной список.
                try:
                    SORTS[name](arr)
                    _, peak_bytes = tracemalloc.get_traced_memory()
                finally:
                    tracemalloc.stop()
                result.append({"algorithm": name, "distribution": kind,
                               "n": n, "peak_kib": peak_bytes / 1024})
    return result


def save_csv(rows: list[dict], target: str | Path) -> None:
    """Сохраняет таблицу эксперимента для воспроизводимости."""
    if not rows:
        raise ValueError("Нет строк для сохранения")
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
