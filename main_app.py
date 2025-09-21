import customtkinter as ctk
import numpy as np
from db_manager import DBManager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from tkinter import messagebox

class App(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.chart_canvas = None
        self.trends_canvas = None
        self.edit_window = None

        self.title("Budget Management System")
        self.geometry("1100x700")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar --- #
        self.sidebar_frame = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        ctk.CTkLabel(self.sidebar_frame, text="BMS", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame_by_name("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)
        self.history_button = ctk.CTkButton(self.sidebar_frame, text="History", command=lambda: self.select_frame_by_name("history"))
        self.history_button.grid(row=2, column=0, padx=20, pady=10)
        self.reports_button = ctk.CTkButton(self.sidebar_frame, text="Reports", command=lambda: self.select_frame_by_name("reports"))
        self.reports_button.grid(row=3, column=0, padx=20, pady=10)
        self.budgets_button = ctk.CTkButton(self.sidebar_frame, text="Budgets", command=lambda: self.select_frame_by_name("budgets"))
        self.budgets_button.grid(row=4, column=0, padx=20, pady=10)
        self.savings_button = ctk.CTkButton(self.sidebar_frame, text="Savings", command=lambda: self.select_frame_by_name("savings"))
        self.savings_button.grid(row=5, column=0, padx=20, pady=10)

        # --- Main Content --- #
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        self.dashboard_frame = ctk.CTkFrame(self.main_content_frame, fg_color='transparent')
        self.history_frame = ctk.CTkFrame(self.main_content_frame, fg_color='transparent')
        self.reports_frame = ctk.CTkFrame(self.main_content_frame, fg_color='transparent')
        self.budgets_frame = ctk.CTkFrame(self.main_content_frame, fg_color='transparent')
        self.savings_frame = ctk.CTkFrame(self.main_content_frame, fg_color='transparent')
        
        self.setup_dashboard_ui()
        self.setup_history_ui()
        self.setup_reports_ui()
        self.setup_budgets_ui()
        self.setup_savings_ui()

        # ---- Status and Copyright Bar ---
        footer_frame = ctk.CTkFrame(self, corner_radius=0, height=25)
        footer_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        footer_frame.grid_columnconfigure(0, weight=1)

        self.status_bar = ctk.CTkLabel(footer_frame, text="Welcome!", anchor="w", font=ctk.CTkFont(size=12))
        self.status_bar.grid(row=0, column=0, sticky="ew", padx=(10, 5))

        copyright_label = ctk.CTkLabel(footer_frame, text="© 2025, Hirwa Munyaneza Jean Leon", text_color="gray50", anchor="e", font=ctk.CTkFont(size=11))
        copyright_label.grid(row=0, column=1, sticky="e", padx=(5, 10))

        # ---- Select initial frame ----
        self.select_frame_by_name("dashboard")

    def select_frame_by_name(self, name):
        buttons = {"dashboard": self.dashboard_button, "history": self.history_button, "reports": self.reports_button, "budgets": self.budgets_button, "savings": self.savings_button}
        for btn_name, btn in buttons.items():
            btn.configure(fg_color="#1f6aa5" if name == btn_name else "transparent")
        
        for frame in [self.dashboard_frame, self.history_frame, self.reports_frame, self.budgets_frame, self.savings_frame]:
            frame.grid_forget()

        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
            self.update_dashboard()
        elif name == "history":
            self.history_frame.grid(row=0, column=0, sticky="nsew")
            self.search_transactions_action()
        elif name == "reports":
            self.reports_frame.grid(row=0, column=0, sticky="nsew")
            self.update_trends_chart()
        elif name == "budgets":
            self.budgets_frame.grid(row=0, column=0, sticky="nsew")
            self.update_budgets_view()
        elif name == "savings":
            self.savings_frame.grid(row=0, column=0, sticky="nsew")
            self.update_savings_view()

    def show_status_message(self, message, is_error=False):
        self.status_bar.configure(text=message, text_color="#F44336" if is_error else "gray60")

    def update_all_views(self):
        active_frame_name = self.get_active_frame_name()
        if active_frame_name == "dashboard": self.update_dashboard()
        if active_frame_name == "history": self.search_transactions_action()
        if active_frame_name == "reports": self.update_trends_chart()
        if active_frame_name == "budgets": self.update_budgets_view()
        if active_frame_name == "savings": self.update_savings_view()

    def get_active_frame_name(self):
        buttons = {"dashboard": self.dashboard_button, "history": self.history_button, "reports": self.reports_button, "budgets": self.budgets_button, "savings": self.savings_button}
        for name, button in buttons.items():
            if button.cget("fg_color") != "transparent":
                return name
        return "dashboard"

    # --- DASHBOARD ---
    def setup_dashboard_ui(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(2, weight=1)
        summary_frame = ctk.CTkFrame(self.dashboard_frame)
        summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.balance_label = ctk.CTkLabel(summary_frame, text="")
        self.balance_label.grid(row=0, column=0, padx=10, pady=10)
        self.income_label = ctk.CTkLabel(summary_frame, text="")
        self.income_label.grid(row=0, column=1, padx=10, pady=10)
        self.expense_label = ctk.CTkLabel(summary_frame, text="")
        self.expense_label.grid(row=0, column=2, padx=10, pady=10)
        actions_frame = ctk.CTkFrame(self.dashboard_frame)
        actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        actions_frame.grid_columnconfigure((0,1,2), weight=1)
        self.amount_entry = ctk.CTkEntry(actions_frame, placeholder_text="Amount")
        self.amount_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.desc_entry = ctk.CTkEntry(actions_frame, placeholder_text="Description")
        self.desc_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.category_combobox = ctk.CTkComboBox(actions_frame, values=[])
        self.category_combobox.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        ctk.CTkButton(actions_frame, text="Add Income", command=self.add_income_action).grid(row=0, column=3, padx=5, pady=10)
        ctk.CTkButton(actions_frame, text="Add Expense", command=self.add_expense_action).grid(row=0, column=4, padx=(5, 10), pady=10)
        bottom_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame = ctk.CTkFrame(bottom_frame)
        self.chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.transactions_frame = ctk.CTkScrollableFrame(bottom_frame, label_text="Recent Transactions")
        self.transactions_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    def add_income_action(self):
        self.add_transaction("income")

    def add_expense_action(self):
        self.add_transaction("expense")

    def add_transaction(self, trans_type):
        amount_str = self.amount_entry.get()
        description = self.desc_entry.get()
        category = self.category_combobox.get()
        if not all([amount_str, description, category]):
            self.show_status_message("Error: All fields are required.", is_error=True)
            return
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_status_message("Error: Amount must be a number.", is_error=True)
            return
        self.db.add_transaction(amount, trans_type, category, description)
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.category_combobox.set("")
        self.update_all_views()
        self.show_status_message(f"{trans_type.capitalize()} of {amount:,.0f} RWF added.")

    def update_dashboard(self):
        summary = self.db.get_summary()
        self.balance_label.configure(text=f"BALANCE\n{summary['balance']:,.0f} RWF")
        self.income_label.configure(text=f"INCOME\n{summary['total_income']:,.0f} RWF")
        self.expense_label.configure(text=f"EXPENSE\n{summary['total_expense']:,.0f} RWF")
        self.category_combobox.configure(values=self.db.get_categories())
        self.update_transactions_list(self.transactions_frame, lambda: self.db.get_transactions(limit=15))
        self.update_pie_chart()

    def update_transactions_list(self, frame, get_trans_func):
        for widget in frame.winfo_children():
            widget.destroy()
        transactions = get_trans_func()
        if not transactions:
            ctk.CTkLabel(frame, text="No transactions found.").pack(pady=10)
        else:
            for trans in transactions:
                trans_id = trans['id']
                trans_frame = ctk.CTkFrame(frame)
                trans_frame.pack(fill="x", padx=5, pady=5)
                trans_frame.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(trans_frame, text=trans['transaction_date'].strftime("%Y-%m-%d"), width=80).grid(row=0, column=0, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['description'], anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['category'], anchor="w", text_color="gray60").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                amount_text = f"{trans['amount']:,.0f} RWF"
                amount_color = "#4CAF50" if trans['type'] == 'income' else "#F44336"
                ctk.CTkLabel(trans_frame, text=amount_text, text_color=amount_color, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").grid(row=0, column=3, padx=5, pady=5, sticky="e")
                ctk.CTkButton(trans_frame, text="Edit", width=40, command=lambda t_id=trans_id: self.open_edit_window(t_id)).grid(row=0, column=4, padx=5)
                ctk.CTkButton(trans_frame, text="Del", width=40, command=lambda t_id=trans_id: self.delete_transaction_action(t_id)).grid(row=0, column=5, padx=(0,5))

    def delete_transaction_action(self, transaction_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to permanently delete this transaction?"):
            self.db.delete_transaction(transaction_id)
            self.show_status_message("Transaction deleted.")
            self.update_all_views()

    def open_edit_window(self, transaction_id):
        if self.edit_window is not None and self.edit_window.winfo_exists():
            self.edit_window.focus()
            return
        trans = self.db.get_transaction_by_id(transaction_id)
        if not trans:
            self.show_status_message("Error: Transaction not found.", is_error=True)
            return
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Edit Transaction")
        self.edit_window.geometry("400x300")
        self.edit_window.transient(self)
        self.edit_window.grab_set()
        ctk.CTkLabel(self.edit_window, text="Amount:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        amount_entry = ctk.CTkEntry(self.edit_window)
        amount_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        amount_entry.insert(0, f"{trans['amount']:.0f}")
        ctk.CTkLabel(self.edit_window, text="Description:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        desc_entry = ctk.CTkEntry(self.edit_window)
        desc_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        desc_entry.insert(0, trans['description'])
        ctk.CTkLabel(self.edit_window, text="Category:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        cat_combobox = ctk.CTkComboBox(self.edit_window, values=self.db.get_categories())
        cat_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        cat_combobox.set(trans['category'])
        ctk.CTkLabel(self.edit_window, text="Type:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        type_combobox = ctk.CTkComboBox(self.edit_window, values=["income", "expense"])
        type_combobox.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        type_combobox.set(trans['type'])
        ctk.CTkLabel(self.edit_window, text="Date (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        date_entry = ctk.CTkEntry(self.edit_window)
        date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        date_entry.insert(0, trans['transaction_date'])
        save_btn = ctk.CTkButton(self.edit_window, text="Save Changes", command=lambda: self.save_edited_transaction(transaction_id, date_entry.get(), amount_entry.get(), type_combobox.get(), cat_combobox.get(), desc_entry.get()))
        save_btn.grid(row=5, column=1, padx=10, pady=20)
        ctk.CTkButton(self.edit_window, text="Cancel", command=self.edit_window.destroy, fg_color="gray50").grid(row=5, column=0, padx=10, pady=20)

    def save_edited_transaction(self, trans_id, date_str, amount_str, trans_type, category, desc):
        if not all([date_str, amount_str, trans_type, category, desc]):
            self.show_status_message("Error: All fields are required.", is_error=True)
            return
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_status_message("Error: Amount must be a number.", is_error=True)
            return
        try:
            date = datetime.datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except ValueError:
            self.show_status_message("Error: Date must be in YYYY-MM-DD format.", is_error=True)
            return
        self.db.update_transaction(trans_id, date, amount, trans_type, category, desc)
        self.edit_window.destroy()
        self.show_status_message("Transaction updated.")
        self.update_all_views()

    def update_pie_chart(self):
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        fig = Figure(figsize=(5, 5), dpi=100, facecolor="#2B2B2B")
        ax = fig.add_subplot(111)
        spending_data = self.db.get_spending_by_category()
        if not spending_data:
            ax.text(0.5, 0.5, "No expense data", ha='center', va='center', color="white")
            ax.axis('off')
        else:
            labels = [item['category'] for item in spending_data]
            sizes = [item['total'] for item in spending_data]
            ax.pie(sizes, labels=labels, autopct=lambda p: f'{p:.0f}%', startangle=140, textprops={'color':"w"})
            ax.axis('equal')
        fig.tight_layout()
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    # --- REPORTS PAGE ---
    def setup_reports_ui(self):
        self.reports_frame.grid_columnconfigure(0, weight=1)
        self.reports_frame.grid_rowconfigure(0, weight=1)
        self.trends_chart_frame = ctk.CTkFrame(self.reports_frame)
        self.trends_chart_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def update_trends_chart(self):
        if self.trends_canvas:
            self.trends_canvas.get_tk_widget().destroy()
        db_data = self.db.get_monthly_summary()
        today = datetime.date.today()
        months_data = {}
        for i in range(12):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            months_data[(year, month)] = {'income': 0, 'expense': 0}
        for row in db_data:
            if (row['year'], row['month']) in months_data:
                months_data[(row['year'], row['month'])] = {'income': row['total_income'], 'expense': row['total_expense']}
        sorted_months = sorted(months_data.keys())
        labels = [f"{datetime.date(y, m, 1):%b %y}" for y, m in sorted_months]
        incomes = [months_data[key]['income'] for key in sorted_months]
        expenses = [months_data[key]['expense'] for key in sorted_months]
        fig = Figure(figsize=(10, 6), dpi=100, facecolor="#2B2B2B")
        ax = fig.add_subplot(111)
        x = np.arange(len(labels))
        width = 0.35
        ax.bar(x - width/2, incomes, width, label='Income', color='#4CAF50')
        ax.bar(x + width/2, expenses, width, label='Expense', color='#F44336')
        ax.set_ylabel('Amount (RWF)', color='white')
        ax.set_title('Monthly Income vs Expense', color='white')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, color='white')
        ax.legend()
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor("#343638")
        fig.tight_layout()
        self.trends_canvas = FigureCanvasTkAgg(fig, master=self.trends_chart_frame)
        self.trends_canvas.draw()
        self.trends_canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    # --- HISTORY PAGE ---
    def setup_history_ui(self):
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(1, weight=1)
        filter_frame = ctk.CTkFrame(self.history_frame)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        filter_frame.grid_columnconfigure(0, weight=1)
        self.search_desc_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search by description...")
        self.search_desc_entry.grid(row=0, column=0, columnspan=2, padx=(10,5), pady=5, sticky="ew")
        self.search_cat_combo = ctk.CTkComboBox(filter_frame, values=["All Categories"] + self.db.get_categories())
        self.search_cat_combo.set("All Categories")
        self.search_cat_combo.grid(row=0, column=2, padx=5, pady=5)
        self.search_type_combo = ctk.CTkComboBox(filter_frame, values=["All Types", "income", "expense"])
        self.search_type_combo.set("All Types")
        self.search_type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.start_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="Start Date (YYYY-MM-DD)")
        self.start_date_entry.grid(row=1, column=0, padx=(10,5), pady=5, sticky="ew")
        self.end_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="End Date (YYYY-MM-DD)")
        self.end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(filter_frame, text="Search", command=self.search_transactions_action).grid(row=1, column=2, padx=5, pady=5)
        ctk.CTkButton(filter_frame, text="Clear", command=self.clear_filters_action, fg_color="gray50").grid(row=1, column=3, padx=5, pady=5)
        self.history_results_frame = ctk.CTkScrollableFrame(self.history_frame, label_text="Transactions")
        self.history_results_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,20))

    def search_transactions_action(self):
        desc = self.search_desc_entry.get()
        cat = self.search_cat_combo.get()
        trans_type = self.search_type_combo.get()
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        search_params = {
            "description": desc if desc else None,
            "category": cat if cat != "All Categories" else None,
            "trans_type": trans_type if trans_type != "All Types" else None,
            "start_date": None,
            "end_date": None
        }
        try:
            if start_date_str: search_params["start_date"] = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str: search_params["end_date"] = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError: self.show_status_message("Error: Date format must be YYYY-MM-DD.", is_error=True); return
        self.update_transactions_list(frame=self.history_results_frame, get_trans_func=lambda: self.db.search_transactions(**search_params))
        self.show_status_message("Search complete.")

    def clear_filters_action(self):
        self.search_desc_entry.delete(0, "end")
        self.search_cat_combo.set("All Categories")
        self.search_type_combo.set("All Types")
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.search_transactions_action()

    # --- BUDGETS PAGE ---
    def setup_budgets_ui(self):
        self.budgets_frame.grid_columnconfigure(0, weight=1)
        self.budgets_frame.grid_rowconfigure(0, weight=1)
        self.budgets_scroll_frame = ctk.CTkScrollableFrame(self.budgets_frame, label_text="Monthly Budgets")
        self.budgets_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.budgets_scroll_frame.grid_columnconfigure(0, weight=1)

    def update_budgets_view(self):
        for widget in self.budgets_scroll_frame.winfo_children(): widget.destroy()
        now = datetime.datetime.now()
        budget_data = self.db.get_budgets_for_month(now.month, now.year)
        for item in budget_data:
            category = item['category']; budget = item['budget_amount']; spent = item['spent_amount']; progress = (spent / budget) if budget > 0 else 0; progress = min(progress, 1.0)
            item_frame = ctk.CTkFrame(self.budgets_scroll_frame); item_frame.pack(fill="x", expand=True, padx=10, pady=5); item_frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(item_frame, text=category, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            progress_bar = ctk.CTkProgressBar(item_frame, orientation="horizontal"); progress_bar.set(progress); progress_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
            ctk.CTkLabel(item_frame, text=f"{spent:,.0f} / {budget:,.0f} RWF").grid(row=0, column=1, padx=10, pady=5, sticky="e")
            budget_entry = ctk.CTkEntry(item_frame, placeholder_text="Set Budget");
            if budget > 0: budget_entry.insert(0, f"{budget:.0f}")
            budget_entry.grid(row=0, column=2, padx=10, pady=5)
            ctk.CTkButton(item_frame, text="Save", width=60, command=lambda c=category, e=budget_entry: self.save_budget_action(c, e)).grid(row=0, column=3, padx=10, pady=5)

    def save_budget_action(self, category, entry_widget):
        try: new_budget = float(entry_widget.get()); now = datetime.datetime.now(); self.db.set_budget(category, new_budget, now.month, now.year); self.update_budgets_view(); self.show_status_message(f"Budget for {category} saved.")
        except (ValueError, TypeError): self.show_status_message(f"Error: Invalid budget for {category}.", is_error=True)

    # --- SAVINGS PAGE ---
    def setup_savings_ui(self):
        self.savings_frame.grid_columnconfigure(0, weight=1)
        self.savings_frame.grid_rowconfigure(1, weight=1)
        form_frame = ctk.CTkFrame(self.savings_frame); form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20); form_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(form_frame, text="Create New Savings Goal", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=(10,0), sticky="w")
        self.goal_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Goal Name"); self.goal_name_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.goal_target_entry = ctk.CTkEntry(form_frame, placeholder_text="Target Amount"); self.goal_target_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(form_frame, text="Create Goal", command=self.create_goal_action).grid(row=1, column=2, padx=10, pady=10)
        self.savings_scroll_frame = ctk.CTkScrollableFrame(self.savings_frame, label_text="Your Goals"); self.savings_scroll_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

    def create_goal_action(self):
        name = self.goal_name_entry.get(); target_str = self.goal_target_entry.get()
        if not all([name, target_str]): self.show_status_message("Error: All fields required.", is_error=True); return
        try: target = float(target_str)
        except ValueError: self.show_status_message("Error: Target must be a number.", is_error=True); return
        self.db.add_savings_goal(name, target); self.goal_name_entry.delete(0, "end"); self.goal_target_entry.delete(0, "end"); self.update_savings_view(); self.show_status_message(f"Goal '{name}' created.")

    def update_savings_view(self):
        for widget in self.savings_scroll_frame.winfo_children(): widget.destroy()
        goals = self.db.get_savings_goals()
        if not goals: ctk.CTkLabel(self.savings_scroll_frame, text="No savings goals yet.").pack(pady=10)
        else:
            for goal in goals: 
                goal_id = goal['id']; name = goal['name']; target = goal['target_amount']; current = goal['current_amount']; progress = (current / target) if target > 0 else 0; progress = min(progress, 1.0)
                item_frame = ctk.CTkFrame(self.savings_scroll_frame); item_frame.pack(fill="x", expand=True, padx=10, pady=5); item_frame.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(item_frame, text=name, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                progress_bar = ctk.CTkProgressBar(item_frame, orientation="horizontal"); progress_bar.set(progress); progress_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
                ctk.CTkLabel(item_frame, text=f"{current:,.0f} / {target:,.0f} RWF").grid(row=0, column=1, padx=10, pady=5, sticky="e")
                add_funds_entry = ctk.CTkEntry(item_frame, placeholder_text="Add Funds"); add_funds_entry.grid(row=0, column=2, padx=10, pady=5)
                ctk.CTkButton(item_frame, text="Add", width=50, command=lambda g_id=goal_id, g_name=name, e=add_funds_entry: self.add_funds_action(g_id, g_name, e)).grid(row=0, column=3, padx=10, pady=5)

    def add_funds_action(self, goal_id, goal_name, entry_widget):
        try: 
            amount = float(entry_widget.get())
            if amount <= 0: self.show_status_message("Error: Amount must be positive.", is_error=True); return
            self.db.add_to_savings_goal(goal_id, goal_name, amount); self.update_savings_view(); self.show_status_message(f"{amount:,.0f} RWF added to '{goal_name}'.")
        except (ValueError, TypeError): self.show_status_message(f"Error: Invalid amount for {goal_name}.", is_error=True)