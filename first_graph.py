
import csv
import matplotlib.pyplot as plt

n_values = []
mean_times = []
deviations = []

with open("results/summary.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["algorithm"] == "Insertion Sort" and row["distribution"] == "random":
            n_values.append(int(row["n"]))
            mean_times.append(float(row["mean_ms"]))
            deviations.append(float(row["std_ms"]))

plt.figure(figsize=(9, 5))

plt.errorbar(
    n_values,
    mean_times,
    yerr=deviations,
    fmt="-o",
    capsize=3,
    label="Insertion Sort"
)

plt.title("Insertion Sort: случайный массив")
plt.xlabel("Размер массива N (элементов)")
plt.ylabel("Среднее время выполнения (мс)")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()
