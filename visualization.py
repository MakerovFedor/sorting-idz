"""Пошаговые учебные трассировки для массива из 20–30 элементов.

Это отдельное наглядное представление тех же алгоритмов; замеры выполняются
только в sorts.py, где нет накладных расходов на сохранение кадров.
"""

def trace_sort(name: str, source: list[int], limit: int = 30000) -> list[dict]:
    """Сохраняет кадры анимации как обычные словари, без классов.

    В каждом кадре три поля:
    - "values": копия текущего массива,
    - "active": индексы подсвеченных элементов,
    - "description": пояснение происходящего.
    """
    arr = source.copy()
    steps = [{"values": arr.copy(), "active": [], "description": "Исходный массив"}]

    def push(active: tuple[int, ...], description: str) -> None:
        if len(steps) < limit:
            steps.append({
                "values": arr.copy(),
                "active": list(active),
                "description": description,
            })

    if name == "Stupid Sort":
        i = 0
        while i < len(arr) - 1:
            push((i, i + 1), f"Сравниваем соседей {arr[i]} и {arr[i + 1]}")
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                push((i, i + 1), "Обмен! Возвращаемся в начало")
                i = 0
            else:
                i += 1

    elif name == "Insertion Sort":
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            push((i,), f"Ключ = {key}: ищем место для вставки")
            while j >= 0:
                push((j, j + 1), f"Сравниваем {arr[j]} с ключом {key}")
                if arr[j] <= key:
                    break
                arr[j + 1] = arr[j]
                push((j, j + 1), f"Сдвиг {arr[j]} вправо; ключ {key} хранится отдельно")
                j -= 1
            if j + 1 != i:
                arr[j + 1] = key
                push((j + 1,), f"Вставили ключ {key}")

    elif name == "Quick Sort (Hoare)":
        def partition(left: int, right: int) -> int:
            pivot_idx = (left + right) // 2
            pivot = arr[pivot_idx]
            i, j = left - 1, right + 1
            push((pivot_idx,), f"Опорное значение pivot = {pivot}, отрезок [{left}, {right}]")
            while True:
                while True:
                    i += 1
                    push((i, pivot_idx), f"Сравнение слева: {arr[i]} < pivot ({pivot})?")
                    if not arr[i] < pivot:
                        break
                while True:
                    j -= 1
                    push((j, pivot_idx), f"Сравнение справа: {arr[j]} > pivot ({pivot})?")
                    if not arr[j] > pivot:
                        break
                if i >= j:
                    push((i, j), f"Разделение закончено, граница = {j}")
                    return j
                arr[i], arr[j] = arr[j], arr[i]
                if pivot_idx == i:
                    pivot_idx = j
                elif pivot_idx == j:
                    pivot_idx = i
                push((i, j), "Обмен элементов по разные стороны от pivot")

        def quicksort(left: int, right: int) -> None:
            if left < right:
                border = partition(left, right)
                quicksort(left, border)
                quicksort(border + 1, right)

        quicksort(0, len(arr) - 1)
    else:
        raise ValueError(f"Неизвестная сортировка: {name}")

    if len(steps) < limit:
        push((), "Готово. Массив отсортирован")
    return steps
