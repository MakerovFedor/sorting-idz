"""Streamlit-дашборд для ИДЗ. Запуск: python -m streamlit run app.py"""


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from experiments import (COMMON_SIZES, DISTRIBUTIONS, benchmark, generate_data,
                         memory_profile)
from sorts import OPERATION_LABELS, SORTS
from visualization import trace_sort

st.set_page_config(page_title="ИДЗ: анализ сортировок", page_icon="📊", layout="wide")
st.title("Эмпирический и теоретический анализ сортировок")
st.caption("Stupid Sort · Insertion Sort · QuickSort (разбиение Хоара)")

st.sidebar.header("Настройки эксперимента")
selected = st.sidebar.multiselect("Алгоритмы", list(SORTS), default=list(SORTS))
kind = st.sidebar.selectbox("Тип входного массива", list(DISTRIBUTIONS),
                            format_func=lambda value: DISTRIBUTIONS[value])
max_n = 500 if "Stupid Sort" in selected else (10000 if "Insertion Sort" in selected else 100000)
n = st.sidebar.slider("Размер массива N", min_value=20, max_value=max_n,
                      value=min(200, max_n), step=10)
repeats = st.sidebar.slider("Повторения (отдельные сиды)", 5, 10, 5)

st.info("Генерация массива, копирование и проверка результата не входят во время сортировки. "
        "Для Stupid Sort действует ограничение N ≤ 500.")


@st.cache_data(show_spinner=False)
def measured(names: tuple[str, ...], distribution: str, sizes: tuple[int, ...], reps: int):
    grid = {name: list(sizes) for name in names}
    return benchmark(names=names, distributions=[distribution], sizes=grid, repeats=reps)


if st.sidebar.button("Измерить время для выбранного N", type="primary"):
    st.session_state.show_single = True

if st.session_state.get("show_single", False):
    if not selected:
        st.warning("Выбери хотя бы один алгоритм")
    else:
        with st.spinner("Выполняются независимые замеры..."):
            raw, stats = measured(tuple(selected), kind, (n,), repeats)
        st.subheader("Результат измерений")
        st.dataframe(pd.DataFrame(stats)[["algorithm", "n", "mean_ms", "std_ms",
                                          "mean_comparisons", "mean_operations",
                                          "operation_type"]], use_container_width=True)
        fig = go.Figure()
        for row in stats:
            fig.add_bar(name=row["algorithm"], x=[row["algorithm"]], y=[row["mean_ms"]],
                        error_y={"type": "data", "array": [row["std_ms"]]})
        fig.update_layout(title="Среднее время ± 1 стандартное отклонение",
                          yaxis_title="Время T(N), мс", xaxis_title="Алгоритм",
                          template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Третий счётчик: у Insertion Sort — записи, у остальных — обмены; "
                   "сравнивать их значения напрямую некорректно.")
        st.subheader("Сырые замеры")
        st.dataframe(pd.DataFrame(raw), use_container_width=True)
        st.download_button("Скачать сырые данные (CSV)",
                           pd.DataFrame(raw).to_csv(index=False).encode("utf-8-sig"),
                           file_name="measurements.csv", mime="text/csv")

st.divider()
st.subheader("Графики зависимости времени от размера N")
st.write("Для этого блока используется одна общая сетка N, чтобы алгоритмы можно было "
         "сравнивать на одинаковых входных размерах. Максимум N = 500 из-за Stupid Sort.")

if st.button("Построить линейный, Log-Log и теоретический графики"):
    st.session_state.show_curves = True

