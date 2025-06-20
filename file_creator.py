"""
Модуль для создания CSV файла с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os


class FileCreator:
    """Класс для создания CSV файла с данными о браузерах"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.entries = {}
        self.data = []

        # Определяем поля для таблицы браузеров
        self.fields = {
            'browser_id': 'ID браузера',
            'browser_name': 'Название браузера',
            'developer': 'Разработчик',
            'release_date': 'Год выпуска',
            'latest_version': 'Последняя версия',
            'engine': 'Движок'
        }

    def show(self):
        """Показать окно создания файла"""
        if self.window is not None:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Создание файла данных")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов окна"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Создание файла с данными о браузерах",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Поля ввода данных
        row = 1
        for field_name, field_label in self.fields.items():
            ttk.Label(main_frame, text=f"{field_label}:").grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )

            entry = ttk.Entry(main_frame, width=40)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[field_name] = entry
            row += 1

        # Кнопки управления записями
        buttons_frame = ttk.LabelFrame(main_frame, text="Управление записями", padding="10")
        buttons_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)

        ttk.Button(
            buttons_frame,
            text="Добавить запись",
            command=self.add_record
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            buttons_frame,
            text="Очистить поля",
            command=self.clear_fields
        ).grid(row=0, column=1, padx=5)

        # Список добавленных записей
        list_frame = ttk.LabelFrame(main_frame, text="Добавленные записи", padding="10")
        list_frame.grid(row=row + 1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(row + 1, weight=1)

        # Создаем Treeview для отображения записей
        self.tree = ttk.Treeview(list_frame, columns=list(self.fields.keys()), show="headings", height=8)

        # Настраиваем заголовки столбцов
        for field_name, field_label in self.fields.items():
            self.tree.heading(field_name, text=field_label)
            self.tree.column(field_name, width=100, minwidth=80)

        # Скроллбары для списка
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Кнопки управления списком
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(
            list_buttons_frame,
            text="Удалить выбранную",
            command=self.delete_selected
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            list_buttons_frame,
            text="Очистить список",
            command=self.clear_list
        ).grid(row=0, column=1, padx=5)

        # Кнопки сохранения файла
        save_frame = ttk.Frame(main_frame)
        save_frame.grid(row=row + 2, column=0, columnspan=2, pady=20)

        ttk.Button(
            save_frame,
            text="Сохранить как CSV",
            command=self.save_file
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            save_frame,
            text="Загрузить образец данных",
            command=self.load_sample_data
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            save_frame,
            text="Закрыть",
            command=self.close_window
        ).grid(row=0, column=2, padx=5)

    def add_record(self):
        """Добавить запись в список"""
        # Проверяем заполненность обязательных полей
        record = {}
        for field_name, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Поле '{self.fields[field_name]}' не может быть пустым!"
                )
                entry.focus()
                return
            record[field_name] = value

        # Проверяем уникальность ID
        browser_id = record['browser_id']
        for existing_record in self.data:
            if existing_record['browser_id'] == browser_id:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Браузер с ID '{browser_id}' уже существует!"
                )
                self.entries['browser_id'].focus()
                return

        # Добавляем запись в данные и в список
        self.data.append(record)
        self.tree.insert('', tk.END, values=list(record.values()))

        self.clear_fields()
        messagebox.showinfo("Успех", "Запись успешно добавлена!")

    def clear_fields(self):
        """Очистить поля ввода"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def delete_selected(self):
        """Удалить выбранную запись"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            # Получаем индекс записи
            item_index = self.tree.index(selected_item[0])

            # Удаляем из данных и из списка
            del self.data[item_index]
            self.tree.delete(selected_item[0])

            messagebox.showinfo("Успех", "Запись удалена!")

    def clear_list(self):
        """Очистить весь список"""
        if not self.data:
            messagebox.showinfo("Информация", "Список уже пуст!")
            return

        if messagebox.askyesno("Подтверждение", "Очистить весь список записей?"):
            self.data.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            messagebox.showinfo("Успех", "Список очищен!")

    def load_sample_data(self):
        """Загрузить образец данных"""
        if messagebox.askyesno(
                "Подтверждение",
                "Загрузить образец данных? Текущие данные будут заменены."
        ):
            # Очищаем текущие данные
            self.data.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Добавляем образец данных
            sample_data = [
                {
                    'browser_id': '1',
                    'browser_name': 'Mozilla Firefox',
                    'developer': 'Mozilla Foundation',
                    'release_date': '2004',
                    'latest_version': '120.0',
                    'engine': 'Gecko'
                },
                {
                    'browser_id': '2',
                    'browser_name': 'Google Chrome',
                    'developer': 'Google LLC',
                    'release_date': '2008',
                    'latest_version': '119.0.6045.199',
                    'engine': 'Blink'
                },
                {
                    'browser_id': '3',
                    'browser_name': 'Microsoft Edge',
                    'developer': 'Microsoft',
                    'release_date': '2015',
                    'latest_version': '119.0.2151.97',
                    'engine': 'Blink'
                },
                {
                    'browser_id': '4',
                    'browser_name': 'Safari',
                    'developer': 'Apple',
                    'release_date': '2003',
                    'latest_version': '17.1',
                    'engine': 'WebKit'
                },
                {
                    'browser_id': '5',
                    'browser_name': 'Opera',
                    'developer': 'Opera Software',
                    'release_date': '1995',
                    'latest_version': '105.0.4970.21',
                    'engine': 'Blink'
                }
            ]

            for record in sample_data:
                self.data.append(record)
                self.tree.insert('', tk.END, values=list(record.values()))

            messagebox.showinfo("Успех", "Образец данных загружен!")

    def save_file(self):
        """Сохранить данные в CSV файл"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения!")
            return

        # Диалог выбора файла для сохранения
        filename = filedialog.asksaveasfilename(
            title="Сохранить файл как",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = list(self.fields.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    # Записываем заголовки
                    writer.writeheader()

                    # Записываем данные
                    for record in self.data:
                        writer.writerow(record)

                messagebox.showinfo(
                    "Успех",
                    f"Файл успешно сохранен!\nПуть: {filename}\nЗаписей: {len(self.data)}"
                )

            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при сохранении файла:\n{str(e)}"
                )

    def close_window(self):
        """Закрыть окно"""
        if self.window:
            self.window.destroy()
            self.window = None