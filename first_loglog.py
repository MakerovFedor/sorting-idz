import csv
import matplotlib.pyplot as plt
import numpy as np

n_values = []
mean_times = []

with open("results/summary.csv", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["algorithm"] == "Insertion Sort" and row["distribution"] == "random":
            n_values.append(int(row["n"]))
            mean_times.append(float(row["mean_ms"]))

# Для логарифма нужны положительные значения времени.
x = []
y = []

for n, t in zip(n_values, mean_times):
    if n > 0 and t > 0:
        x.append(n)
        y.append(t)

plt.figure(figsize=(9, 5))

plt.plot(x, y, "o-", label="Insertion Sort")

plt.xscale("log")
plt.yscale("log")

plt.title("Insertion Sort: Log-Log")
plt.xlabel("Размер массива N, логарифмическая шкала")
plt.ylabel("Среднее время, мс, логарифмическая шкала")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()

if len(x) >= 2:
    slope = np.polyfit(np.log(x), np.log(y), 1)[0]
    print("Наклон Log-Log:", slope)

plt.savefig("results/my_first_loglog.png", dpi=160)
plt.show()