if st.session_state.get("show_curves", False):
    if not selected:
        st.warning("Нужно выбрать алгоритм")
    else:
        with st.spinner("Строятся графики..."):
            _, series = measured(tuple(selected), kind, tuple(COMMON_SIZES), repeats)
        df = pd.DataFrame(series)
        fig = px.line(df, x="n", y="mean_ms", color="algorithm", markers=True,
                      error_y="std_ms", template="plotly_white",
                      labels={"n": "Размер массива N (элементов)",
                              "mean_ms": "Время T(N) (мс)", "algorithm": "Алгоритм"},
                      title="1. Линейная шкала")
        st.plotly_chart(fig, use_container_width=True)
        fig_log = px.line(df, x="n", y="mean_ms", color="algorithm", markers=True,
                          error_y="std_ms", log_x=True, log_y=True,
                          template="plotly_white",
                          labels={"n": "Размер N (элементов), log",
                                  "mean_ms": "Время T(N) (мс), log", "algorithm": "Алгоритм"},
                          title="2. Log-Log")
        st.plotly_chart(fig_log, use_container_width=True)
        fit_fig = go.Figure()
        from charts import fit_coefficient, theory_model
        import numpy as np
        for name in selected:
            group = df[df["algorithm"] == name].sort_values("n")
            xs = group["n"].to_numpy(dtype=float)
            ys = group["mean_ms"].to_numpy(dtype=float)
            model_name, model = theory_model(name, kind)
            c = fit_coefficient(xs, ys, model)
            fit_fig.add_scatter(x=xs, y=ys, mode="markers", name=f"{name}: измерения")
            grid = np.linspace(min(xs), max(xs), 100)
            fit_fig.add_scatter(x=grid, y=c * model(grid), mode="lines",
                                name=f"{name}: {model_name}")
        fit_fig.update_layout(title="3. Экспериментальные точки + теоретическая модель (МНК)",
                              xaxis_title="Размер N (элементов)",
                              yaxis_title="Время T(N) (мс)", template="plotly_white")
        st.plotly_chart(fit_fig, use_container_width=True)
        st.caption("Общая сетка мала для уверенной оценки сложности QuickSort. "
                   "В научном отчёте используй полные диапазоны N из ТЗ.")

st.divider()
st.subheader("Дополнительно: память Python")
if st.button("Измерить дополнительную память"):
    st.session_state.show_memory = True

if st.session_state.get("show_memory", False):
    if not selected:
        st.warning("Нужно выбрать алгоритм")
    else:
        with st.spinner("tracemalloc замеряет выделения памяти..."):
            memories = memory_profile(names=selected, distributions=[kind])
        df_mem = pd.DataFrame(memories)
        fig = px.line(df_mem, x="n", y="peak_kib", color="algorithm", markers=True,
                      template="plotly_white",
                      labels={"n": "Размер массива N (элементов)",
                              "peak_kib": "Дополнительная память (КиБ)",
                              "algorithm": "Алгоритм"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_mem, use_container_width=True)
        st.caption("tracemalloc отслеживает выделения Python после создания входного массива, "
                   "а не всю оперативную память процесса.")

st.divider()
st.subheader("Пошаговая визуализация (20–30 элементов)")
trace_name = st.selectbox("Алгоритм для анимации", list(SORTS), key="trace_name")
trace_kind = st.selectbox("Входные данные", list(DISTRIBUTIONS),
                          format_func=lambda value: DISTRIBUTIONS[value], key="trace_kind")
trace_n = st.slider("Количество элементов", 20, 30, 20, key="trace_n")
trace_seed = st.number_input("Seed для воспроизводимости", 0, 1000000, 42, key="trace_seed")

@st.cache_data(show_spinner=False)
def get_steps(name: str, distribution: str, size: int, seed: int):
    return trace_sort(name, generate_data(size, distribution, seed))

steps = get_steps(trace_name, trace_kind, trace_n, trace_seed)
trace_key = (trace_name, trace_kind, trace_n, trace_seed)
if st.session_state.get("last_trace_key") != trace_key:
    st.session_state.last_trace_key = trace_key
    st.session_state.step_slider = 0

left, middle, right = st.columns([1, 1, 4])
with left:
    if st.button("◀ Назад"):
        st.session_state.step_slider = max(0, st.session_state.step_slider - 1)
with middle:
    if st.button("Вперёд ▶"):
        st.session_state.step_slider = min(len(steps) - 1, st.session_state.step_slider + 1)
with right:
    st.slider("Шаг", 0, len(steps) - 1, key="step_slider")

current = steps[st.session_state.step_slider]
colors = ["#EF8B5A" if i in current["active"] else "#4E79A7"
          for i in range(len(current["values"]))]
bar = go.Figure(go.Bar(x=list(range(len(current["values"]))), y=current["values"],
                       marker_color=colors))
bar.update_layout(title=f"Шаг {st.session_state.step_slider + 1} из {len(steps)}",
                  xaxis_title="Индекс элемента (с нуля)",
                  yaxis_title="Значение", template="plotly_white", height=380)
st.plotly_chart(bar, use_container_width=True)
st.write("**Что происходит:**", current["description"])
st.caption("Оранжевым отмечены рассматриваемые позиции. "
           "Пошаговая визуализация работает отдельно от функции бенчмарка, "
           "чтобы сохранение кадров не увеличивало измеряемое время.")
