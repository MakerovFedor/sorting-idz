"""Запуск всех серий: python run_experiments.py --full."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from charts import plot_fitting, plot_loglog, plot_memory, plot_time
from experiments import (DEMO_SIZES, FULL_SIZES, benchmark, memory_profile,
                         save_csv)


def main():
    parser = argparse.ArgumentParser(description="Замер сортировок по ТЗ")
    parser.add_argument("--full", action="store_true", help="Полные сетки N из ТЗ")
    parser.add_argument("--repeats", type=int, default=5,
                        help="5–10 повторений для финального исследования")
    args = parser.parse_args()
    Path("results").mkdir(exist_ok=True)
    sizes = FULL_SIZES if args.full else DEMO_SIZES
    raw, summary = benchmark(sizes=sizes, repeats=args.repeats, progress=print)
    save_csv(raw, "results/raw.csv")
    save_csv(summary, "results/summary.csv")
    for kind in ("random", "sorted", "reversed", "nearly_sorted", "duplicates"):
        fig = plot_time(summary, kind)
        fig.savefig(f"results/linear_{kind}.png", dpi=160)
        plt.close(fig)
        fig, slopes = plot_loglog(summary, kind)
        fig.savefig(f"results/loglog_{kind}.png", dpi=160)
        plt.close(fig)
        print("Наклоны Log-Log:", kind, slopes)
        fig, _ = plot_fitting(summary, kind)
        fig.savefig(f"results/fitting_{kind}.png", dpi=160)
        plt.close(fig)
    memory = memory_profile()
    save_csv(memory, "results/memory.csv")
    fig = plot_memory(memory)
    fig.savefig("results/memory.png", dpi=160)
    plt.close(fig)
    print("Готово: файлы записаны в папку results/")


if __name__ == "__main__":
    main()
