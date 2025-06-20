"""
Модуль для печати (просмотра) CSV файла с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime


class FilePrinter:
    """Класс для печати/просмотра CSV файла с данными о браузерах"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.data = []
        self.current_file = None

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
        """Показать окно печати файла"""
        if self.window is not None:
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Печать исходного файла")
        self.window.geometry("900x600")
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
        main_frame.rowconfigure(2, weight=1)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Просмотр исходного файла данных",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Панель управления файлами
        control_frame = ttk.LabelFrame(main_frame, text="Управление файлом", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # Кнопка открытия файла
        ttk.Button(
            control_frame,
            text="Открыть файл",
            command=self.open_file
        ).grid(row=0, column=0, padx=5)

        # Поле с именем текущего файла
        self.file_label = ttk.Label(control_frame, text="Файл не выбран", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)

        # Кнопки управления
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.grid(row=0, column=2)

        ttk.Button(
            buttons_frame,
            text="Обновить",
            command=self.refresh_data
        ).grid(row=0, column=0, padx=2)

        ttk.Button(
            buttons_frame,
            text="Экспорт в текст",
            command=self.export_to_text
        ).grid(row=0, column=1, padx=2)

        ttk.Button(
            buttons_frame,
            text="Печать",
            command=self.print_data
        ).grid(row=0, column=2, padx=2)

        # Область отображения данных
        data_frame = ttk.LabelFrame(main_frame, text="Данные файла", padding="10")
        data_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)

        # Создаем Treeview для отображения данных
        self.tree = ttk.Treeview(
            data_frame,
            columns=list(self.fields.keys()),
            show="headings",
            height=15
        )

        # Настраиваем заголовки столбцов
        for field_name, field_label in self.fields.items():
            self.tree.heading(field_name, text=field_label)
            # Устанавливаем ширину столбцов в зависимости от содержимого
            if field_name == 'browser_id':
                self.tree.column(field_name, width=80, minwidth=60)
            elif field_name == 'browser_name':
                self.tree.column(field_name, width=150, minwidth=120)
            elif field_name == 'developer':
                self.tree.column(field_name, width=150, minwidth=120)
            elif field_name == 'release_date':
                self.tree.column(field_name, width=100, minwidth=80)
            elif field_name == 'latest_version':
                self.tree.column(field_name, width=120, minwidth=100)
            elif field_name == 'engine':
                self.tree.column(field_name, width=100, minwidth=80)

        # Скроллбары для таблицы
        v_scrollbar = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Информационная панель
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        info_frame.columnconfigure(0, weight=1)

        # Статистика
        self.stats_label = ttk.Label(
            info_frame,
            text="Статистика: записей не загружено",
            font=("Arial", 10)
        )
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

        # Кнопка закрытия
        ttk.Button(
            info_frame,
            text="Закрыть",
            command=self.close_window
        ).grid(row=0, column=1, padx=5)

        # Привязываем события
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)

    def open_file(self):
        """Открыть CSV файл"""
        filename = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Загрузить данные из файла"""
        try:
            self.data.clear()

            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Читаем CSV файл
            with open(filename, 'r', encoding='utf-8') as csvfile:
                # Пытаемся автоматически определить разделитель
                sample = csvfile.read(1024)
                csvfile.seek(0)

                # Создаем reader
                reader = csv.DictReader(csvfile)

                # Читаем данные
                for row_num, row in enumerate(reader, 1):
                    # Проверяем наличие необходимых полей
                    if not all(field in row for field in self.fields.keys()):
                        missing_fields = [field for field in self.fields.keys() if field not in row]
                        messagebox.showerror(
                            "Ошибка",
                            f"В файле отсутствуют обязательные поля:\n{', '.join(missing_fields)}\n\n"
                            f"Ожидаемые поля: {', '.join(self.fields.keys())}"
                        )
                        return

                    # Добавляем запись в данные
                    record = {field: row.get(field, '').strip() for field in self.fields.keys()}
                    self.data.append(record)

                    # Добавляем в таблицу
                    self.tree.insert('', tk.END, values=list(record.values()))

            # Обновляем информацию о файле
            self.current_file = filename
            self.file_label.config(
                text=f"Файл: {os.path.basename(filename)}",
                foreground="black"
            )

            # Обновляем статистику
            self.update_statistics()

            messagebox.showinfo(
                "Успех",
                f"Файл успешно загружен!\n"
                f"Записей: {len(self.data)}"
            )

        except UnicodeDecodeError:
            messagebox.showerror(
                "Ошибка",
                "Ошибка кодировки файла. Попробуйте сохранить файл в UTF-8."
            )
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Ошибка при загрузке файла:\n{str(e)}"
            )

    def refresh_data(self):
        """Обновить данные из файла"""
        if self.current_file and os.path.exists(self.current_file):
            self.load_file(self.current_file)
        else:
            messagebox.showwarning(
                "Предупреждение",
                "Файл не выбран или не существует!"
            )

    def update_statistics(self):
        """Обновить статистику"""
        if not self.data:
            self.stats_label.config(text="Статистика: записей не загружено")
            return

        total_records = len(self.data)

        # Подсчитываем статистику по разработчикам
        developers = {}
        engines = {}

        for record in self.data:
            dev = record.get('developer', 'Неизвестно')
            eng = record.get('engine', 'Неизвестно')

            developers[dev] = developers.get(dev, 0) + 1
            engines[eng] = engines.get(eng, 0) + 1

        # Находим самого популярного разработчика и движок
        top_developer = max(developers.items(), key=lambda x: x[1]) if developers else ('Неизвестно', 0)
        top_engine = max(engines.items(), key=lambda x: x[1]) if engines else ('Неизвестно', 0)

        stats_text = (
            f"Всего записей: {total_records} | "
            f"Разработчиков: {len(developers)} | "
            f"Движков: {len(engines)} | "
            f"Топ разработчик: {top_developer[0]} ({top_developer[1]}) | "
            f"Топ движок: {top_engine[0]} ({top_engine[1]})"
        )

        self.stats_label.config(text=stats_text)

    def export_to_text(self):
        """Экспорт данных в текстовый файл"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта!")
            return

        filename = filedialog.asksaveasfilename(
            title="Экспорт в текстовый файл",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as txtfile:
                    # Заголовок отчета
                    txtfile.write("=" * 80 + "\n")
                    txtfile.write("ОТЧЕТ О БРАУЗЕРАХ\n")
                    txtfile.write(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
                    if self.current_file:
                        txtfile.write(f"Исходный файл: {os.path.basename(self.current_file)}\n")
                    txtfile.write("=" * 80 + "\n\n")

                    # Данные
                    for i, record in enumerate(self.data, 1):
                        txtfile.write(f"Запись #{i}\n")
                        txtfile.write("-" * 50 + "\n")

                        for field_name, field_label in self.fields.items():
                            value = record.get(field_name, 'Не указано')
                            txtfile.write(f"{field_label}: {value}\n")

                        txtfile.write("\n")

                    # Статистика
                    txtfile.write("=" * 80 + "\n")
                    txtfile.write("СТАТИСТИКА\n")
                    txtfile.write("=" * 80 + "\n")
                    txtfile.write(f"Общее количество записей: {len(self.data)}\n")

                    # Группировка по разработчикам
                    developers = {}
                    for record in self.data:
                        dev = record.get('developer', 'Неизвестно')
                        developers[dev] = developers.get(dev, 0) + 1

                    txtfile.write("\nПо разработчикам:\n")
                    for dev, count in sorted(developers.items()):
                        txtfile.write(f"  {dev}: {count}\n")

                    # Группировка по движкам
                    engines = {}
                    for record in self.data:
                        eng = record.get('engine', 'Неизвестно')
                        engines[eng] = engines.get(eng, 0) + 1

                    txtfile.write("\nПо движкам:\n")
                    for eng, count in sorted(engines.items()):
                        txtfile.write(f"  {eng}: {count}\n")

                messagebox.showinfo(
                    "Успех",
                    f"Данные успешно экспортированы в текстовый файл!\n"
                    f"Файл: {filename}"
                )

            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при экспорте:\n{str(e)}"
                )

    def print_data(self):
        """Имитация печати данных"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Нет данных для печати!")
            return

        # Создаем окно предварительного просмотра
        preview_window = tk.Toplevel(self.window)
        preview_window.title("Предварительный просмотр печати")
        preview_window.geometry("800x600")

        # Создаем текстовое поле для предварительного просмотра
        text_frame = ttk.Frame(preview_window, padding="10")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        preview_window.columnconfigure(0, weight=1)
        preview_window.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Текстовое поле с прокруткой
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar_preview = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_preview.set)

        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_preview.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Формируем содержимое для печати
        content = self.format_print_content()
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

        # Кнопки управления
        buttons_frame = ttk.Frame(preview_window, padding="10")
        buttons_frame.grid(row=1, column=0)

        ttk.Button(
            buttons_frame,
            text="Печать",
            command=lambda: messagebox.showinfo("Печать", "Функция печати будет реализована позднее")
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            buttons_frame,
            text="Закрыть",
            command=preview_window.destroy
        ).grid(row=0, column=1, padx=5)

    def format_print_content(self):
        """Форматирование содержимого для печати"""
        content = []

        # Заголовок
        content.append("=" * 80)
        content.append("ОТЧЕТ О БРАУЗЕРАХ")
        content.append(f"Дата печати: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        if self.current_file:
            content.append(f"Исходный файл: {os.path.basename(self.current_file)}")
        content.append("=" * 80)
        content.append("")

        # Данные в табличном формате
        if self.data:
            # Заголовки таблицы
            headers = ["№", "ID", "Название", "Разработчик", "Год", "Версия", "Движок"]
            content.append(
                f"{headers[0]:>3} {headers[1]:<4} {headers[2]:<20} {headers[3]:<18} {headers[4]:<6} {headers[5]:<15} {headers[6]:<12}")
            content.append("-" * 80)

            # Данные
            for i, record in enumerate(self.data, 1):
                line = (
                    f"{i:>3} "
                    f"{record.get('browser_id', ''):<4} "
                    f"{record.get('browser_name', '')[:20]:<20} "
                    f"{record.get('developer', '')[:18]:<18} "
                    f"{record.get('release_date', ''):<6} "
                    f"{record.get('latest_version', '')[:15]:<15} "
                    f"{record.get('engine', '')[:12]:<12}"
                )
                content.append(line)

        content.append("")
        content.append("-" * 80)
        content.append(f"Всего записей: {len(self.data)}")

        return "\n".join(content)

    def on_double_click(self, event):
        """Обработчик двойного клика по записи"""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']

            # Создаем окно с подробной информацией
            detail_window = tk.Toplevel(self.window)
            detail_window.title("Подробная информация")
            detail_window.geometry("400x300")
            detail_window.resizable(False, False)

            frame = ttk.Frame(detail_window, padding="20")
            frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Отображаем информацию
            row = 0
            for i, (field_name, field_label) in enumerate(self.fields.items()):
                value = item_values[i] if i < len(item_values) else "Не указано"

                ttk.Label(frame, text=f"{field_label}:", font=("Arial", 10, "bold")).grid(
                    row=row, column=0, sticky=tk.W, pady=5
                )
                ttk.Label(frame, text=str(value), wraplength=200).grid(
                    row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
                )
                row += 1

            # Кнопка закрытия
            ttk.Button(
                frame,
                text="Закрыть",
                command=detail_window.destroy
            ).grid(row=row, column=0, columnspan=2, pady=20)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Создаем контекстное меню
        context_menu = tk.Menu(self.window, tearoff=0)
        context_menu.add_command(
            label="Подробная информация",
            command=lambda: self.on_double_click(None)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="Копировать строку",
            command=self.copy_selected_row
        )

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def copy_selected_row(self):
        """Копировать выбранную строку в буфер обмена"""
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0])['values']

            # Формируем строку для копирования
            row_text = []
            for i, (field_name, field_label) in enumerate(self.fields.items()):
                value = item_values[i] if i < len(item_values) else ""
                row_text.append(f"{field_label}: {value}")

            clipboard_text = " | ".join(row_text)

            # Копируем в буфер обмена
            self.window.clipboard_clear()
            self.window.clipboard_append(clipboard_text)

            messagebox.showinfo("Успех", "Строка скопирована в буфер обмена!")

    def close_window(self):
        """Закрыть окно"""
        if self.window:
            self.window.destroy()
            self.window = None