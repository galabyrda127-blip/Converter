import tkinter as tk
from tkinter import ttk, messagebox
import requests


# ---------------------------------------
# Получение списка валют
# ---------------------------------------

def get_currencies():
    url = "https://api.frankfurter.dev/v2/currencies"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    currencies = []

    for currency in data:
        currencies.append(currency["iso_code"])

    return sorted(currencies)


# ---------------------------------------
# Получение курса валют
# ---------------------------------------

def get_rate(base_currency, target_currency):
    url = (
        "https://api.frankfurter.dev/v2/latest"
        f"?from={base_currency.upper()}"
        f"&to={target_currency.upper()}"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    if target_currency.upper() not in data.get("rates", {}):
        raise KeyError(target_currency)

    rate = data["rates"][target_currency.upper()]
    date = data["date"]

    return rate, date


# ---------------------------------------
# Поиск валюты при вводе
# ---------------------------------------

def filter_currencies(event):
    combobox = event.widget

    # Что сейчас написал пользователь
    typed = combobox.get().upper()

    # Ищем валюты, которые начинаются с введённых букв
    filtered = [
        currency
        for currency in currencies
        if currency.startswith(typed)
    ]

    # Обновляем список
    combobox["values"] = filtered

    # Если есть подходящие валюты,
    # открываем выпадающий список
    if filtered:
        combobox.event_generate("<Down>")


# ---------------------------------------
# Конвертация
# ---------------------------------------

def convert_currency():
    try:
        amount_text = amount_entry.get().strip()
        amount_text = amount_text.replace(",", ".")

        amount = float(amount_text)

        if amount <= 0:
            messagebox.showerror(
                "Ошибка",
                "Сумма должна быть больше нуля."
            )
            return

        base_currency = from_currency.get().strip().upper()
        target_currency = to_currency.get().strip().upper()

        # Проверяем исходную валюту
        if base_currency not in currencies:
            messagebox.showerror(
                "Ошибка",
                "Такой исходной валюты нет в списке."
            )
            return

        # Проверяем конечную валюту
        if target_currency not in currencies:
            messagebox.showerror(
                "Ошибка",
                "Такой конечной валюты нет в списке."
            )
            return

        # Если валюты одинаковые
        if base_currency == target_currency:
            rate = 1
            result = amount
            date = "не требуется"

        else:
            rate, date = get_rate(
                base_currency,
                target_currency
            )

            result = amount * rate

        # Показываем результат
        result_label.config(
            text=(
                f"{amount:.2f} {base_currency} = "
                f"{result:.2f} {target_currency}"
            )
        )

        # Показываем курс
        rate_label.config(
            text=(
                f"Курс: 1 {base_currency} = "
                f"{rate:.4f} {target_currency}"
            )
        )

        # Показываем дату
        date_label.config(
            text=f"Дата курса: {date}"
        )

    except ValueError:
        messagebox.showerror(
            "Ошибка",
            "Введите корректную сумму."
        )

    except requests.exceptions.RequestException:
        messagebox.showerror(
            "Ошибка подключения",
            "Не удалось получить данные с сервера.\n"
            "Проверьте подключение к интернету."
        )

    except KeyError:
        messagebox.showerror(
            "Ошибка",
            "Сервер вернул неожиданные данные."
        )


# ---------------------------------------
# Поменять валюты местами
# ---------------------------------------

def swap_currencies():
    base_currency = from_currency.get()
    target_currency = to_currency.get()

    from_currency.set(target_currency)
    to_currency.set(base_currency)


# ---------------------------------------
# Создаём главное окно
# ---------------------------------------

window = tk.Tk()

window.title("Конвертер валют")
window.geometry("500x450")
window.resizable(False, False)


# ---------------------------------------
# Заголовок
# ---------------------------------------

title_label = ttk.Label(
    window,
    text="Конвертер валют",
    font=("Arial", 20, "bold")
)

title_label.pack(pady=20)


# ---------------------------------------
# Поле суммы
# ---------------------------------------

amount_label = ttk.Label(
    window,
    text="Введите сумму:"
)

amount_label.pack()

amount_entry = ttk.Entry(
    window,
    width=30
)

amount_entry.pack(pady=5)
amount_entry.insert(0, "100")


# ---------------------------------------
# Выбор исходной валюты
# ---------------------------------------

from_label = ttk.Label(
    window,
    text="Из какой валюты:"
)

from_label.pack(pady=(15, 0))

from_currency = ttk.Combobox(
    window,
    state="normal",
    width=27
)

from_currency.pack(pady=5)


# ---------------------------------------
# Кнопка обмена валют
# ---------------------------------------

swap_button = ttk.Button(
    window,
    text="Поменять валюты",
    command=swap_currencies
)

swap_button.pack(pady=5)


# ---------------------------------------
# Выбор конечной валюты
# ---------------------------------------

to_label = ttk.Label(
    window,
    text="В какую валюту:"
)

to_label.pack(pady=(10, 0))

to_currency = ttk.Combobox(
    window,
    state="normal",
    width=27
)

to_currency.pack(pady=5)


# ---------------------------------------
# Кнопка конвертации
# ---------------------------------------

convert_button = ttk.Button(
    window,
    text="Конвертировать",
    command=convert_currency
)

convert_button.pack(pady=20)


# ---------------------------------------
# Результат
# ---------------------------------------

result_label = ttk.Label(
    window,
    text="Результат появится здесь",
    font=("Arial", 14, "bold")
)

result_label.pack(pady=5)


rate_label = ttk.Label(
    window,
    text="Курс: —"
)

rate_label.pack()


date_label = ttk.Label(
    window,
    text="Дата курса: —"
)

date_label.pack(pady=5)


# ---------------------------------------
# Загружаем валюты
# ---------------------------------------

try:
    currencies = get_currencies()

    # Передаём список валют в оба поля
    from_currency["values"] = currencies
    to_currency["values"] = currencies

    # Значения по умолчанию


except requests.exceptions.RequestException:
    currencies = []

    messagebox.showerror(
        "Ошибка",
        "Не удалось загрузить список валют.\n"
        "Проверьте подключение к интернету."
    )


# ---------------------------------------
# Включаем поиск по первым буквам
# ---------------------------------------

from_currency.bind(
    "<KeyRelease>",
    filter_currencies
)

to_currency.bind(
    "<KeyRelease>",
    filter_currencies
)


# ---------------------------------------
# Запускаем программу
# ---------------------------------------

window.mainloop()