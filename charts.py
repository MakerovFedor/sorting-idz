"""Научные графики: линейный, log-log, аппроксимация, память, операции."""


import matplotlib.pyplot as plt
import numpy as np

from experiments import DISTRIBUTIONS


def subset(summary: list[dict], distribution: str, name: str) -> list[dict]:
    return sorted((r for r in summary
                   if r["distribution"] == distribution and r["algorithm"] == name),
                  key=lambda r: r["n"])


def plot_time(summary: list[dict], distribution: str = "random"):
    """График 1: X=N, Y=среднее время в мс; погрешность +/-1 std."""
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for name in dict.fromkeys(r["algorithm"] for r in summary):
        rows = subset(summary, distribution, name)
        if rows:
            x = [r["n"] for r in rows]
            y = [r["mean_ms"] for r in rows]
            e = [r["std_ms"] for r in rows]
            ax.errorbar(x, y, yerr=e, capsize=2, marker="o", label=name)
    ax.set(title=f"Время сортировки — {DISTRIBUTIONS[distribution]}",
           xlabel="Размер массива N (элементов)", ylabel="Время T(N) (мс)")
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    return fig


def slope_loglog(rows: list[dict]) -> float | None:
    """Оценка наклона прямой: log(T) = k log(N) + b."""
    pairs = [(r["n"], r["mean_ms"]) for r in rows if r["mean_ms"] > 0]
    if len(pairs) < 2:
        return None
    x = np.log([p[0] for p in pairs])
    y = np.log([p[1] for p in pairs])
    return float(np.polyfit(x, y, deg=1)[0])


def plot_loglog(summary: list[dict], distribution: str = "random"):
    """График 2: логарифмические шкалы по обеим осям."""
    fig, ax = plt.subplots(figsize=(10, 5.4))
    slopes = {}
    for name in dict.fromkeys(r["algorithm"] for r in summary):
        rows = subset(summary, distribution, name)
        if rows:
            slope = slope_loglog(rows)
            slopes[name] = slope
            label = f"{name}, наклон k={slope:.2f}" if slope is not None else name
            ax.errorbar([r["n"] for r in rows], [r["mean_ms"] for r in rows],
                        yerr=[r["std_ms"] for r in rows], capsize=2,
                        marker="o", label=label)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set(title=f"Log-Log — {DISTRIBUTIONS[distribution]}",
           xlabel="Размер массива N (элементов), log",
           ylabel="Время T(N) (мс), log")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    return fig, slopes


def theory_model(name: str, distribution: str) -> tuple[str, callable]:
    """Подбираем обоснованную модель для выбранного набора данных."""
    if name == "Stupid Sort":
        if distribution == "sorted":
            return "c · N", lambda n: n
        return "c · N³", lambda n: n ** 3
    if name == "Insertion Sort":
        if distribution == "sorted":
            return "c · N", lambda n: n
        return "c · N²", lambda n: n ** 2
    return "c · N·log₂(N)", lambda n: n * np.log2(n)


def fit_coefficient(n: np.ndarray, times: np.ndarray, model) -> float:
    """МНК для y = c f(n), при свободном только параметре c."""
    values = np.asarray(model(n), dtype=float)
    return float(np.dot(values, times) / np.dot(values, values))


def plot_fitting(summary: list[dict], distribution: str = "random"):
    """График 3: эмпирические точки и теоретические кривые, c находится по МНК."""
    names = list(dict.fromkeys(r["algorithm"] for r in summary))
    fig, axes = plt.subplots(len(names), 1, figsize=(9, 4.1 * len(names)), squeeze=False)
    coefficients = {}
    for axis, name in zip(axes.flat, names):
        rows = subset(summary, distribution, name)
        if not rows:
            continue
        n = np.array([r["n"] for r in rows], dtype=float)
        times = np.array([r["mean_ms"] for r in rows], dtype=float)
        model_name, model = theory_model(name, distribution)
        c = fit_coefficient(n, times, model)
        coefficients[name] = (model_name, c)
        dense_n = np.linspace(float(min(n)), float(max(n)), 250)
        axis.errorbar(n, times, yerr=[r["std_ms"] for r in rows],
                      fmt="o", capsize=2, label="Замеры (±1 σ)")
        axis.plot(dense_n, c * model(dense_n),
                  label=f"Теория: {model_name}, c={c:.3g}")
        axis.set(title=name, xlabel="Размер массива N (элементов)",
                 ylabel="Время T(N) (мс)")
        axis.grid(True, alpha=0.35)
        axis.legend()
    fig.suptitle(f"Теоретическая аппроксимация — {DISTRIBUTIONS[distribution]}", y=1.00)
    fig.tight_layout()
    return fig, coefficients


def plot_memory(records: list[dict]):
    """График 4: пик выделений, отслеживаемых tracemalloc, в КиБ."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for name in dict.fromkeys(r["algorithm"] for r in records):
        rows = sorted((r for r in records if r["algorithm"] == name),
                      key=lambda r: r["n"])
        ax.plot([r["n"] for r in rows], [r["peak_kib"] for r in rows],
                marker="o", label=name)
    ax.set(title="Пиковые дополнительные выделения Python (tracemalloc)",
           xlabel="Размер массива N (элементов)",
           ylabel="Пик дополнительной памяти (КиБ)")
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    return fig
