"""Первое знакомство с проектом: запусти python first_steps.py в CMD.

Этот файл не использует классы, графики и сложные библиотеки.
"""

from sorts import stupid_sort, insertion_sort, quick_sort_hoare

numbers = [4, 24, 3, 1, 2]
print("Исходный массив:", numbers)
print()

result, comparisons, swaps = stupid_sort(numbers.copy())
print("Stupid Sort:", result)
print("Сравнения:", comparisons, "Обмены:", swaps)
print()

result, comparisons, writes = insertion_sort(numbers.copy())
print("Insertion Sort:", result)
print("Сравнения:", comparisons, "Записи:", writes)
print()

result, comparisons, swaps = quick_sort_hoare(numbers.copy())
print("Quick Sort (Hoare):", result)
print("Сравнения:", comparisons, "Обмены:", swaps)
print()
print("Исходный массив не изменился:", numbers)
