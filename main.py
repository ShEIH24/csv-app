"""
Главный модуль приложения для работы с производственно-экономическими данными
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Импортируем все модули приложения
from file_creator import FileCreator
from file_printer import FilePrinter
from record_adder import RecordAdder
from record_editor import RecordEditor
from record_deleter import RecordDeleter
from file_sorter import FileSorter
from calculator import Calculator
from result_printer import ResultPrinter
from chart_viewer import ChartViewer


class MainApplication:
    """Главный класс приложения"""

    def __init__(self, root):
        self.root = root
        self.root.title("Система управления производственно-экономическими данными")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Создаем главное меню
        self.create_menu()

        # Создаем главный фрейм
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настраиваем grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Создаем интерфейс
        self.create_widgets()

        # Инициализируем модули
        self.init_modules()

    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Создать файл", command=self.create_file)
        file_menu.add_command(label="Печать исходного файла", command=self.print_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Меню "Редактирование"
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Редактирование", menu=edit_menu)
        edit_menu.add_command(label="Добавить записи", command=self.add_records)
        edit_menu.add_command(label="Корректировка записей", command=self.edit_records)
        edit_menu.add_command(label="Удалить записи", command=self.delete_records)
        edit_menu.add_command(label="Упорядочить записи", command=self.sort_file)

        # Меню "Расчеты"
        calc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Расчеты", menu=calc_menu)
        calc_menu.add_command(label="Расчет показателей", command=self.calculate)
        calc_menu.add_command(label="Печать результатов", command=self.print_results)

        # Меню "Графики"
        chart_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Графики", menu=chart_menu)
        chart_menu.add_command(label="Показать графики", command=self.show_charts)

    def create_widgets(self):
        """Создание виджетов главного окна"""
        # Заголовок
        title_label = ttk.Label(
            self.main_frame,
            text="Система управления производственно-экономическими данными",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Фрейм для кнопок
        buttons_frame = ttk.LabelFrame(self.main_frame, text="Операции", padding="10")
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Кнопки операций
        buttons = [
            ("1. Создать файл", self.create_file),
            ("2. Печать исходного файла", self.print_file),
            ("3. Добавить записи", self.add_records),
            ("4. Корректировка записей", self.edit_records),
            ("5. Удалить записи", self.delete_records),
            ("6. Упорядочить записи", self.sort_file),
            ("7. Расчет показателей", self.calculate),
            ("8. Печать результатов", self.print_results),
            ("9. Показать графики", self.show_charts),
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(buttons_frame, text=text, command=command, width=30)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky=tk.W + tk.E)

        # Настраиваем grid для кнопок
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def init_modules(self):
        """Инициализация модулей"""
        try:
            self.file_creator = FileCreator(self.root)
            self.file_printer = FilePrinter(self.root)
            self.record_adder = RecordAdder(self.root)
            self.record_editor = RecordEditor(self.root)
            self.record_deleter = RecordDeleter(self.root)
            self.file_sorter = FileSorter(self.root)
            self.calculator = Calculator(self.root)
            self.result_printer = ResultPrinter(self.root)
            self.chart_viewer = ChartViewer(self.root)

            self.status_var.set("Все модули загружены успешно")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации модулей: {str(e)}")
            self.status_var.set("Ошибка инициализации")

    def create_file(self):
        """Создание файла"""
        try:
            self.file_creator.show()
            self.status_var.set("Режим создания файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания файла: {str(e)}")

    def print_file(self):
        """Печать исходного файла"""
        try:
            self.file_printer.show()
            self.status_var.set("Режим печати файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка печати файла: {str(e)}")

    def add_records(self):
        """Добавление записей"""
        try:
            self.record_adder.show()
            self.status_var.set("Режим добавления записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка добавления записей: {str(e)}")

    def edit_records(self):
        """Корректировка записей"""
        try:
            self.record_editor.show()
            self.status_var.set("Режим корректировки записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка корректировки записей: {str(e)}")

    def delete_records(self):
        """Удаление записей"""
        try:
            self.record_deleter.show()
            self.status_var.set("Режим удаления записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления записей: {str(e)}")

    def sort_file(self):
        """Упорядочение записей"""
        try:
            self.file_sorter.show()
            self.status_var.set("Режим сортировки файла")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сортировки файла: {str(e)}")

    def calculate(self):
        """Расчет показателей"""
        try:
            self.calculator.show()
            self.status_var.set("Режим расчета показателей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {str(e)}")

    def print_results(self):
        """Печать результатов"""
        try:
            self.result_printer.show()
            self.status_var.set("Режим печати результатов")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка печати результатов: {str(e)}")

    def show_charts(self):
        """Показ графиков"""
        try:
            self.chart_viewer.show()
            self.status_var.set("Режим просмотра графиков")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка показа графиков: {str(e)}")


def main():
    """Главная функция"""
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()