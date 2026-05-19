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
