import sqlite3
import time
import random
import tkinter as tk
from tkinter import messagebox, ttk

# --- Настройка Базы Данных и Кэша ---
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        date TEXT,
        category TEXT,
        organizer TEXT,
        capacity INTEGER,
        price REAL,
        status TEXT
    )
''')
conn.commit()

# Оптимизированный кэш в оперативной памяти (структурированный реестр)
MEMORY_CACHE = []


# --- Логика Приложения ---
def calculate_analytics():
    """Перерасчет аналитических показателей системы"""
    if not MEMORY_CACHE:
        label_total.config(text="Всего мероприятий: 0")
        label_avg_price.config(text="Средняя стоимость: 0 руб.")
        label_total_capacity.config(text="Общая вместимость: 0 чел.")
        return

    total_events = len(MEMORY_CACHE)
    total_price = sum(item["price"] for item in MEMORY_CACHE)
    total_capacity = sum(item["capacity"] for item in MEMORY_CACHE)

    avg_price = total_price / total_events

    label_total.config(text=f"Всего мероприятий: {total_events}")
    label_avg_price.config(text=f"Средняя стоимость: {avg_price:.1f} руб.")
    label_total_capacity.config(text=f"Общая вместимость: {total_capacity} чел.")


def add_event_advanced():
    """Добавление нового мероприятия с валидацией и замером времени кэширования"""
    name = entry_name.get().strip()
    city = entry_city.get().strip()
    date = entry_date.get().strip()
    category = combo_category.get()
    organizer = entry_org.get().strip()
    capacity_str = entry_capacity.get().strip()
    price_str = entry_price.get().strip()
    status = combo_status.get()

    # Полная валидация полей
    if not all([name, city, date, organizer, capacity_str, price_str]):
        messagebox.showwarning("Валидация", "Ошибка! Заполните все поля формы.")
        return

    try:
        capacity = int(capacity_str)
        price = float(price_str)
    except ValueError:
        messagebox.showerror("Ошибка типов", "Вместимость должна быть целым числом, а цена — числом!")
        return

    # ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ: Замер скорости сохранения в высокоскоростной буфер
    start_time = time.perf_counter()

    event_obj = {
        "name": name, "city": city, "date": date, "category": category,
        "organizer": organizer, "capacity": capacity, "price": price, "status": status
    }
    MEMORY_CACHE.append(event_obj)

    # Запись в СУБД
    cursor.execute('''
        INSERT INTO system_events (name, city, date, category, organizer, capacity, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, city, date, category, organizer, capacity, price, status))

    end_time = time.perf_counter()

    # Выводим время эксперимента
    execution_time = (end_time - start_time) * 1000
    label_time.config(text=f"Скорость обработки транзакции (RAM-буфер): {execution_time:.4f} мс")

    # Обновление таблицы интерфейса
    refresh_table(MEMORY_CACHE)
    calculate_analytics()

    # Очистка полей формы
    for entry in [entry_name, entry_city, entry_date, entry_org, entry_capacity, entry_price]:
        entry.delete(0, tk.END)


def refresh_table(data_list):
    """Обновление визуального списка (Treeview)"""
    for row in tree.get_children():
        tree.delete(row)
    for item in data_list:
        tree.insert("", tk.END, values=(
            item["name"], item["city"], item["date"], item["category"],
            item["organizer"], item["capacity"], f"{item['price']} руб.", item["status"]
        ))


def search_events(event=None):
    """Быстрый поиск по названию или городу прямо внутри кэша (без SQL-запросов)"""
    query = entry_search.get().strip().lower()
    if not query:
        refresh_table(MEMORY_CACHE)
        return

    filtered_data = [
        item for item in MEMORY_CACHE
        if query in item["name"].lower() or query in item["city"].lower()
    ]
    refresh_table(filtered_data)


def export_report():
    """Экспорт реестра мероприятий в файл отчета"""
    if not MEMORY_CACHE:
        messagebox.showinfo("Экспорт", "Реестр пуст. Нечего экспортировать.")
        return

    filename = "Отчет_Мероприятия_Суслов.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=== СЕРВИС ОРГАНИЗАЦИИ МЕРОПРИЯТИЙ (ОТЧЕТ ПРАКТИКИ) ===\n\n")
        for idx, item in enumerate(MEMORY_CACHE, 1):
            f.write(f"{idx}. {item['name']} | Город: {item['city']} | Дата: {item['date']} | "
                    f"Категория: {item['category']} | Организатор: {item['organizer']} | "
                    f"Вместимость: {item['capacity']} чел. | Цена: {item['price']} руб. | Статус: {item['status']}\n")

    messagebox.showinfo("Успех", f"Отчет успешно сохранен в файл:\n{filename}")


# --- Построение Интерфейса ---
root = tk.Tk()
root.title("Сервис мероприятий — Версия 2: ERP-Система (Суслов)")
root.geometry("950x720")  # Увеличили высоту окна с 650 до 720
root.configure(bg="#f4f6f7")

# Заголовок
tk.Label(root, text="ПАНЕЛЬ УПРАВЛЕНИЯ СЕРВИСОМ МЕРОПРИЯТИЙ (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)",
         font=("Arial", 12, "bold"), bg="#f4f6f7", fg="#2c3e50").pack(pady=10)

