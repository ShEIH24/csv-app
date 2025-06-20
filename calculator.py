"""
Модуль для расчета производственно-экономических показателей браузеров
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime
from collections import defaultdict
import statistics


class Calculator:
    """Класс для расчета показателей по данным браузеров"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.data = []
        self.results = {}

    def show(self):
        """Показать окно расчета показателей"""
        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.parent)
        self.window.title("Расчет показателей браузеров")
        self.window.geometry("900x700")
        self.window.resizable(True, True)

        # Создаем интерфейс
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов окна расчета"""
        # Главный фрейм
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Расчет показателей браузеров",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Фрейм для кнопок управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Кнопка загрузки файла
        load_btn = ttk.Button(control_frame, text="Загрузить файл CSV",
                              command=self.load_file)
        load_btn.grid(row=0, column=0, padx=(0, 10))

        # Кнопка расчета
        calc_btn = ttk.Button(control_frame, text="Выполнить расчеты",
                              command=self.calculate_metrics)
        calc_btn.grid(row=0, column=1, padx=(0, 10))

        # Кнопка сохранения
        save_btn = ttk.Button(control_frame, text="Сохранить результаты",
                              command=self.save_results)
        save_btn.grid(row=0, column=2, padx=(0, 10))

        # Кнопка очистки
        clear_btn = ttk.Button(control_frame, text="Очистить",
                               command=self.clear_results)
        clear_btn.grid(row=0, column=3)

        # Область для результатов
        results_frame = ttk.LabelFrame(main_frame, text="Результаты расчетов", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Текстовое поле для результатов с прокруткой
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def load_file(self):
        """Загрузка CSV файла"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл CSV",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                self.data = []
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        self.data.append(row)

                self.status_var.set(f"Загружено {len(self.data)} записей из файла")
                messagebox.showinfo("Успех", f"Файл загружен успешно!\nЗагружено записей: {len(self.data)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")
            self.status_var.set("Ошибка загрузки файла")

    def calculate_metrics(self):
        """Расчет всех показателей"""
        if not self.data:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
            return

        try:
            self.results = {}

            # Основные статистические показатели
            self.calculate_basic_stats()

            # Анализ по разработчикам
            self.calculate_developer_stats()

            # Анализ по движкам
            self.calculate_engine_stats()

            # Временной анализ
            self.calculate_time_stats()

            # Анализ версий
            self.calculate_version_stats()

            # Рыночная доля (условная)
            self.calculate_market_share()

            # Отображение результатов
            self.display_results()

            self.status_var.set("Расчеты выполнены успешно")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {str(e)}")
            self.status_var.set("Ошибка расчета")

    def calculate_basic_stats(self):
        """Расчет базовых статистических показателей"""
        self.results['basic'] = {
            'total_browsers': len(self.data),
            'unique_developers': len(set(row['developer'] for row in self.data)),
            'unique_engines': len(set(row['engine'] for row in self.data)),
            'date_range': {
                'min_year': min(int(row['release_date']) for row in self.data),
                'max_year': max(int(row['release_date']) for row in self.data)
            }
        }

    def calculate_developer_stats(self):
        """Анализ по разработчикам"""
        dev_stats = defaultdict(list)

        for row in self.data:
            dev_stats[row['developer']].append({
                'browser': row['browser_name'],
                'year': int(row['release_date']),
                'version': row['latest_version']
            })

        self.results['developers'] = {}
        for dev, browsers in dev_stats.items():
            self.results['developers'][dev] = {
                'browser_count': len(browsers),
                'browsers': [b['browser'] for b in browsers],
                'avg_release_year': statistics.mean([b['year'] for b in browsers]),
                'year_range': max([b['year'] for b in browsers]) - min([b['year'] for b in browsers])
            }

    def calculate_engine_stats(self):
        """Анализ по движкам"""
        engine_stats = defaultdict(list)

        for row in self.data:
            engine_stats[row['engine']].append({
                'browser': row['browser_name'],
                'year': int(row['release_date']),
                'developer': row['developer']
            })

        self.results['engines'] = {}
        for engine, browsers in engine_stats.items():
            self.results['engines'][engine] = {
                'browser_count': len(browsers),
                'browsers': [b['browser'] for b in browsers],
                'developers': list(set(b['developer'] for b in browsers)),
                'avg_release_year': statistics.mean([b['year'] for b in browsers])
            }

    def calculate_time_stats(self):
        """Временной анализ"""
        years = [int(row['release_date']) for row in self.data]
        decade_stats = defaultdict(int)

        for year in years:
            decade = (year // 10) * 10
            decade_stats[decade] += 1

        self.results['time_analysis'] = {
            'by_decade': dict(decade_stats),
            'avg_release_year': statistics.mean(years),
            'std_dev_year': statistics.stdev(years) if len(years) > 1 else 0,
            'oldest_browser': min(self.data, key=lambda x: int(x['release_date'])),
            'newest_browser': max(self.data, key=lambda x: int(x['release_date']))
        }

    def calculate_version_stats(self):
        """Анализ версий"""
        version_info = []

        for row in self.data:
            version = row['latest_version']
            try:
                # Пытаемся извлечь числовую часть версии
                major_version = float(version.split('.')[0])
                version_info.append(major_version)
            except:
                continue

        if version_info:
            self.results['versions'] = {
                'avg_major_version': statistics.mean(version_info),
                'max_major_version': max(version_info),
                'min_major_version': min(version_info),
                'version_range': max(version_info) - min(version_info)
            }

    def calculate_market_share(self):
        """Условный расчет рыночной доли (на основе года выпуска и популярности)"""
        # Условные весовые коэффициенты популярности
        popularity_weights = {
            'Google': 0.65,
            'Mozilla Foundation': 0.15,
            'Microsoft': 0.10,
            'Apple': 0.07,
            'Opera Software': 0.03
        }

        market_share = {}
        total_weight = 0

        for row in self.data:
            developer = row['developer']
            weight = popularity_weights.get(developer, 0.01)  # Малый вес для остальных

            # Учитываем современность браузера
            year = int(row['release_date'])
            if year >= 2000:
                weight *= 1.5  # Бонус за современность

            market_share[row['browser_name']] = weight
            total_weight += weight

        # Нормализация до 100%
        for browser in market_share:
            market_share[browser] = (market_share[browser] / total_weight) * 100

        self.results['market_share'] = market_share

    def display_results(self):
        """Отображение результатов в текстовом поле"""
        self.results_text.delete(1.0, tk.END)

        output = []

        # Заголовок отчета
        output.append("=" * 80)
        output.append("ОТЧЕТ ПО АНАЛИЗУ БРАУЗЕРОВ")
        output.append(f"Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        output.append("=" * 80)
        output.append("")

        # Основные показатели
        if 'basic' in self.results:
            output.append("1. ОСНОВНЫЕ ПОКАЗАТЕЛИ")
            output.append("-" * 30)
            basic = self.results['basic']
            output.append(f"Всего браузеров: {basic['total_browsers']}")
            output.append(f"Уникальных разработчиков: {basic['unique_developers']}")
            output.append(f"Уникальных движков: {basic['unique_engines']}")
            output.append(
                f"Диапазон годов выпуска: {basic['date_range']['min_year']}-{basic['date_range']['max_year']}")
            output.append("")

        # Анализ по разработчикам
        if 'developers' in self.results:
            output.append("2. АНАЛИЗ ПО РАЗРАБОТЧИКАМ")
            output.append("-" * 30)
            for dev, stats in self.results['developers'].items():
                output.append(f"Разработчик: {dev}")
                output.append(f"  Количество браузеров: {stats['browser_count']}")
                output.append(f"  Браузеры: {', '.join(stats['browsers'])}")
                output.append(f"  Средний год выпуска: {stats['avg_release_year']:.1f}")
                output.append(f"  Диапазон лет: {stats['year_range']} лет")
                output.append("")

        # Анализ по движкам
        if 'engines' in self.results:
            output.append("3. АНАЛИЗ ПО ДВИЖКАМ")
            output.append("-" * 30)
            for engine, stats in self.results['engines'].items():
                output.append(f"Движок: {engine}")
                output.append(f"  Количество браузеров: {stats['browser_count']}")
                output.append(f"  Браузеры: {', '.join(stats['browsers'])}")
                output.append(f"  Разработчики: {', '.join(stats['developers'])}")
                output.append(f"  Средний год выпуска: {stats['avg_release_year']:.1f}")
                output.append("")

        # Временной анализ
        if 'time_analysis' in self.results:
            output.append("4. ВРЕМЕННОЙ АНАЛИЗ")
            output.append("-" * 30)
            time_stats = self.results['time_analysis']
            output.append(f"Средний год выпуска: {time_stats['avg_release_year']:.1f}")
            output.append(f"Стандартное отклонение: {time_stats['std_dev_year']:.1f}")
            output.append("")
            output.append("Распределение по десятилетиям:")
            for decade, count in sorted(time_stats['by_decade'].items()):
                output.append(f"  {decade}е годы: {count} браузеров")
            output.append("")
            output.append(
                f"Самый старый браузер: {time_stats['oldest_browser']['browser_name']} ({time_stats['oldest_browser']['release_date']})")
            output.append(
                f"Самый новый браузер: {time_stats['newest_browser']['browser_name']} ({time_stats['newest_browser']['release_date']})")
            output.append("")

        # Анализ версий
        if 'versions' in self.results:
            output.append("5. АНАЛИЗ ВЕРСИЙ")
            output.append("-" * 30)
            version_stats = self.results['versions']
            output.append(f"Средняя мажорная версия: {version_stats['avg_major_version']:.1f}")
            output.append(f"Максимальная версия: {version_stats['max_major_version']:.0f}")
            output.append(f"Минимальная версия: {version_stats['min_major_version']:.0f}")
            output.append(f"Диапазон версий: {version_stats['version_range']:.0f}")
            output.append("")

        # Условная рыночная доля
        if 'market_share' in self.results:
            output.append("6. УСЛОВНАЯ РЫНОЧНАЯ ДОЛЯ")
            output.append("-" * 30)
            sorted_share = sorted(self.results['market_share'].items(),
                                  key=lambda x: x[1], reverse=True)
            for browser, share in sorted_share:
                output.append(f"{browser}: {share:.1f}%")
            output.append("")

        # Заключение
        output.append("7. ЗАКЛЮЧЕНИЕ")
        output.append("-" * 30)
        if 'basic' in self.results:
            total = self.results['basic']['total_browsers']
            if total > 0:
                modern_count = sum(1 for row in self.data if int(row['release_date']) >= 2000)
                output.append(f"Доля современных браузеров (2000+): {(modern_count / total) * 100:.1f}%")

                webkit_count = sum(1 for row in self.data if 'webkit' in row['engine'].lower())
                output.append(f"Доля браузеров на WebKit: {(webkit_count / total) * 100:.1f}%")

        output.append("")
        output.append("=" * 80)
        output.append("КОНЕЦ ОТЧЕТА")
        output.append("=" * 80)

        # Вывод в текстовое поле
        self.results_text.insert(tk.END, "\n".join(output))

    def save_results(self):
        """Сохранение результатов в файл"""
        if not self.results:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения!")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                title="Сохранить результаты",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.results_text.get(1.0, tk.END))

                messagebox.showinfo("Успех", "Результаты сохранены успешно!")
                self.status_var.set("Результаты сохранены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    def clear_results(self):
        """Очистка результатов"""
        self.results_text.delete(1.0, tk.END)
        self.results = {}
        self.data = []
        self.status_var.set("Данные очищены")