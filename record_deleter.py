"""
Модуль для удаления записей из файла CSV с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os


class RecordDeleter:
    """Класс для удаления записей из файла"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.filename = ""
        self.records = []
        self.headers = ["browser_id", "browser_name", "developer", "release_date", "latest_version", "engine"]

    def show(self):
        """Показ окна удаления записей"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Удаление записей")
        self.window.geometry("900x600")
        self.window.resizable(True, True)

        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов окна"""
        # Главный фрейм
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(main_frame, text="Выбор файла", padding="5")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(file_frame, text="Выбрать файл", command=self.select_file).grid(row=0, column=0, padx=(0, 10))

        self.file_var = tk.StringVar()
        ttk.Label(file_frame, textvariable=self.file_var).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Фрейм для кнопок управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(control_frame, text="Загрузить данные", command=self.load_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Удалить выбранные", command=self.delete_selected).grid(row=0, column=1,
                                                                                               padx=(0, 10))
        ttk.Button(control_frame, text="Удалить все", command=self.delete_all).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(control_frame, text="Сохранить изменения", command=self.save_data).grid(row=0, column=3,
                                                                                           padx=(0, 10))
        ttk.Button(control_frame, text="Обновить таблицу", command=self.refresh_table).grid(row=0, column=4)

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация и поиск", padding="5")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(filter_frame, text="Поиск по названию:").grid(row=0, column=0, padx=(0, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(filter_frame, text="Фильтр по разработчику:").grid(row=0, column=2, padx=(0, 10))
        self.developer_var = tk.StringVar()
        self.developer_combo = ttk.Combobox(filter_frame, textvariable=self.developer_var, width=15, state="readonly")
        self.developer_combo.grid(row=0, column=3, padx=(0, 10))
        self.developer_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=4)

        # Таблица для отображения записей
        table_frame = ttk.LabelFrame(main_frame, text="Записи браузеров", padding="5")
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создание Treeview с возможностью множественного выбора
        self.tree = ttk.Treeview(table_frame, columns=self.headers, show='headings', height=15, selectmode='extended')

        # Настройка заголовков
        column_widths = [80, 150, 150, 100, 120, 120]
        for i, header in enumerate(self.headers):
            self.tree.heading(header, text=header.replace('_', ' ').title())
            self.tree.column(header, width=column_widths[i], minwidth=50)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Размещение таблицы и scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Привязка событий
        self.tree.bind('<Double-1>', self.on_double_click)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Выберите файл для работы с удалением записей")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Переменные для фильтрации
        self.original_records = []
        self.filtered_records = []

    def select_file(self):
        """Выбор файла для работы"""
        filename = filedialog.askopenfilename(
            title="Выберите файл CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            self.filename = filename
            self.file_var.set(os.path.basename(filename))
            self.status_var.set("Файл выбран. Нажмите 'Загрузить данные'")

    def load_data(self):
        """Загрузка данных из файла"""
        if not self.filename:
            messagebox.showwarning("Предупреждение", "Сначала выберите файл")
            return

        try:
            self.records = []
            self.original_records = []

            with open(self.filename, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.records.append(row)
                    self.original_records.append(row.copy())

            self.filtered_records = self.records.copy()
            self.update_developer_filter()
            self.refresh_table()
            self.status_var.set(f"Загружено {len(self.records)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")

    def update_developer_filter(self):
        """Обновление списка разработчиков для фильтра"""
        developers = sorted(set(record.get('developer', '') for record in self.original_records))
        developers.insert(0, "Все разработчики")
        self.developer_combo['values'] = developers
        self.developer_combo.set("Все разработчики")

    def on_search_change(self, *args):
        """Обработка изменения поискового запроса"""
        self.apply_filters()

    def on_filter_change(self, *args):
        """Обработка изменения фильтра"""
        self.apply_filters()

    def apply_filters(self):
        """Применение фильтров к данным"""
        search_text = self.search_var.get().lower()
        selected_developer = self.developer_var.get()

        self.filtered_records = []

        for record in self.records:
            # Фильтр по поиску
            if search_text and search_text not in record.get('browser_name', '').lower():
                continue

            # Фильтр по разработчику
            if (selected_developer and selected_developer != "Все разработчики" and
                    record.get('developer', '') != selected_developer):
                continue

            self.filtered_records.append(record)

        self.refresh_table()
        self.status_var.set(f"Показано {len(self.filtered_records)} из {len(self.records)} записей")

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.search_var.set("")
        self.developer_combo.set("Все разработчики")
        self.filtered_records = self.records.copy()
        self.refresh_table()
        self.status_var.set(f"Показано {len(self.records)} записей")

    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение таблицы отфильтрованными данными
        for i, record in enumerate(self.filtered_records):
            values = [record.get(header, "") for header in self.headers]
            # Используем исходный индекс записи как iid для корректного удаления
            original_index = self.records.index(record)
            self.tree.insert("", tk.END, iid=original_index, values=values)

    def on_double_click(self, event):
        """Обработка двойного клика по записи"""
        selection = self.tree.selection()
        if selection:
            item_id = selection[0]
            record_index = int(item_id)
            record = self.records[record_index]

            # Показываем информацию о записи
            info = "\n".join([f"{header.replace('_', ' ').title()}: {record.get(header, '')}"
                              for header in self.headers])
            messagebox.showinfo("Информация о записи", info)

    def delete_selected(self):
        """Удаление выбранных записей"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите записи для удаления")
            return

        # Подтверждение удаления
        count = len(selection)
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить {count} выбранных записей?"):
            return

        try:
            # Получаем индексы для удаления (сортируем в обратном порядке)
            indices_to_delete = sorted([int(item_id) for item_id in selection], reverse=True)

            # Удаляем записи
            for index in indices_to_delete:
                del self.records[index]

            # Обновляем отфильтрованные записи
            self.apply_filters()

            self.status_var.set(f"Удалено {count} записей. Осталось {len(self.records)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления записей: {str(e)}")

    def delete_all(self):
        """Удаление всех записей"""
        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет записей для удаления")
            return

        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить ВСЕ {len(self.records)} записей?\n\n" +
                                   "Это действие необратимо!"):
            return

        try:
            self.records.clear()
            self.filtered_records.clear()
            self.refresh_table()
            self.status_var.set("Все записи удалены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления всех записей: {str(e)}")

    def save_data(self):
        """Сохранение данных в файл"""
        if not self.filename:
            messagebox.showwarning("Предупреждение", "Файл не выбран")
            return

        try:
            with open(self.filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(self.records)

            messagebox.showinfo("Успех", "Изменения успешно сохранены")
            self.status_var.set("Данные сохранены в файл")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")


if __name__ == "__main__":
    # Тестирование модуля
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    deleter = RecordDeleter(root)
    deleter.show()

    root.mainloop()