# Главный контейнер
main_frame = tk.Frame(root, bg="#f4f6f7")
main_frame.pack(fill="both", expand=True, padx=15, pady=5)

# ЛЕВАЯ ЧАСТЬ: ФОРМА ВВОДА
form_frame = tk.LabelFrame(main_frame, text=" Добавление нового мероприятия ", font=("Arial", 10, "bold"), bg="white",
                           pady=5, width=320)
form_frame.pack(side="left", fill="both", padx=5, expand=False)
form_frame.pack_propagate(False)

# Объявление всех полей ввода с уменьшенными отступами pady=1
tk.Label(form_frame, text="Название:", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_name = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_name.pack(fill="x", padx=15, pady=2)

tk.Label(form_frame, text="Город проведения:", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_city = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_city.pack(fill="x", padx=15, pady=2)

tk.Label(form_frame, text="Дата (ДД.ММ.ГГГГ):", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_date = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_date.pack(fill="x", padx=15, pady=2)

tk.Label(form_frame, text="Организатор:", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_org = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_org.pack(fill="x", padx=15, pady=2)

tk.Label(form_frame, text="Вместимость зала (чел):", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_capacity = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_capacity.pack(fill="x", padx=15, pady=2)

tk.Label(form_frame, text="Цена билета (руб):", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
entry_price = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
entry_price.pack(fill="x", padx=15, pady=2)

# Выпадающие списки
tk.Label(form_frame, text="Категория:", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
combo_category = ttk.Combobox(form_frame, values=["Концерт", "Конференция", "Выставка", "Спектакль", "Фестиваль"],
                              state="readonly")
combo_category.pack(fill="x", padx=15, pady=2)
combo_category.current(0)

tk.Label(form_frame, text="Статус события:", bg="white", font=("Arial", 9)).pack(anchor="w", padx=15, pady=1)
combo_status = ttk.Combobox(form_frame, values=["Регистрация открыта", "Мест нет", "Завершено"], state="readonly")
combo_status.pack(fill="x", padx=15, pady=2)
combo_status.current(0)

# Кнопка добавления
btn_add = tk.Button(form_frame, text="Создать мероприятие", bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                    command=add_event_advanced, relief="flat")
btn_add.pack(fill="x", padx=15, pady=10)

# СПРАВА ЧАСТЬ: ПОИСК, ТАБЛИЦА, АНАЛИТИКА
right_frame = tk.Frame(main_frame, bg="#f4f6f7")
right_frame.pack(side="right", fill="both", expand=True, padx=5)

# Блок поиска
search_frame = tk.Frame(right_frame, bg="#f4f6f7")
search_frame.pack(fill="x", pady=2)
tk.Label(search_frame, text="Быстрый фильтр (по имени / городу):", font=("Arial", 9, "bold"), bg="#f4f6f7").pack(
    side="left", padx=5)
entry_search = tk.Entry(search_frame, font=("Arial", 10), bd=1, relief="solid")
entry_search.pack(side="left", fill="x", expand=True, padx=5)
entry_search.bind("<KeyRelease>", search_events)

# Таблица элементов
table_frame = tk.Frame(right_frame)
table_frame.pack(fill="both", expand=True, pady=5)

columns = ("name", "city", "date", "category", "org", "capacity", "price", "status")
tree = ttk.Treeview(table_frame, columns=columns, show="headings")

tree.heading("name", text="Название")
tree.heading("city", text="Город")
tree.heading("date", text="Дата")
tree.heading("category", text="Категория")
tree.heading("org", text="Организатор")
tree.heading("capacity", text="Мест")
tree.heading("price", text="Цена")
tree.heading("status", text="Статус")

for col in columns:
    tree.column(col, width=95, anchor="center")
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# НИЖНЯЯ ЧАСТЬ: АНАЛИТИКА И ЭКСПЕРИМЕНТ
bottom_frame = tk.LabelFrame(root, text=" Аналитический модуль и Вычислительный эксперимент ",
                             font=("Arial", 10, "bold"), bg="white")
bottom_frame.pack(fill="x", padx=20, pady=10)

label_total = tk.Label(bottom_frame, text="Всего мероприятий: 0", font=("Arial", 10), bg="white")
label_total.grid(row=0, column=0, padx=20, pady=5, sticky="w")

label_avg_price = tk.Label(bottom_frame, text="Средняя стоимость: 0 руб.", font=("Arial", 10), bg="white")
label_avg_price.grid(row=0, column=1, padx=20, pady=5, sticky="w")

label_total_capacity = tk.Label(bottom_frame, text="Общая вместимость: 0 чел.", font=("Arial", 10), bg="white")
label_total_capacity.grid(row=0, column=2, padx=20, pady=5, sticky="w")

btn_export = tk.Button(bottom_frame, text="Выгрузить отчет (.TXT)", bg="#2980b9", fg="white", font=("Arial", 9, "bold"),
                       command=export_report, relief="flat")
btn_export.grid(row=0, column=3, padx=20, pady=5, sticky="e")

label_time = tk.Label(bottom_frame, text="Скорость обработки транзакции (RAM-буфер): -", font=("Arial", 10, "bold"),
                      fg="#27ae60", bg="white")
label_time.grid(row=1, column=0, columnspan=4, padx=20, pady=5, sticky="w")

root.mainloop()
