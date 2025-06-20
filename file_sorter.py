"""
Модуль для упорядочения записей в файле CSV с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime


class FileSorter:
    """Класс для упорядочения записей в файле"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.filename = ""
        self.records = []
        self.original_records = []
        self.headers = ["browser_id", "browser_name", "developer", "release_date", "latest_version", "engine"]

    def show(self):
        """Показ окна упорядочения записей"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Упорядочение записей")
        self.window.geometry("1000x700")
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

        # Фрейм для управления
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(control_frame, text="Загрузить данные", command=self.load_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(control_frame, text="Восстановить исходный порядок", command=self.restore_original).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=(0,
                                                                                                                  10))
        ttk.Button(control_frame, text="Сохранить изменения", command=self.save_data).grid(row=0, column=2,
                                                                                           padx=(0, 10))

        # Фрейм для сортировки
        sort_frame = ttk.LabelFrame(main_frame, text="Параметры сортировки", padding="10")
        sort_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Первый уровень сортировки
        ttk.Label(sort_frame, text="Основное поле для сортировки:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.sort_field1 = ttk.Combobox(sort_frame, width=20, state="readonly")
        self.sort_field1['values'] = [
            "browser_id - ID браузера",
            "browser_name - Название браузера",
            "developer - Разработчик",
            "release_date - Дата выпуска",
            "latest_version - Последняя версия",
            "engine - Движок"
        ]
        self.sort_field1.grid(row=0, column=1, padx=(0, 10))
        self.sort_field1.set("browser_name - Название браузера")

        self.sort_order1 = tk.StringVar(value="asc")
        ttk.Radiobutton(sort_frame, text="По возрастанию", variable=self.sort_order1, value="asc").grid(row=0, column=2,
                                                                                                        padx=(0, 10))
        ttk.Radiobutton(sort_frame, text="По убыванию", variable=self.sort_order1, value="desc").grid(row=0, column=3)

        # Второй уровень сортировки
        ttk.Label(sort_frame, text="Дополнительное поле:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10),
                                                                pady=(10, 0))
        self.sort_field2 = ttk.Combobox(sort_frame, width=20, state="readonly")
        self.sort_field2['values'] = ["Не использовать"] + list(self.sort_field1['values'])
        self.sort_field2.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        self.sort_field2.set("Не использовать")

        self.sort_order2 = tk.StringVar(value="asc")
        ttk.Radiobutton(sort_frame, text="По возрастанию", variable=self.sort_order2, value="asc").grid(row=1, column=2,
                                                                                                        padx=(0, 10),
                                                                                                        pady=(10, 0))
        ttk.Radiobutton(sort_frame, text="По убыванию", variable=self.sort_order2, value="desc").grid(row=1, column=3,
                                                                                                      pady=(10, 0))

        # Кнопки сортировки
        button_frame = ttk.Frame(sort_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))

        ttk.Button(button_frame, text="Применить сортировку", command=self.apply_sort).grid(row=0, column=0,
                                                                                            padx=(0, 10))
        ttk.Button(button_frame, text="Быстрая сортировка по названию", command=self.quick_sort_name).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=(0, 10))
        ttk.Button(button_frame, text="Сортировка по дате выпуска", command=self.quick_sort_date).grid(row=0, column=2,
                                                                                                       padx=(0, 10))
        ttk.Button(button_frame, text="Сортировка по разработчику", command=self.quick_sort_developer).grid(row=0,
                                                                                                            column=3)

        # Таблица для отображения записей
        table_frame = ttk.LabelFrame(main_frame, text="Записи браузеров", padding="5")
        table_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создание Treeview
        self.tree = ttk.Treeview(table_frame, columns=self.headers, show='headings', height=15)

        # Настройка заголовков с возможностью сортировки по клику
        column_widths = [80, 150, 150, 100, 120, 120]
        for i, header in enumerate(self.headers):
            display_name = header.replace('_', ' ').title()
            self.tree.heading(header, text=display_name, command=lambda h=header: self.sort_by_column(h))
            self.tree.column(header, width=column_widths[i], minwidth=50)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Размещение таблицы и scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Выберите файл для упорядочения записей")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # Переменная для отслеживания направления сортировки столбцов
        self.column_sort_order = {}

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

            self.refresh_table()
            self.status_var.set(f"Загружено {len(self.records)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")

    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение таблицы
        for i, record in enumerate(self.records):
            values = [record.get(header, "") for header in self.headers]
            self.tree.insert("", tk.END, iid=i, values=values)

    def get_sort_key(self, record, field):
        """Получение ключа для сортировки"""
        value = record.get(field, "")

        # Специальная обработка для даты
        if field == "release_date":
            try:
                # Попытка преобразовать в дату
                return datetime.strptime(value, "%Y")
            except:
                try:
                    return datetime.strptime(value, "%Y-%m-%d")
                except:
                    return datetime.min

        # Специальная обработка для версий
        elif field == "latest_version":
            try:
                # Разбиваем версию на части и конвертируем в числа
                parts = value.split('.')
                return tuple(int(part) if part.isdigit() else 0 for part in parts)
            except:
                return (0,)

        # Специальная обработка для ID
        elif field == "browser_id":
            try:
                return int(value)
            except:
                return 0

        # Для остальных полей - строковая сортировка
        return value.lower()

    def apply_sort(self):
        """Применение сортировки"""
        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет данных для сортировки")
            return

        try:
            # Получаем поля для сортировки
            field1_text = self.sort_field1.get()
            field1 = field1_text.split(' - ')[0] if ' - ' in field1_text else field1_text

            field2_text = self.sort_field2.get()
            field2 = None
            if field2_text != "Не использовать":
                field2 = field2_text.split(' - ')[0] if ' - ' in field2_text else field2_text

            # Применяем сортировку
            if field2:
                # Двухуровневая сортировка
                self.records.sort(
                    key=lambda x: (
                        self.get_sort_key(x, field1),
                        self.get_sort_key(x, field2)
                    ),
                    reverse=(self.sort_order1.get() == "desc")
                )
            else:
                # Одноуровневая сортировка
                self.records.sort(
                    key=lambda x: self.get_sort_key(x, field1),
                    reverse=(self.sort_order1.get() == "desc")
                )

            self.refresh_table()

            sort_desc = f"по полю '{field1}'"
            if field2:
                sort_desc += f" и '{field2}'"
            sort_desc += f" ({self.sort_order1.get()})"

            self.status_var.set(f"Данные отсортированы {sort_desc}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки: {str(e)}")

    def sort_by_column(self, column):
        """Сортировка по клику на заголовок столбца"""
        if not self.records:
            return

        # Определяем направление сортировки
        if column in self.column_sort_order:
            self.column_sort_order[column] = not self.column_sort_order[column]
        else:
            self.column_sort_order[column] = False  # False = по возрастанию

        reverse = self.column_sort_order[column]

        try:
            self.records.sort(
                key=lambda x: self.get_sort_key(x, column),
                reverse=reverse
            )

            self.refresh_table()

            order_text = "убыванию" if reverse else "возрастанию"
            self.status_var.set(f"Данные отсортированы по '{column}' по {order_text}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки по столбцу: {str(e)}")

    def quick_sort_name(self):
        """Быстрая сортировка по названию браузера"""
        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет данных для сортировки")
            return

        try:
            self.records.sort(key=lambda x: x.get('browser_name', '').lower())
            self.refresh_table()
            self.status_var.set("Данные отсортированы по названию браузера (А-Я)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки: {str(e)}")

    def quick_sort_date(self):
        """Быстрая сортировка по дате выпуска"""
        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет данных для сортировки")
            return

        try:
            self.records.sort(key=lambda x: self.get_sort_key(x, 'release_date'))
            self.refresh_table()
            self.status_var.set("Данные отсортированы по дате выпуска (старые → новые)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки: {str(e)}")

    def quick_sort_developer(self):
        """Быстрая сортировка по разработчику"""
        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет данных для сортировки")
            return

        try:
            self.records.sort(key=lambda x: x.get('developer', '').lower())
            self.refresh_table()
            self.status_var.set("Данные отсортированы по разработчику (А-Я)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки: {str(e)}")

    def restore_original(self):
        """Восстановление исходного порядка записей"""
        if not self.original_records:
            messagebox.showwarning("Предупреждение", "Нет исходных данных")
            return

        self.records = [record.copy() for record in self.original_records]
        self.refresh_table()
        self.status_var.set("Восстановлен исходный порядок записей")

    def save_data(self):
        """Сохранение данных в файл"""
        if not self.filename:
            messagebox.showwarning("Предупреждение", "Файл не выбран")
            return

        if not self.records:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return

        try:
            with open(self.filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writeheader()
                writer.writerows(self.records)

            messagebox.showinfo("Успех", "Данные успешно сохранены")
            self.status_var.set("Отсортированные данные сохранены в файл")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")


if __name__ == "__main__":
    # Тестирование модуля
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    sorter = FileSorter(root)
    sorter.show()

    root.mainloop()