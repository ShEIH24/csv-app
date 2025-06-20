"""
Модуль для печати результирующих файлов и отчетов по браузерам
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime
import subprocess
import tempfile
import platform


class ResultPrinter:
    """Класс для печати результатов анализа браузеров"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.data = []
        self.filtered_data = []

    def show(self):
        """Показать окно печати результатов"""
        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title("Печать результатов")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов окна печати"""
        # Главный фрейм
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Печать результатов анализа браузеров",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Фрейм для управления файлами
        file_frame = ttk.LabelFrame(main_frame, text="Управление файлами", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Кнопки управления файлами
        load_btn = ttk.Button(file_frame, text="Загрузить данные",
                              command=self.load_data)
        load_btn.grid(row=0, column=0, padx=(0, 10))

        load_results_btn = ttk.Button(file_frame, text="Загрузить результаты",
                                      command=self.load_results)
        load_results_btn.grid(row=0, column=1, padx=(0, 10))

        # Фрейм для параметров печати
        print_frame = ttk.LabelFrame(main_frame, text="Параметры печати", padding="10")
        print_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        print_frame.columnconfigure(1, weight=1)

        # Тип отчета
        ttk.Label(print_frame, text="Тип отчета:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.report_type = tk.StringVar(value="summary")
        report_combo = ttk.Combobox(print_frame, textvariable=self.report_type,
                                    values=["summary", "detailed", "statistical", "by_developer", "by_engine"])
        report_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # Формат вывода
        ttk.Label(print_frame, text="Формат:").grid(row=0, column=2, sticky=tk.W, padx=(10, 10))
        self.output_format = tk.StringVar(value="text")
        format_combo = ttk.Combobox(print_frame, textvariable=self.output_format,
                                    values=["text", "html", "csv"])
        format_combo.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # Фильтры
        ttk.Label(print_frame, text="Фильтр по разработчику:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.developer_filter = tk.StringVar()
        dev_combo = ttk.Combobox(print_frame, textvariable=self.developer_filter)
        dev_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0), padx=(0, 10))

        ttk.Label(print_frame, text="Фильтр по движку:").grid(row=1, column=2, sticky=tk.W, pady=(10, 0), padx=(10, 10))
        self.engine_filter = tk.StringVar()
        engine_combo = ttk.Combobox(print_frame, textvariable=self.engine_filter)
        engine_combo.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Сохраняем комбобоксы для обновления
        self.dev_combo = dev_combo
        self.engine_combo = engine_combo

        # Кнопки действий
        buttons_frame = ttk.Frame(print_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))

        preview_btn = ttk.Button(buttons_frame, text="Предварительный просмотр",
                                 command=self.preview_report)
        preview_btn.grid(row=0, column=0, padx=(0, 10))

        print_btn = ttk.Button(buttons_frame, text="Печать",
                               command=self.print_report)
        print_btn.grid(row=0, column=1, padx=(0, 10))

        save_btn = ttk.Button(buttons_frame, text="Сохранить в файл",
                              command=self.save_report)
        save_btn.grid(row=0, column=2, padx=(0, 10))

        clear_btn = ttk.Button(buttons_frame, text="Очистить",
                               command=self.clear_preview)
        clear_btn.grid(row=0, column=3)

        # Область предварительного просмотра
        preview_frame = ttk.LabelFrame(main_frame, text="Предварительный просмотр", padding="10")
        preview_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        # Текстовое поле для предварительного просмотра
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, font=("Consolas", 9))
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL,
                                          command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)

        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def load_data(self):
        """Загрузка исходных данных"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл данных",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                self.data = []
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.data.append(row)

                self.update_filters()
                self.status_var.set(f"Загружено {len(self.data)} записей")
                messagebox.showinfo("Успех", f"Данные загружены успешно!\nЗаписей: {len(self.data)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def load_results(self):
        """Загрузка результатов расчетов"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл результатов",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(tk.END, content)

                self.status_var.set("Результаты загружены для печати")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки результатов: {str(e)}")

    def update_filters(self):
        """Обновление списков фильтров"""
        if self.data:
            # Обновляем список разработчиков
            developers = sorted(set(row['developer'] for row in self.data))
            developers.insert(0, "Все")
            self.dev_combo['values'] = developers
            self.developer_filter.set("Все")

            # Обновляем список движков
            engines = sorted(set(row['engine'] for row in self.data))
            engines.insert(0, "Все")
            self.engine_combo['values'] = engines
            self.engine_filter.set("Все")

    def apply_filters(self):
        """Применение фильтров к данным"""
        self.filtered_data = self.data.copy()

        # Фильтр по разработчику
        if self.developer_filter.get() and self.developer_filter.get() != "Все":
            self.filtered_data = [row for row in self.filtered_data
                                  if row['developer'] == self.developer_filter.get()]

        # Фильтр по движку
        if self.engine_filter.get() and self.engine_filter.get() != "Все":
            self.filtered_data = [row for row in self.filtered_data
                                  if row['engine'] == self.engine_filter.get()]

    def preview_report(self):
        """Предварительный просмотр отчета"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
            return

        try:
            self.apply_filters()
            report_content = self.generate_report()

            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, report_content)

            self.status_var.set(f"Сформирован отчет ({len(self.filtered_data)} записей)")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания отчета: {str(e)}")

    def generate_report(self):
        """Генерация отчета в зависимости от выбранного типа"""
        report_type = self.report_type.get()
        output_format = self.output_format.get()

        if report_type == "summary":
            content = self.generate_summary_report()
        elif report_type == "detailed":
            content = self.generate_detailed_report()
        elif report_type == "statistical":
            content = self.generate_statistical_report()
        elif report_type == "by_developer":
            content = self.generate_developer_report()
        elif report_type == "by_engine":
            content = self.generate_engine_report()
        else:
            content = self.generate_summary_report()

        # Форматирование в зависимости от выбранного формата
        if output_format == "html":
            return self.format_as_html(content)
        elif output_format == "csv":
            return self.format_as_csv(content)
        else:
            return content

    def generate_summary_report(self):
        """Генерация краткого отчета"""
        lines = []

        # Заголовок
        lines.append("КРАТКИЙ ОТЧЕТ ПО БРАУЗЕРАМ")
        lines.append("=" * 50)
        lines.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append(f"Всего записей: {len(self.filtered_data)}")
        lines.append("")

        # Фильтры
        if self.developer_filter.get() and self.developer_filter.get() != "Все":
            lines.append(f"Фильтр по разработчику: {self.developer_filter.get()}")
        if self.engine_filter.get() and self.engine_filter.get() != "Все":
            lines.append(f"Фильтр по движку: {self.engine_filter.get()}")
        if any([self.developer_filter.get() != "Все", self.engine_filter.get() != "Все"]):
            lines.append("")

        # Основная информация
        lines.append("ОСНОВНЫЕ ПОКАЗАТЕЛИ:")
        lines.append("-" * 25)

        developers = set(row['developer'] for row in self.filtered_data)
        engines = set(row['engine'] for row in self.filtered_data)
        years = [int(row['release_date']) for row in self.filtered_data]

        lines.append(f"Уникальных разработчиков: {len(developers)}")
        lines.append(f"Уникальных движков: {len(engines)}")
        lines.append(f"Диапазон лет: {min(years)}-{max(years)}")
        lines.append("")

        # Список браузеров
        lines.append("СПИСОК БРАУЗЕРОВ:")
        lines.append("-" * 20)
        for i, row in enumerate(self.filtered_data, 1):
            lines.append(f"{i:2d}. {row['browser_name']} ({row['developer']}, {row['release_date']})")

        return "\n".join(lines)

    def generate_detailed_report(self):
        """Генерация подробного отчета"""
        lines = []

        # Заголовок
        lines.append("ПОДРОБНЫЙ ОТЧЕТ ПО БРАУЗЕРАМ")
        lines.append("=" * 60)
        lines.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append(f"Всего записей: {len(self.filtered_data)}")
        lines.append("")

        # Подробная информация по каждому браузеру
        for i, row in enumerate(self.filtered_data, 1):
            lines.append(f"{i}. {row['browser_name'].upper()}")
            lines.append("-" * (len(row['browser_name']) + 3))
            lines.append(f"   Разработчик: {row['developer']}")
            lines.append(f"   Год выпуска: {row['release_date']}")
            lines.append(f"   Движок: {row['engine']}")
            lines.append(f"   Последняя версия: {row['latest_version']}")
            lines.append("")

        return "\n".join(lines)

    def generate_statistical_report(self):
        """Генерация статистического отчета"""
        lines = []

        # Заголовок
        lines.append("СТАТИСТИЧЕСКИЙ ОТЧЕТ")
        lines.append("=" * 40)
        lines.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append("")

        # Статистика по разработчикам
        dev_stats = {}
        for row in self.filtered_data:
            dev = row['developer']
            if dev not in dev_stats:
                dev_stats[dev] = []
            dev_stats[dev].append(row)

        lines.append("СТАТИСТИКА ПО РАЗРАБОТЧИКАМ:")
        lines.append("-" * 35)
        for dev, browsers in sorted(dev_stats.items()):
            lines.append(f"{dev}: {len(browsers)} браузеров")
            years = [int(b['release_date']) for b in browsers]
            avg_year = sum(years) / len(years)
            lines.append(f"   Средний год выпуска: {avg_year:.1f}")
            lines.append(f"   Диапазон: {min(years)}-{max(years)}")
            lines.append("")

        # Статистика по движкам
        engine_stats = {}
        for row in self.filtered_data:
            engine = row['engine']
            if engine not in engine_stats:
                engine_stats[engine] = []
            engine_stats[engine].append(row)

        lines.append("СТАТИСТИКА ПО ДВИЖКАМ:")
        lines.append("-" * 30)
        for engine, browsers in sorted(engine_stats.items()):
            lines.append(f"{engine}: {len(browsers)} браузеров")
            devs = set(b['developer'] for b in browsers)
            lines.append(f"   Разработчиков: {len(devs)}")
            lines.append("")

        return "\n".join(lines)

    def generate_developer_report(self):
        """Генерация отчета по разработчикам"""
        lines = []

        # Заголовок
        lines.append("ОТЧЕТ ПО РАЗРАБОТЧИКАМ")
        lines.append("=" * 40)
        lines.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append("")

        # Группировка по разработчикам
        dev_groups = {}
        for row in self.filtered_data:
            dev = row['developer']
            if dev not in dev_groups:
                dev_groups[dev] = []
            dev_groups[dev].append(row)

        # Отчет по каждому разработчику
        for dev, browsers in sorted(dev_groups.items()):
            lines.append(f"РАЗРАБОТЧИК: {dev.upper()}")
            lines.append("=" * (len(dev) + 13))
            lines.append(f"Количество браузеров: {len(browsers)}")

            years = [int(b['release_date']) for b in browsers]
            lines.append(f"Период деятельности: {min(years)}-{max(years)}")

            engines = set(b['engine'] for b in browsers)
            lines.append(f"Используемые движки: {', '.join(sorted(engines))}")
            lines.append("")

            lines.append("Браузеры:")
            for browser in sorted(browsers, key=lambda x: x['release_date']):
                lines.append(f"  • {browser['browser_name']} ({browser['release_date']}) - {browser['engine']}")
            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def generate_engine_report(self):
        """Генерация отчета по движкам"""
        lines = []

        # Заголовок
        lines.append("ОТЧЕТ ПО ДВИЖКАМ")
        lines.append("=" * 30)
        lines.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append("")

        # Группировка по движкам
        engine_groups = {}
        for row in self.filtered_data:
            engine = row['engine']
            if engine not in engine_groups:
                engine_groups[engine] = []
            engine_groups[engine].append(row)

        # Отчет по каждому движку
        for engine, browsers in sorted(engine_groups.items()):
            lines.append(f"ДВИЖОК: {engine.upper()}")
            lines.append("=" * (len(engine) + 8))
            lines.append(f"Количество браузеров: {len(browsers)}")

            developers = set(b['developer'] for b in browsers)
            lines.append(f"Разработчики: {', '.join(sorted(developers))}")

            years = [int(b['release_date']) for b in browsers]
            lines.append(f"Период использования: {min(years)}-{max(years)}")
            lines.append("")

            lines.append("Браузеры:")
            for browser in sorted(browsers, key=lambda x: x['release_date']):
                lines.append(f"  • {browser['browser_name']} ({browser['developer']}, {browser['release_date']})")
            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def format_as_html(self, content):
        """Форматирование в HTML"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Отчет по браузерам</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        pre {{ background-color: #f5f5f5; padding: 10px; }}
    </style>
</head>
<body>
    <h1>Отчет по браузерам</h1>
    <pre>{content}</pre>
</body>
</html>
"""
        return html_content

    def format_as_csv(self, content):
        """Форматирование в CSV (только для табличных данных)"""
        if not self.filtered_data:
            return content

        # Создаем CSV из отфильтрованных данных
        csv_lines = []

        # Заголовки
        if self.filtered_data:
            headers = list(self.filtered_data[0].keys())
            csv_lines.append(','.join(headers))

            # Данные
            for row in self.filtered_data:
                values = [str(row[header]) for header in headers]
                csv_lines.append(','.join(values))

        return '\n'.join(csv_lines)

    def print_report(self):
        """Печать отчета"""
        try:
            if not self.preview_text.get(1.0, tk.END).strip():
                messagebox.showwarning("Предупреждение", "Сначала создайте предварительный просмотр!")
                return

            # Создаем временный файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                content = self.preview_text.get(1.0, tk.END)
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Открываем файл для печати в зависимости от ОС
            system = platform.system()
            if system == "Windows":
                # Windows
                os.startfile(temp_file_path, "print")
            elif system == "Darwin":
                # macOS
                subprocess.run(["lpr", temp_file_path])
            else:
                # Linux
                subprocess.run(["lp", temp_file_path])

            self.status_var.set("Отчет отправлен на печать")
            messagebox.showinfo("Успех", "Отчет отправлен на печать!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка печати: {str(e)}")

    def save_report(self):
        """Сохранение отчета в файл"""
        if not self.preview_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Предупреждение", "Сначала создайте отчет!")
            return

        try:
            # Определяем расширение файла по формату
            format_ext = {
                'text': '.txt',
                'html': '.html',
                'csv': '.csv'
            }

            default_ext = format_ext.get(self.output_format.get(), '.txt')

            file_path = filedialog.asksaveasfilename(
                title="Сохранить отчет",
                defaultextension=default_ext,
                filetypes=[
                    ("Text files", "*.txt"),
                    ("HTML files", "*.html"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.preview_text.get(1.0, tk.END))

                self.status_var.set("Отчет сохранен")
                messagebox.showinfo("Успех", "Отчет сохранен успешно!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    def clear_preview(self):
        """Очистка предварительного просмотра"""
        self.preview_text.delete(1.0, tk.END)
        self.status_var.set("Предварительный просмотр очищен")