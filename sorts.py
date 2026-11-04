"""Три сортировки из индивидуального варианта. Без встроенной сортировки."""

from collections.abc import Callable

Number = int | float
SortResult = tuple[list[Number], int, int]
SortFunction = Callable[[list[Number]], SortResult]


def stupid_sort(arr: list[Number]) -> SortResult:
    """Stupid Sort (возврат к началу): время O(n^3) в худшем случае, память O(1).

    Счётчики: сравнения соседей и обменов соседних элементов.
    Сортирует переданный список на месте и возвращает (список, comparisons, swaps).
    """
    comparisons = 0
    swaps = 0
    i = 0

    while i < len(arr) - 1:
        comparisons += 1
        if arr[i] > arr[i + 1]:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
            swaps += 1
            i = 0  # После обмена просматриваем массив с начала.
        else:
            i += 1

    return arr, comparisons, swaps


def insertion_sort(arr: list[Number]) -> SortResult:
    """Insertion Sort: O(n^2) в худшем, O(n) в лучшем; память O(1).

    Счётчики: сравнения элементов и записей в ячейки списка.
    Сортирует переданный список на месте и возвращает (список, comparisons, writes).
    """
    comparisons = 0
    writes = 0

    for i in range(1, len(arr)): #Считаем первый элемент отсортированным, расставляем второй относительно него
        key = arr[i] #Элемент, который мы ставим в нужную позицию относ уже отсортированных
        j = i - 1
        while j >= 0:
            comparisons += 1
            if arr[j] <= key:
                break
            arr[j + 1] = arr[j]  # Сдвигаем слишком большой элемент вправо.
            writes += 1
            j -= 1
        if j + 1 != i:
            arr[j + 1] = key
            writes += 1

    return arr, comparisons, writes


def quick_sort_hoare(arr: list[Number]) -> SortResult:
    """QuickSort с разбиением Хоара: среднее O(n log n), худшее O(n^2).

    Дополнительная память O(log n) в типичном случае (стек рекурсии).
    Счётчики: сравнения с опорным элементом и обмены элементов списка.
    Сортирует переданный список на месте и возвращает (список, comparisons, swaps).
    """
    comparisons = 0
    swaps = 0

    def partition(left: int, right: int) -> int:
        nonlocal comparisons, swaps
        pivot = arr[(left + right) // 2]
        i = left - 1
        j = right + 1

        while True:
            while True:
                i += 1
                comparisons += 1
                if not arr[i] < pivot:
                    break
            while True:
                j -= 1
                comparisons += 1
                if not arr[j] > pivot:
                    break
            if i >= j:
                return j #j=border
            arr[i], arr[j] = arr[j], arr[i]
            swaps += 1

    def quicksort(left: int, right: int) -> None:
        if left >= right:
            return
        border = partition(left, right)
        quicksort(left, border)
        quicksort(border + 1, right)

    quicksort(0, len(arr) - 1)
    return arr, comparisons, swaps


SORTS: dict[str, SortFunction] = {
    "Stupid Sort": stupid_sort,
    "Insertion Sort": insertion_sort,
    "Quick Sort (Hoare)": quick_sort_hoare,
}

# У разных сортировок третий счётчик разный.
OPERATION_LABELS: dict[str, str] = {
    "Stupid Sort": "обмены",
    "Insertion Sort": "записи",
    "Quick Sort (Hoare)": "обмены",
}

