import sqlite3
import time
import tkinter as tk
from tkinter import messagebox

# База данных
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        city TEXT,
        price TEXT
    )
''')
conn.commit()


def add_event():
    name = entry_name.get().strip()
    city = entry_city.get().strip()
    price = entry_price.get().strip()

    if not name or not city or not price:
        messagebox.showwarning("Ошибка", "Заполните все поля формы!")
        return

    # Вычислительный эксперимент: замеряем чистую скорость вставки СУБД
    start_time = time.perf_counter()
    cursor.execute("INSERT INTO events (name, city, price) VALUES (?, ?, ?)", (name, city, price))
    conn.commit()
    end_time = time.perf_counter()

    execution_time = (end_time - start_time) * 1000  # в миллисекундах
    label_time.config(text=f"Время записи в БД: {execution_time:.4f} мс")

    # Обновляем список на экране
    listbox.insert(tk.END, f"{name} ({city}) — {price} руб.")

    # Очищаем поля
    entry_name.delete(0, tk.END)
    entry_city.delete(0, tk.END)
    entry_price.delete(0, tk.END)


# Интерфейс формы
root = tk.Tk()
root.title("Сервис мероприятий — Версия 1 (Суслов)")
root.geometry("400x450")

tk.Label(root, text="ОРГАНИЗАЦИЯ МЕРОПРИЯТИЯ (БАЗОВАЯ БД)", font=("Arial", 11, "bold")).pack(pady=10)

tk.Label(root, text="Название мероприятия:").pack(anchor="w", padx=20)
entry_name = tk.Entry(root, font=("Arial", 10))
entry_name.pack(fill="x", padx=20, pady=5)

tk.Label(root, text="Город проведения:").pack(anchor="w", padx=20)
entry_city = tk.Entry(root, font=("Arial", 10))
entry_city.pack(fill="x", padx=20, pady=5)

tk.Label(root, text="Стоимость билета (руб):").pack(anchor="w", padx=20)
entry_price = tk.Entry(root, font=("Arial", 10))
entry_price.pack(fill="x", padx=20, pady=5)

btn_add = tk.Button(root, text="Создать мероприятие", bg="#34495e", fg="white", font=("Arial", 10, "bold"),
                    command=add_event)
btn_add.pack(fill="x", padx=20, pady=15)

tk.Label(root, text="Список созданных мероприятий:").pack(anchor="w", padx=20)
listbox = tk.Listbox(root, font=("Arial", 10))
listbox.pack(fill="both", expand=True, padx=20, pady=5)

label_time = tk.Label(root, text="Время записи в БД: -", font=("Arial", 10, "bold"), fg="#c0392b")
label_time.pack(pady=10)

root.mainloop()
