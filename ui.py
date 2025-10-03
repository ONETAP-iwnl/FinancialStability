import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import get_enterprises, add_enterprise, get_financial_data, add_financial_data
from calculations import calculate_coefficients
from reports import export_to_excel

class FinancialApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система оценки финансовой устойчивости")
        self.geometry("800x600")

        self.selected_enterprise_id = None

        # Верхняя панель
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=10, fill="x")

        ttk.Label(top_frame, text="Выберите предприятие:").pack(side="left", padx=5)

        self.enterprise_combo = ttk.Combobox(top_frame, state="readonly", width=40)
        self.enterprise_combo.pack(side="left", padx=5)
        self.enterprise_combo.bind("<<ComboboxSelected>>", self.on_enterprise_selected)

        ttk.Button(top_frame, text="➕ Добавить", command=self.add_enterprise_dialog).pack(side="left", padx=5)
        ttk.Button(top_frame, text="📊 Добавить данные", command=self.add_financial_data_dialog).pack(side="left", padx=5)
        ttk.Button(top_frame, text="🧮 Рассчитать", command=self.calculate_and_show).pack(side="left", padx=5)
        ttk.Button(top_frame, text="📄 Сформировать отчёт", command=self.export_report).pack(side="left", padx=5)

        # Таблица для вывода коэффициентов
        columns = ("period", "current_ratio", "autonomy_ratio", "debt_ratio", "profit_sales", "profit_assets", "summary")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.heading("period", text="Период")
        self.tree.heading("current_ratio", text="Тек. ликвид.")
        self.tree.heading("autonomy_ratio", text="Автономия")
        self.tree.heading("debt_ratio", text="Зависимость")
        self.tree.heading("profit_sales", text="Рентаб. продаж (%)")
        self.tree.heading("profit_assets", text="Рентаб. активов (%)")
        self.tree.heading("summary", text="Оценка")

        # Подгон ширины
        for col in columns:
            self.tree.column(col, width=110, anchor="center")

        self.load_enterprises()

    # --- Загрузка предприятий в ComboBox ---
    def load_enterprises(self):
        enterprises = get_enterprises()
        self.enterprise_combo["values"] = [f"{row[0]}: {row[1]}" for row in enterprises]
        if enterprises:
            self.enterprise_combo.current(0)
            self.selected_enterprise_id = enterprises[0][0]

    # --- При выборе предприятия ---
    def on_enterprise_selected(self, event):
        val = self.enterprise_combo.get()
        if val:
            self.selected_enterprise_id = int(val.split(":")[0])

    # --- Диалог добавления предприятия ---
    def add_enterprise_dialog(self):
        name = simpledialog.askstring("Добавить предприятие", "Название предприятия:")
        if name:
            add_enterprise(name)
            self.load_enterprises()
            messagebox.showinfo("Успех", "Предприятие добавлено.")

    # --- Диалог добавления финансовых данных ---
    def add_financial_data_dialog(self):
        if not self.selected_enterprise_id:
            messagebox.showwarning("Ошибка", "Сначала выберите предприятие.")
            return

        dialog = FinancialDataDialog(self, self.selected_enterprise_id)
        self.wait_window(dialog)
        self.calculate_and_show()

    # --- Расчёт и вывод таблицы ---
    def calculate_and_show(self):
        if not self.selected_enterprise_id:
            messagebox.showwarning("Ошибка", "Сначала выберите предприятие.")
            return

        self.tree.delete(*self.tree.get_children())

        rows = get_financial_data(self.selected_enterprise_id)
        if not rows:
            messagebox.showinfo("Нет данных", "Для данного предприятия нет финансовых данных.")
            return

        for row in rows:
            res = calculate_coefficients(row)
            self.tree.insert("", "end", values=(
                res["period"],
                f"{res['current_ratio']:.2f}",
                f"{res['autonomy_ratio']:.2f}",
                f"{res['debt_ratio']:.2f}",
                f"{res['profitability_sales']:.2f}",
                f"{res['profitability_assets']:.2f}",
                res["summary"]
            ))
            
    def export_report(self):
        if not self.selected_enterprise_id:
            messagebox.showwarning("Ошибка", "Сначала выберите предприятие.")
            return
        val = self.enterprise_combo.get()
        if not val:
            messagebox.showwarning("Ошибка", "Не выбрано предприятие.")
            return
        enterprise_name = val.split(":")[1].strip()
        export_to_excel(self.selected_enterprise_id, enterprise_name)
        messagebox.showinfo("Готово", "Отчёт успешно экспортирован в Excel.")

# --- Окно ввода финансовых данных ---
class FinancialDataDialog(tk.Toplevel):
    def __init__(self, parent, enterprise_id):
        super().__init__(parent)
        self.title("Добавить финансовые данные")
        self.enterprise_id = enterprise_id
        self.resizable(False, False)

        fields = [
            ("Период", "period"),
            ("Активы", "assets"),
            ("Обязательства", "liabilities"),
            ("Собственный капитал", "equity"),
            ("Прибыль", "profit"),
            ("Выручка", "revenue"),
            ("Оборотные активы", "current_assets"),
            ("Краткосрочные обязательства", "current_liabilities")
        ]

        self.entries = {}
        for i, (label_text, field) in enumerate(fields):
            ttk.Label(self, text=label_text + ":").grid(row=i, column=0, padx=5, pady=3, sticky="e")
            entry = ttk.Entry(self)
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.entries[field] = entry

        ttk.Button(self, text="Сохранить", command=self.save_data).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_data(self):
        try:
            period = self.entries["period"].get().strip()
            assets = float(self.entries["assets"].get())
            liabilities = float(self.entries["liabilities"].get())
            equity = float(self.entries["equity"].get())
            profit = float(self.entries["profit"].get())
            revenue = float(self.entries["revenue"].get())
            current_assets = float(self.entries["current_assets"].get())
            current_liabilities = float(self.entries["current_liabilities"].get())
        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте корректность введённых чисел.")
            return

        add_financial_data(
            self.enterprise_id,
            period,
            assets,
            liabilities,
            equity,
            profit,
            revenue,
            current_assets,
            current_liabilities
        )

        messagebox.showinfo("Успех", "Данные добавлены.")
        self.destroy()
    
