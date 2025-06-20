"""
Модуль для добавления записей в существующий CSV файл с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime


class RecordAdder:
    """Класс для добавления записей в CSV файл с данными о браузерах"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.entries = {}
        self.data = []
        self.current_file = None
        self.new_records = []

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
        """Показать окно добавления записей"""
        if self.window is not None:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавление записей в файл")
        self.window.geometry("800x700")
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
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Добавление записей в файл данных",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Панель выбора файла
        file_frame = ttk.LabelFrame(main_frame, text="Выбор файла", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Button(
            file_frame,
            text="Выбрать файл",
            command=self.select_file
        ).grid(row=0, column=0, padx=(0, 10))

        self.file_label = ttk.Label(
            file_frame,
            text="Файл не выбран",
            foreground="gray"
        )
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Показать количество существующих записей
        self.records_count_label = ttk.Label(
            file_frame,
            text="",
            font=("Arial", 9)
        )
        self.records_count_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # Панель ввода новой записи
        input_frame = ttk.LabelFrame(main_frame, text="Добавление новой записи", padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        input_frame.columnconfigure(1, weight=1)

        # Поля ввода данных
        row = 0
        for field_name, field_label in self.fields.items():
            ttk.Label(input_frame, text=f"{field_label}:").grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )

            if field_name == 'browser_id':
                # Для ID добавляем кнопку автогенерации
                id_frame = ttk.Frame(input_frame)
                id_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                id_frame.columnconfigure(0, weight=1)

                entry = ttk.Entry(id_frame, width=30)
                entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

                ttk.Button(
                    id_frame,
                    text="Авто ID",
                    command=self.generate_id,
                    width=10
                ).grid(row=0, column=1)

                self.entries[field_name] = entry
            elif field_name == 'developer':
                # Для разработчика добавляем combobox с популярными вариантами
                combo = ttk.Combobox(input_frame, width=37)
                combo['values'] = (
                    'Google LLC',
                    'Mozilla Foundation',
                    'Microsoft',
                    'Apple',
                    'Opera Software',
                    'Yandex',
                    'Brave Software',
                    'Vivaldi Technologies'
                )
                combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.entries[field_name] = combo
            elif field_name == 'engine':
                # Для движка добавляем combobox с популярными движками
                combo = ttk.Combobox(input_frame, width=37)
                combo['values'] = (
                    'Blink',
                    'Gecko',
                    'WebKit',
                    'Trident',
                    'EdgeHTML',
                    'Presto'
                )
                combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.entries[field_name] = combo
            else:
                entry = ttk.Entry(input_frame, width=40)
                entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
                self.entries[field_name] = entry

            row += 1

        # Кнопки управления записью
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=15)

        ttk.Button(
            button_frame,
            text="Добавить запись",
            command=self.add_record
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Очистить поля",
            command=self.clear_fields
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Заполнить пример",
            command=self.fill_example
        ).grid(row=0, column=2, padx=5)

        # Список новых записей
        list_frame = ttk.LabelFrame(main_frame, text="Новые записи для добавления", padding="10")
        list_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Создаем Treeview для отображения новых записей
        self.tree = ttk.Treeview(
            list_frame,
            columns=list(self.fields.keys()),
            show="headings",
            height=10
        )

        # Настраиваем заголовки столбцов
        for field_name, field_label in self.fields.items():
            self.tree.heading(field_name, text=field_label)
            if field_name == 'browser_id':
                self.tree.column(field_name, width=80, minwidth=60)
            elif field_name == 'browser_name':
                self.tree.column(field_name, width=150, minwidth=120)
            elif field_name == 'developer':
                self.tree.column(field_name, width=140, minwidth=120)
            elif field_name == 'release_date':
                self.tree.column(field_name, width=90, minwidth=80)
            elif field_name == 'latest_version':
                self.tree.column(field_name, width=120, minwidth=100)
            elif field_name == 'engine':
                self.tree.column(field_name, width=90, minwidth=80)

        # Скроллбары для списка
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Кнопки управления списком новых записей
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(
            list_buttons_frame,
            text="Удалить выбранную",
            command=self.delete_selected
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            list_buttons_frame,
            text="Редактировать",
            command=self.edit_selected
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            list_buttons_frame,
            text="Очистить все",
            command=self.clear_new_records
        ).grid(row=0, column=2, padx=5)

        # Панель сохранения
        save_frame = ttk.LabelFrame(main_frame, text="Сохранение изменений", padding="10")
        save_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)

        # Статистика
        self.stats_label = ttk.Label(
            save_frame,
            text="Новых записей: 0",
            font=("Arial", 10)
        )
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

        # Кнопки сохранения
        save_buttons_frame = ttk.Frame(save_frame)
        save_buttons_frame.grid(row=1, column=0, pady=10)

        ttk.Button(
            save_buttons_frame,
            text="Сохранить в файл",
            command=self.save_to_file
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            save_buttons_frame,
            text="Предварительный просмотр",
            command=self.preview_changes
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            save_buttons_frame,
            text="Закрыть",
            command=self.close_window
        ).grid(row=0, column=2, padx=5)

        # Привязываем события
        self.tree.bind('<Double-1>', self.edit_selected)

    def select_file(self):
        """Выбрать файл для добавления записей"""
        filename = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            self.load_existing_file(filename)

    def load_existing_file(self, filename):
        """Загрузить существующий файл"""
        try:
            self.data.clear()

            # Читаем существующий файл
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Проверяем наличие необходимых полей
                if not all(field in reader.fieldnames for field in self.fields.keys()):
                    missing_fields = [field for field in self.fields.keys()
                                      if field not in reader.fieldnames]
                    messagebox.showerror(
                        "Ошибка",
                        f"В файле отсутствуют обязательные поля:\n{', '.join(missing_fields)}"
                    )
                    return

                # Читаем данные
                for row in reader:
                    record = {field: row.get(field, '').strip() for field in self.fields.keys()}
                    self.data.append(record)

            # Обновляем информацию о файле
            self.current_file = filename
            self.file_label.config(
                text=f"Файл: {os.path.basename(filename)}",
                foreground="black"
            )

            self.records_count_label.config(
                text=f"Существующих записей в файле: {len(self.data)}"
            )

            messagebox.showinfo(
                "Файл загружен",
                f"Файл успешно загружен!\n"
                f"Существующих записей: {len(self.data)}"
            )

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Ошибка при загрузке файла:\n{str(e)}"
            )

    def generate_id(self):
        """Автоматическая генерация ID"""
        if not self.current_file:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала выберите файл для получения информации о существующих ID!"
            )
            return

        # Находим максимальный существующий ID
        existing_ids = []

        # ID из загруженного файла
        for record in self.data:
            try:
                existing_ids.append(int(record.get('browser_id', 0)))
            except ValueError:
                continue

        # ID из новых записей
        for record in self.new_records:
            try:
                existing_ids.append(int(record.get('browser_id', 0)))
            except ValueError:
                continue

        # Генерируем новый ID
        new_id = max(existing_ids, default=0) + 1

        self.entries['browser_id'].delete(0, tk.END)
        self.entries['browser_id'].insert(0, str(new_id))

    def fill_example(self):
        """Заполнить поля примером данных"""
        examples = [
            {
                'browser_name': 'Brave Browser',
                'developer': 'Brave Software',
                'release_date': '2019',
                'latest_version': '1.60.125',
                'engine': 'Blink'
            },
            {
                'browser_name': 'Vivaldi',
                'developer': 'Vivaldi Technologies',
                'release_date': '2016',
                'latest_version': '6.4.3160.47',
                'engine': 'Blink'
            },
            {
                'browser_name': 'Yandex Browser',
                'developer': 'Yandex',
                'release_date': '2012',
                'latest_version': '23.11.1.806',
                'engine': 'Blink'
            }
        ]

        import random
        example = random.choice(examples)

        # Очищаем поля
        self.clear_fields()

        # Заполняем пример
        for field_name, value in example.items():
            if field_name in self.entries:
                if hasattr(self.entries[field_name], 'set'):
                    self.entries[field_name].set(value)
                else:
                    self.entries[field_name].insert(0, value)

        # Генерируем ID если файл выбран
        if self.current_file:
            self.generate_id()

    def add_record(self):
        """Добавить новую запись в список"""
        if not self.current_file:
            messagebox.showwarning(
                "Предупреждение",
                "Сначала выберите файл для добавления записей!"
            )
            return

        # Собираем данные из полей
        record = {}
        for field_name, widget in self.entries.items():
            if hasattr(widget, 'get'):
                value = widget.get().strip()
            else:
                value = widget.get().strip() if hasattr(widget, 'get') else ''

            if not value:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Поле '{self.fields[field_name]}' не может быть пустым!"
                )
                widget.focus()
                return

            record[field_name] = value

        # Проверяем уникальность ID
        browser_id = record['browser_id']

        # Проверяем в существующих записях
        for existing_record in self.data:
            if existing_record['browser_id'] == browser_id:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Браузер с ID '{browser_id}' уже существует в файле!"
                )
                self.entries['browser_id'].focus()
                return

        # Проверяем в новых записях
        for new_record in self.new_records:
            if new_record['browser_id'] == browser_id:
                messagebox.showwarning(
                    "Предупреждение",
                    f"Браузер с ID '{browser_id}' уже добавлен в список новых записей!"
                )
                self.entries['browser_id'].focus()
                return

        # Добавляем запись
        self.new_records.append(record)
        self.tree.insert('', tk.END, values=list(record.values()))

        # Обновляем статистику
        self.update_stats()

        # Очищаем поля
        self.clear_fields()

        messagebox.showinfo("Успех", "Запись добавлена в список!")

    def clear_fields(self):
        """Очистить поля ввода"""
        for widget in self.entries.values():
            if hasattr(widget, 'delete'):
                widget.delete(0, tk.END)
            elif hasattr(widget, 'set'):
                widget.set('')

    def delete_selected(self):
        """Удалить выбранную запись из списка новых записей"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись из списка?"):
            # Получаем индекс записи
            item_index = self.tree.index(selected_item[0])

            # Удаляем из списка новых записей и из дерева
            del self.new_records[item_index]
            self.tree.delete(selected_item[0])

            self.update_stats()
            messagebox.showinfo("Успех", "Запись удалена из списка!")

    def edit_selected(self, event=None):
        """Редактировать выбранную запись"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования!")
            return

        item_index = self.tree.index(selected_item[0])
        record = self.new_records[item_index]

        # Заполняем поля данными записи
        self.clear_fields()
        for field_name, value in record.items():
            if field_name in self.entries:
                widget = self.entries[field_name]
                if hasattr(widget, 'set'):
                    widget.set(value)
                else:
                    widget.insert(0, value)

        # Удаляем запись из списка (будет добавлена заново при нажатии "Добавить")
        del self.new_records[item_index]
        self.tree.delete(selected_item[0])
        self.update_stats()

    def clear_new_records(self):
        """Очистить список новых записей"""
        if not self.new_records:
            messagebox.showinfo("Информация", "Список новых записей уже пуст!")
            return

        if messagebox.askyesno("Подтверждение", "Очистить весь список новых записей?"):
            self.new_records.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.update_stats()
            messagebox.showinfo("Успех", "Список новых записей очищен!")

    def update_stats(self):
        """Обновить статистику"""
        self.stats_label.config(text=f"Новых записей: {len(self.new_records)}")

    def preview_changes(self):
        """Предварительный просмотр изменений"""
        if not self.new_records:
            messagebox.showwarning("Предупреждение", "Нет новых записей для просмотра!")
            return

        # Создаем окно предварительного просмотра
        preview_window = tk.Toplevel(self.window)
        preview_window.title("Предварительный просмотр добавляемых записей")
        preview_window.geometry("800x500")

        frame = ttk.Frame(preview_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        preview_window.columnconfigure(0, weight=1)
        preview_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Информация
        info_label = ttk.Label(
            frame,
            text=f"Будет добавлено записей: {len(self.new_records)}",
            font=("Arial", 12, "bold")
        )
        info_label.grid(row=0, column=0, pady=(0, 10))

        # Таблица с записями
        preview_tree = ttk.Treeview(
            frame,
            columns=list(self.fields.keys()),
            show="headings",
            height=15
        )

        for field_name, field_label in self.fields.items():
            preview_tree.heading(field_name, text=field_label)
            preview_tree.column(field_name, width=120)

        # Заполняем данными
        for record in self.new_records:
            preview_tree.insert('', tk.END, values=list(record.values()))

        # Скроллбары
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=preview_tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=preview_tree.xview)
        preview_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        preview_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=2, column=0, sticky=(tk.W, tk.E))

        # Кнопка закрытия
        ttk.Button(
            frame,
            text="Закрыть",
            command=preview_window.destroy
        ).grid(row=3, column=0, pady=10)

    def save_to_file(self):
        """Сохранить новые записи в файл"""
        if not self.current_file:
            messagebox.showwarning("Предупреждение", "Файл не выбран!")
            return

        if not self.new_records:
            messagebox.showwarning("Предупреждение", "Нет новых записей для сохранения!")
            return

        if messagebox.askyesno(
                "Подтверждение",
                f"Добавить {len(self.new_records)} новых записей в файл?\n"
                f"Файл: {os.path.basename(self.current_file)}"
        ):
            try:
                # Читаем существующие данные
                all_data = self.data.copy()

                # Добавляем новые записи
                all_data.extend(self.new_records)

                # Сохраняем в файл
                with open(self.current_file, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = list(self.fields.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for record in all_data:
                        writer.writerow(record)

                # Создаем резервную копию с информацией о добавлении
                backup_name = f"{self.current_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_name, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = list(self.fields.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for record in self.data:
                        writer.writerow(record)

                messagebox.showinfo(
                    "Успех",
                    f"Записи успешно добавлены в файл!\n"
                    f"Добавлено записей: {len(self.new_records)}\n"
                    f"Общее количество записей: {len(all_data)}\n"
                    f"Создана резервная копия: {os.path.basename(backup_name)}"
                )

                # Обновляем данные и очищаем список новых записей
                self.data = all_data
                self.new_records.clear()
                for item in self.tree.get_children():
                    self.tree.delete(item)

                self.update_stats()
                self.records_count_label.config(
                    text=f"Существующих записей в файле: {len(self.data)}"
                )

            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при сохранении файла:\n{str(e)}"
                )

    def close_window(self):
        """Закрыть окно"""
        if self.new_records:
            if messagebox.askyesno(
                    "Подтверждение",
                    "У вас есть несохранённые новые записи.\n"
                    "Закрыть окно без сохранения?"
            ):
                pass
            else:
                return

        if self.window:
            self.window.destroy()
            self.window = None