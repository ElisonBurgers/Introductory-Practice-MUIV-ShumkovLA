"""
Ознакомительная Практика 1

Выполнил
Шумков Леонид Алексеевич
23.08.2006
ид 30.1/б3-24

#print((23+8+2006)%30)
Вариант 27
"""
### (Команда для установки библиотек) pip install requests pandas numpy matplotlib logging scipy

import requests
import pandas
import numpy
import matplotlib.pyplot
import logging
import scipy.stats

"""
ЗАДАНИЕ 1
Получить числовой ряд с помощью API
"""

print("\n{[]} ЗАДАНИЕ 1: ПОЛУЧИТЬ ЧИСЛОВОЙ РЯД С ПОМОЩЬЮ API {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 55.7558,
    "longitude": 37.6173,
    "start_date": "2023-01-01",
    "end_date": "2023-03-31",
    "hourly": "temperature_2m",
    "timezone": "Europe/Moscow"
}

response = requests.get(BASE_URL, params=params)
response.raise_for_status()
data = response.json()

timestamps = data["hourly"]["time"]
temperatures = data["hourly"]["temperature_2m"]
df_raw = pandas.DataFrame({"time": timestamps, "temperature": temperatures})
print(f"Загружено значений: {len(df_raw)}")
df_raw.to_csv("temperature_raw.csv", index=False)

"""
ЗАДАНИЕ 2
Провести очистку данных, логировать и вывести данные об очистке.
"""

