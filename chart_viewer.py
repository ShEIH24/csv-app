"""
Модуль для отображения графиков и диаграмм по данным браузеров
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import Counter
import os


class ChartViewer:
    """Класс для просмотра графиков по данным браузеров"""

    def __init__(self, root):
        self.root = root
        self.window = None
        self.data = None
        self.canvas = None
        self.figure = None

    def show(self):
        """Показать окно просмотра графиков"""
        if self.window is None or not self.window.winfo_exists():
            self.create_window()
        else:
            self.window.lift()
            self.window.focus()

    def create_window(self):
        """Создание окна просмотра графиков"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Просмотр графиков - Данные браузеров")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)

        # Главный фрейм
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Кнопка загрузки файла
        ttk.Button(control_frame, text="Загрузить CSV файл",
                   command=self.load_file).grid(row=0, column=0, padx=(0, 10))

        # Статус загрузки
        self.status_var = tk.StringVar()
        self.status_var.set("Файл не загружен")
        ttk.Label(control_frame, textvariable=self.status_var).grid(row=0, column=1, padx=10)

        # Панель выбора типа графика
        chart_frame = ttk.LabelFrame(main_frame, text="Тип графика", padding="5")
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Кнопки для разных типов графиков
        chart_buttons = [
            ("Распределение по разработчикам", self.show_developer_chart),
            ("Временная шкала выпуска", self.show_timeline_chart),
            ("Распределение движков", self.show_engine_chart),
            ("Версии браузеров", self.show_version_chart),
            ("Статистика по годам", self.show_year_stats),
            ("Сравнение популярности", self.show_popularity_chart)
        ]

        for i, (text, command) in enumerate(chart_buttons):
            btn = ttk.Button(chart_frame, text=text, command=command, width=25)
            btn.grid(row=i, column=0, pady=2, sticky=(tk.W, tk.E))

        # Фрейм для отображения графика
        self.chart_frame = ttk.LabelFrame(main_frame, text="График", padding="5")
        self.chart_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Инициализация matplotlib
        self.init_matplotlib()

    def init_matplotlib(self):
        """Инициализация matplotlib"""
        plt.style.use('default')
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.chart_frame.columnconfigure(0, weight=1)
        self.chart_frame.rowconfigure(0, weight=1)

        # Показать начальное сообщение
        self.ax.text(0.5, 0.5, 'Загрузите CSV файл для отображения графиков',
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, fontsize=14)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def load_file(self):
        """Загрузка CSV файла"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите CSV файл с данными браузеров",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if file_path:
                # Загружаем данные
                self.data = pd.read_csv(file_path, encoding='utf-8')

                # Проверяем наличие необходимых колонок
                required_columns = ['browser_name', 'developer', 'release_date', 'engine']
                missing_columns = [col for col in required_columns if col not in self.data.columns]

                if missing_columns:
                    messagebox.showwarning("Предупреждение",
                                           f"В файле отсутствуют колонки: {', '.join(missing_columns)}")

                # Обработка данных
                self.process_data()

                self.status_var.set(f"Загружено записей: {len(self.data)}")
                messagebox.showinfo("Успех", f"Файл успешно загружен!\nКоличество записей: {len(self.data)}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файла:\n{str(e)}")

    def process_data(self):
        """Обработка данных после загрузки"""
        if self.data is not None:
            # Преобразование даты
            if 'release_date' in self.data.columns:
                self.data['release_year'] = pd.to_numeric(self.data['release_date'], errors='coerce')

            # Очистка данных от пустых значений
            self.data = self.data.dropna(subset=['browser_name'])

    def clear_chart(self):
        """Очистка графика"""
        self.ax.clear()

    def show_developer_chart(self):
        """График распределения браузеров по разработчикам"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            # Подсчет браузеров по разработчикам
            developer_counts = self.data['developer'].value_counts()

            # Создание круговой диаграммы
            colors = plt.cm.Set3(np.linspace(0, 1, len(developer_counts)))
            wedges, texts, autotexts = self.ax.pie(developer_counts.values,
                                                   labels=developer_counts.index,
                                                   autopct='%1.1f%%',
                                                   colors=colors,
                                                   startangle=90)

            self.ax.set_title('Распределение браузеров по разработчикам', fontsize=14, fontweight='bold')

            # Улучшение читаемости
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")

    def show_timeline_chart(self):
        """График временной шкалы выпуска браузеров"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            # Подсчет браузеров по годам
            if 'release_year' in self.data.columns:
                year_counts = self.data['release_year'].value_counts().sort_index()

                # Создание столбчатой диаграммы
                bars = self.ax.bar(year_counts.index, year_counts.values,
                                   color='skyblue', edgecolor='navy', alpha=0.7)

                self.ax.set_xlabel('Год выпуска', fontsize=12)
                self.ax.set_ylabel('Количество браузеров', fontsize=12)
                self.ax.set_title('Временная шкала выпуска браузеров', fontsize=14, fontweight='bold')
                self.ax.grid(True, alpha=0.3)

                # Добавление значений на столбцы
                for bar in bars:
                    height = bar.get_height()
                    self.ax.annotate(f'{int(height)}',
                                     xy=(bar.get_x() + bar.get_width() / 2, height),
                                     xytext=(0, 3),
                                     textcoords="offset points",
                                     ha='center', va='bottom')
            else:
                self.ax.text(0.5, 0.5, 'Данные о годах выпуска недоступны',
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, fontsize=12)

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")

    def show_engine_chart(self):
        """График распределения движков браузеров"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            # Подсчет движков
            engine_counts = self.data['engine'].value_counts()

            # Создание горизонтальной столбчатой диаграммы
            bars = self.ax.barh(engine_counts.index, engine_counts.values,
                                color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])

            self.ax.set_xlabel('Количество браузеров', fontsize=12)
            self.ax.set_ylabel('Движок браузера', fontsize=12)
            self.ax.set_title('Распределение браузеров по движкам', fontsize=14, fontweight='bold')
            self.ax.grid(True, alpha=0.3, axis='x')

            # Добавление значений на столбцы
            for i, bar in enumerate(bars):
                width = bar.get_width()
                self.ax.annotate(f'{int(width)}',
                                 xy=(width, bar.get_y() + bar.get_height() / 2),
                                 xytext=(3, 0),
                                 textcoords="offset points",
                                 ha='left', va='center')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")

    def show_version_chart(self):
        """График анализа версий браузеров"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            if 'latest_version' in self.data.columns:
                # Анализ основных версий (первая цифра)
                versions = self.data['latest_version'].dropna().astype(str)
                major_versions = [v.split('.')[0] for v in versions if v.split('.')[0].isdigit()]
                version_counts = Counter(major_versions)

                # Берем топ-10 версий
                top_versions = dict(sorted(version_counts.items(),
                                           key=lambda x: int(x[0]) if x[0].isdigit() else 0)[-10:])

                # Создание линейного графика
                x_pos = range(len(top_versions))
                self.ax.plot(x_pos, list(top_versions.values()),
                             marker='o', linewidth=2, markersize=8, color='#E74C3C')

                self.ax.set_xticks(x_pos)
                self.ax.set_xticklabels(list(top_versions.keys()))
                self.ax.set_xlabel('Основная версия', fontsize=12)
                self.ax.set_ylabel('Количество браузеров', fontsize=12)
                self.ax.set_title('Распределение по основным версиям браузеров', fontsize=14, fontweight='bold')
                self.ax.grid(True, alpha=0.3)

                # Добавление значений на точки
                for i, v in enumerate(top_versions.values()):
                    self.ax.annotate(f'{v}',
                                     xy=(i, v),
                                     xytext=(0, 10),
                                     textcoords="offset points",
                                     ha='center', va='bottom')
            else:
                self.ax.text(0.5, 0.5, 'Данные о версиях недоступны',
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, fontsize=12)

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")

    def show_year_stats(self):
        """График статистики по годам"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            if 'release_year' in self.data.columns:
                # Группировка по годам и разработчикам
                year_dev_data = self.data.groupby(['release_year', 'developer']).size().unstack(fill_value=0)

                # Создание стековой диаграммы
                year_dev_data.plot(kind='bar', stacked=True, ax=self.ax,
                                   colormap='Set3', alpha=0.8)

                self.ax.set_xlabel('Год выпуска', fontsize=12)
                self.ax.set_ylabel('Количество браузеров', fontsize=12)
                self.ax.set_title('Статистика выпуска браузеров по годам и разработчикам',
                                  fontsize=14, fontweight='bold')
                self.ax.legend(title='Разработчик', bbox_to_anchor=(1.05, 1), loc='upper left')
                self.ax.grid(True, alpha=0.3)

                # Поворот подписей оси X
                self.ax.tick_params(axis='x', rotation=45)
            else:
                self.ax.text(0.5, 0.5, 'Данные о годах выпуска недоступны',
                             horizontalalignment='center', verticalalignment='center',
                             transform=self.ax.transAxes, fontsize=12)

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")

    def show_popularity_chart(self):
        """График сравнения популярности браузеров"""
        if self.data is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите файл данных!")
            return

        try:
            self.clear_chart()

            # Создание комбинированного анализа
            browser_counts = self.data['browser_name'].value_counts().head(10)

            # Создание диаграммы с градиентом
            colors = plt.cm.viridis(np.linspace(0, 1, len(browser_counts)))
            bars = self.ax.bar(range(len(browser_counts)), browser_counts.values,
                               color=colors, alpha=0.8)

            self.ax.set_xticks(range(len(browser_counts)))
            self.ax.set_xticklabels(browser_counts.index, rotation=45, ha='right')
            self.ax.set_xlabel('Браузер', fontsize=12)
            self.ax.set_ylabel('Количество записей', fontsize=12)
            self.ax.set_title('Топ-10 браузеров в базе данных', fontsize=14, fontweight='bold')

            # Добавление значений на столбцы
            for bar in bars:
                height = bar.get_height()
                self.ax.annotate(f'{int(height)}',
                                 xy=(bar.get_x() + bar.get_width() / 2, height),
                                 xytext=(0, 3),
                                 textcoords="offset points",
                                 ha='center', va='bottom', fontweight='bold')

            self.ax.grid(True, alpha=0.3, axis='y')

            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания графика:\n{str(e)}")


# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно для тестирования

    viewer = ChartViewer(root)
    viewer.show()

    root.mainloop()