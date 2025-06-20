"""
Модуль для корректировки записей в файле CSV с данными о браузерах
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os


class RecordEditor:
    """Класс для корректировки записей в файле"""

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.filename = ""
        self.records = []
        self.headers = ["browser_id", "browser_name", "developer", "release_date", "latest_version", "engine"]

    def show(self):
        """Показ окна корректировки записей"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Корректировка записей")
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
        main_frame.rowconfigure(2, weight=1)

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
        ttk.Button(control_frame, text="Редактировать запись", command=self.edit_record).grid(row=0, column=1,
                                                                                              padx=(0, 10))
        ttk.Button(control_frame, text="Сохранить изменения", command=self.save_data).grid(row=0, column=2,
                                                                                           padx=(0, 10))
        ttk.Button(control_frame, text="Обновить таблицу", command=self.refresh_table).grid(row=0, column=3)

        # Таблица для отображения записей
        table_frame = ttk.LabelFrame(main_frame, text="Записи браузеров", padding="5")
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создание Treeview
        self.tree = ttk.Treeview(table_frame, columns=self.headers, show='headings', height=15)

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

        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("Выберите файл для редактирования")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

    def select_file(self):
        """Выбор файла для редактирования"""
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
            with open(self.filename, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.records.append(row)

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

    def edit_record(self):
        """Редактирование выбранной записи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
            return

        item_id = selection[0]
        record_index = int(item_id)
        record = self.records[record_index]

        self.show_edit_dialog(record, record_index)

    def show_edit_dialog(self, record, record_index):
        """Показ диалога редактирования записи"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Редактирование записи")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()

        # Центрирование окна
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Поля для редактирования
        entries = {}
        field_labels = {
            "browser_id": "ID браузера",
            "browser_name": "Название браузера",
            "developer": "Разработчик",
            "release_date": "Дата выпуска",
            "latest_version": "Последняя версия",
            "engine": "Движок"
        }

        for i, header in enumerate(self.headers):
            ttk.Label(main_frame, text=field_labels[header] + ":").grid(row=i, column=0, sticky=tk.W, pady=5)

            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
            entry.insert(0, record.get(header, ""))
            entries[header] = entry

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.headers), column=0, columnspan=2, pady=20)

        def save_changes():
            try:
                # Валидация данных
                new_data = {}
                for header in self.headers:
                    value = entries[header].get().strip()
                    if not value:
                        messagebox.showwarning("Предупреждение", f"Поле '{field_labels[header]}' не может быть пустым")
                        return
                    new_data[header] = value

                # Проверка уникальности ID (если ID изменился)
                if new_data['browser_id'] != record['browser_id']:
                    for i, r in enumerate(self.records):
                        if i != record_index and r['browser_id'] == new_data['browser_id']:
                            messagebox.showerror("Ошибка", "Браузер с таким ID уже существует")
                            return

                # Сохранение изменений
                self.records[record_index] = new_data
                self.refresh_table()

                # Выделение измененной записи
                self.tree.selection_set(str(record_index))
                self.tree.focus(str(record_index))

                self.status_var.set("Запись успешно изменена")
                dialog.destroy()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

        ttk.Button(button_frame, text="Сохранить", command=save_changes).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).grid(row=0, column=1)

        # Фокус на первое поле
        entries[self.headers[0]].focus()

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
            self.status_var.set("Данные сохранены в файл")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения файла: {str(e)}")


if __name__ == "__main__":
    # Тестирование модуля
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно

    editor = RecordEditor(root)
    editor.show()

    root.mainloop()