print("\n{[]} ЗАДАНИЕ 2: ПРОВЕСТИ ОЧИСТКУ ДАННЫХ, ЛОГИРОВАТЬ И ВЫВЕСТИ ДАННЫЕ ОБ ОЧИСТКЕ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
logging.basicConfig(
    filename="cleaning.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Начало очистки данных")

df_raw["time"] = pandas.to_datetime(df_raw["time"])
logging.info("Столбец time преобразован в datetime")

miss_before = df_raw["temperature"].isna().sum()
logging.info(f"Пропусков до очистки: {miss_before}")
print(f"Пропусков до очистки: {miss_before}")

Q1 = df_raw["temperature"].quantile(0.25)
Q3 = df_raw["temperature"].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

before = len(df_raw)
df_clean = df_raw[(df_raw["temperature"] >= lower) & (df_raw["temperature"] <= upper)]
after = len(df_clean)
removed = before - after
logging.info(f"Удалено выбросов: {removed} ({(removed/before)*100:.2f}%)")
print(f"Удалено выбросов: {removed} из {before}")
print(f"Размер очищенных данных: {after}")
df_clean.to_csv("temperature_clean.csv", index=False)
logging.info("Очищенные данные сохранены в temperature_clean.csv")

"""
ЗАДАНИЕ 3
Сформировать объект для работы
"""

print("\n{[]} ЗАДАНИЕ 3: СФОРМИРОВАТЬ ОБЪЕКТ ДЛЯ РАБОТЫ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
temp_list = df_clean["temperature"].tolist()
temp_array = numpy.array(temp_list)
print(f"Список: длина {len(temp_list)}")
print(f"NumPy-массив: shape {temp_array.shape}, dtype {temp_array.dtype}")

"""
ЗАДАНИЕ 4
Рассчитать характеристики ряда, вывести их.

1.Минимум 
12.Среднеквадратическое отклонение
13.Размах
14.Коэффициент вариации
15.Третий квартиль
"""


print("\n{[]} ЗАДАНИЕ 4: РАССЧИТАТЬ ХАРАКТЕРИСТИКИ РЯДА, ВЫВЕСТИ ИХ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
min_val = numpy.min(temp_array)
std_val = numpy.std(temp_array, ddof=1)          # выборочное стандартное отклонение
range_val = numpy.max(temp_array) - numpy.min(temp_array)
mean_val = numpy.mean(temp_array)
cv_val = (std_val / mean_val) * 100 if mean_val != 0 else numpy.nan
q3_val = numpy.percentile(temp_array, 75)

print(f"1. Минимум:                        {min_val:.2f} °C")
print(f"2. Среднеквадратическое отклонение: {std_val:.2f} °C")
print(f"3. Размах:                          {range_val:.2f} °C")
print(f"4. Коэффициент вариации:            {cv_val:.2f} %")
print(f"5. Третий квартиль (Q3):            {q3_val:.2f} °C")


"""
ЗАДАНИЕ 5
Провести визуализацию

3.Гистограмма
4.Ящик с усами
5.График отсортированных значений (по возрастанию или убыванию)
"""

print("\n{[]} ЗАДАНИЕ 5: ПРОВЕСТИ ВИЗУАЛИЗАЦИЮ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
matplotlib.pyplot.figure(figsize=(15, 5))

matplotlib.pyplot.subplot(1, 3, 1)
matplotlib.pyplot.hist(df_clean["temperature"], bins=30, color="skyblue", edgecolor="black")
matplotlib.pyplot.title("Гистограмма температуры")
matplotlib.pyplot.xlabel("Температура (°C)")
matplotlib.pyplot.ylabel("Частота")

matplotlib.pyplot.subplot(1, 3, 2)
matplotlib.pyplot.boxplot(df_clean["temperature"], vert=True, patch_artist=True, boxprops=dict(facecolor="lightgreen"))
matplotlib.pyplot.title("Ящик с усами")
matplotlib.pyplot.ylabel("Температура (°C)")
matplotlib.pyplot.xticks([1], ["Температура"])

matplotlib.pyplot.subplot(1, 3, 3)
sorted_temps = sorted(df_clean["temperature"])
matplotlib.pyplot.plot(sorted_temps, color="coral", linewidth=0.8)
matplotlib.pyplot.title("Отсортированные значения")
matplotlib.pyplot.xlabel("Порядковый номер")
matplotlib.pyplot.ylabel("Температура (°C)")

matplotlib.pyplot.tight_layout()
matplotlib.pyplot.savefig("visualization.png", dpi=150)
matplotlib.pyplot.show()
print("Графики сохранены в visualization.png")

"""
ЗАДАНИЕ 6
Провести анализ пропусков внутри временного ряда.
Предусмотреть метод заполнения пропусков
Логировать наличие/отсутствие пропусков и метод их устранения.
"""

print("\n{[]} ЗАДАНИЕ 6: ПРОВЕСТИ АНАЛИЗ ПРОПУСКОВ ВНУТРИ ВРЕМЕННОГО РЯДА {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
logging.info("Задание 6: анализ пропусков")
df_missing = df_clean.copy()  # копия, чтобы не менять оригинал

real_miss = df_missing["temperature"].isna().sum()
print(f"Реальных пропусков в очищенных данных: {real_miss}")
logging.info(f"Реальных пропусков: {real_miss}")

if real_miss == 0:
    numpy.random.seed(42)
    idx = numpy.random.choice(df_missing.index, size=5, replace=False)
    df_missing.loc[idx, "temperature"] = numpy.nan
    print("Добавлено 5 искусственных пропусков.")
    logging.info("Добавлено 5 искусственных пропусков")

median_temp = df_missing["temperature"].median()
df_missing["temperature"] = df_missing["temperature"].fillna(median_temp)
remaining = df_missing["temperature"].isna().sum()
print(f"Пропуски заполнены медианой ({median_temp:.2f} °C). Осталось пропусков: {remaining}")
logging.info(f"Пропуски заполнены медианой {median_temp:.2f}°C, осталось: {remaining}")

"""
ЗАДАНИЕ 7
Сгруппировать данные по категориальному признаку, вывести сгруппированные данные.
"""

print("\n{[]} ЗАДАНИЕ 7: ГРУППИРОВКА ПО ДНЯМ НЕДЕЛИ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
df_clean["day_of_week"] = df_clean["time"].dt.day_name()
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
grouped = df_clean.groupby("day_of_week")["temperature"].agg(["mean", "std", "count"])
grouped = grouped.reindex(order)
grouped.columns = ["Средняя температура", "Стандартное отклонение", "Количество"]
print(grouped.to_string())
grouped.to_csv("grouped_by_weekday.csv")
print("Сгруппированные данные сохранены в grouped_by_weekday.csv")

"""
ЗАДАНИЕ 8 
Найти тройку наибольших и наименьших значений, вывести их.
"""

print("\n{[]} ЗАДАНИЕ 8: ТРОЙКИ НАИБОЛЬШИХ/НАИМЕНЬШИХ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
n = 3
smallest = df_clean.nsmallest(n, "temperature")
largest = df_clean.nlargest(n, "temperature")
print("Три самых низких температуры:")
print(smallest[["time", "temperature"]].to_string(index=False))
print("\nТри самых высоких температуры:")
print(largest[["time", "temperature"]].to_string(index=False))

"""
ЗАДАНИЕ 9
Сформулировать и проверить гипотезу на очищенных данных
"""

# Проверка гипотезы о сезонности (различии температур по дням недели)
# Гипотеза H0: средние температуры во все дни недели равны (сезонности нет)
# Гипотеза H1: хотя бы в один день средняя отличается (сезонность есть)
# Используем непараметрический критерий Краскела-Уоллиса

print("\n{[]} ЗАДАНИЕ 9: ПРОВЕРКА ГИПОТЕЗЫ О СЕЗОННОСТИ {[]}")
print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")

groups = []
for day in order:
    groups.append(df_clean[df_clean["day_of_week"] == day]["temperature"].dropna().values)

def kruskal_wallis(*samples):
    """Возвращает H-статистику и p-value для теста Краскела-Уоллиса."""
    all_data = numpy.concatenate(samples)
    n = len(all_data)
    ranks = numpy.zeros(n)

    order_ = numpy.argsort(all_data)
    ranks[order_] = numpy.arange(1, n+1)

    uniq, inverse, counts = numpy.unique(all_data, return_inverse=True, return_counts=True)
    for i in range(len(uniq)):
        if counts[i] > 1:
            idx = numpy.where(inverse == i)[0]
            ranks[idx] = numpy.mean(ranks[idx])

    rk_groups = []
    start = 0
    for s in samples:
        end = start + len(s)
        rk_groups.append(ranks[start:end])
        start = end

    k = len(samples)
    R_sums = numpy.array([numpy.sum(r) for r in rk_groups])
    n_i = numpy.array([len(s) for s in samples])
    H = (12 / (n*(n+1))) * numpy.sum(R_sums**2 / n_i) - 3*(n+1)

    p = 1 - scipy.stats.chi2.cdf(H, k-1)
    return H, p

H_stat, p_val = kruskal_wallis(*groups)
alpha = 0.05
print(f"Статистика Краскела-Уоллиса H = {H_stat:.4f}")
print(f"p-значение = {p_val:.4f}")
if p_val < alpha:
    print(f"p < {alpha} → отвергаем нулевую гипотезу.")
    print("Вывод: обнаружена статистически значимая сезонность (различие средних по дням недели).")
else:
    print(f"p >= {alpha} → нет оснований отвергнуть нулевую гипотезу.")
    print("Вывод: сезонность не подтверждена.")

#ОБЪЕДИНЕНИЕ ВСЕХ CSV-ФАЙЛОВ ДЛЯ ОТЧЁТА НА ВСЯКИЙ СЛУЧАЙ
print("\n=== ОБЪЕДИНЕНИЕ ДАННЫХ В ОДИН ФАЙЛ ===")

# Загрузка сырых данных
raw = pandas.read_csv("temperature_raw.csv")
raw = raw.rename(columns={"time": "Время", "temperature": "Температура"})
raw["Тип"] = "Исходные данные"

# Загрузка очищенных данных
clean = pandas.read_csv("temperature_clean.csv")
clean = clean.rename(columns={"time": "Время", "temperature": "Температура"})
clean["Тип"] = "Очищенные данные"

# Загрузка сгруппированных данных (индекс – день недели)
grouped = pandas.read_csv("grouped_by_weekday.csv", index_col=0)
grouped = grouped.reset_index().rename(columns={"index": "День недели"})
grouped["Тип"] = "Группировка по дням недели"

# Порядок типов для сортировки
type_order = ["Исходные данные", "Очищенные данные", "Группировка по дням недели"]
type_dtype = pandas.CategoricalDtype(categories=type_order, ordered=True)

# Единый набор столбцов
all_columns = ["Тип", "Время", "Температура", "День недели", "Средняя температура", "Стандартное отклонение", "Количество"]

# Приведение всех датафреймов к общему списку колонок
raw_full = raw.reindex(columns=all_columns)
clean_full = clean.reindex(columns=all_columns)
grouped_full = grouped.reindex(columns=all_columns)

# Объединение
combined = pandas.concat([raw_full, clean_full, grouped_full], ignore_index=True)

# Сортировка: по типу (категориальный порядок), затем по времени, затем по дню недели
combined["Тип"] = combined["Тип"].astype(type_dtype)

day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_dtype = pandas.CategoricalDtype(categories=day_order, ordered=True)
combined["День недели"] = combined["День недели"].astype(day_dtype)

combined = combined.sort_values(
    by=["Тип", "Время", "День недели"],
    ascending=[True, True, True],
    na_position="last"
)

# Сохранение в единый CSV
combined.to_csv("combined_all_data.csv", index=False, encoding="utf-8-sig")
print("Сводный файл сохранён как combined_all_data.csv")
