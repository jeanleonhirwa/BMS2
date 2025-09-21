import customtkinter as ctk
from db_manager import DBManager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class App(ctk.CTk):
    def __init__(self, db_manager):
        super().__init__()

        self.db = db_manager
        self.chart_canvas = None

        # ---- Window Setup ----
        self.title("Budget Management System")
        self.geometry("1100x700")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ---- Sidebar Navigation ----
        self.sidebar_frame = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BMS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_button = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame_by_name("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10)

        self.budgets_button = ctk.CTkButton(self.sidebar_frame, text="Budgets", command=lambda: self.select_frame_by_name("budgets"))
        self.budgets_button.grid(row=2, column=0, padx=20, pady=10)

        self.savings_button = ctk.CTkButton(self.sidebar_frame, text="Savings", command=lambda: self.select_frame_by_name("savings"))
        self.savings_button.grid(row=3, column=0, padx=20, pady=10)

        # ---- Create Frames for each page ----
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.budgets_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.savings_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        self.setup_dashboard_ui()
        self.setup_budgets_ui()
        self.setup_savings_ui()

        # ---- Select initial frame ----
        self.select_frame_by_name("dashboard")

    def select_frame_by_name(self, name):
        # Set button colors
        self.dashboard_button.configure(fg_color= "#1f6aa5" if name == "dashboard" else "transparent")
        self.budgets_button.configure(fg_color="#1f6aa5" if name == "budgets" else "transparent")
        self.savings_button.configure(fg_color="#1f6aa5" if name == "savings" else "transparent")

        # Show the selected frame
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew"); self.update_dashboard()
        else: self.dashboard_frame.grid_forget()

        if name == "budgets":
            self.budgets_frame.grid(row=0, column=1, sticky="nsew"); self.update_budgets_view()
        else: self.budgets_frame.grid_forget()

        if name == "savings":
            self.savings_frame.grid(row=0, column=1, sticky="nsew"); self.update_savings_view()
        else: self.savings_frame.grid_forget()

    # --- DASHBOARD ---
    def setup_dashboard_ui(self):
        self.dashboard_frame.grid_columnconfigure(0, weight=1); self.dashboard_frame.grid_rowconfigure(2, weight=1)
        summary_frame = ctk.CTkFrame(self.dashboard_frame); summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10); summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.balance_label = ctk.CTkLabel(summary_frame, text="", font=ctk.CTkFont(size=18)); self.balance_label.grid(row=0, column=0, padx=10, pady=10)
        self.income_label = ctk.CTkLabel(summary_frame, text="", font=ctk.CTkFont(size=18)); self.income_label.grid(row=0, column=1, padx=10, pady=10)
        self.expense_label = ctk.CTkLabel(summary_frame, text="", font=ctk.CTkFont(size=18)); self.expense_label.grid(row=0, column=2, padx=10, pady=10)
        actions_frame = ctk.CTkFrame(self.dashboard_frame); actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0); actions_frame.grid_columnconfigure((0,1,2), weight=1)
        self.amount_entry = ctk.CTkEntry(actions_frame, placeholder_text="Amount"); self.amount_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.desc_entry = ctk.CTkEntry(actions_frame, placeholder_text="Description"); self.desc_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.category_combobox = ctk.CTkComboBox(actions_frame, values=[]); self.category_combobox.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        ctk.CTkButton(actions_frame, text="Add Income", command=self.add_income_action).grid(row=0, column=3, padx=5, pady=10)
        ctk.CTkButton(actions_frame, text="Add Expense", command=self.add_expense_action).grid(row=0, column=4, padx=(5, 10), pady=10)
        bottom_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent"); bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10); bottom_frame.grid_columnconfigure(0, weight=1); bottom_frame.grid_columnconfigure(1, weight=1); bottom_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame = ctk.CTkFrame(bottom_frame); self.chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.transactions_frame = ctk.CTkScrollableFrame(bottom_frame, label_text="Recent Transactions"); self.transactions_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

    def add_income_action(self): self.add_transaction("income")
    def add_expense_action(self): self.add_transaction("expense")

    def add_transaction(self, trans_type):
        amount_str = self.amount_entry.get(); description = self.desc_entry.get(); category = self.category_combobox.get()
        if not all([amount_str, description, category]): return
        try: amount = float(amount_str)
        except ValueError: return
        self.db.add_transaction(amount, trans_type, category, description)
        self.amount_entry.delete(0, "end"); self.desc_entry.delete(0, "end"); self.category_combobox.set("")
        self.update_dashboard()

    def update_dashboard(self):
        summary = self.db.get_summary()
        self.balance_label.configure(text=f"BALANCE\n{summary['balance']:,.0f} RWF"); self.income_label.configure(text=f"INCOME\n{summary['total_income']:,.0f} RWF"); self.expense_label.configure(text=f"EXPENSE\n{summary['total_expense']:,.0f} RWF")
        self.category_combobox.configure(values=self.db.get_categories())
        self.update_transactions_list(); self.update_pie_chart()

    def update_transactions_list(self):
        for widget in self.transactions_frame.winfo_children(): widget.destroy()
        transactions = self.db.get_transactions(limit=50)
        if not transactions: ctk.CTkLabel(self.transactions_frame, text="No transactions yet.").pack(pady=10)
        else:
            for trans in transactions:
                trans_frame = ctk.CTkFrame(self.transactions_frame); trans_frame.pack(fill="x", padx=5, pady=5); trans_frame.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(trans_frame, text=trans['transaction_date'].strftime("%b %d"), width=50).grid(row=0, column=0, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['description'], anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['category'], anchor="w", text_color="gray60").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                amount_text = f"{trans['amount']:,.0f} RWF"; amount_color = "#4CAF50" if trans['type'] == 'income' else "#F44336"
                ctk.CTkLabel(trans_frame, text=amount_text, text_color=amount_color, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").grid(row=0, column=3, padx=5, pady=5, sticky="e")

    def update_pie_chart(self):
        if self.chart_canvas: self.chart_canvas.get_tk_widget().destroy()
        fig = Figure(figsize=(5, 5), dpi=100, facecolor="#2B2B2B"); ax = fig.add_subplot(111)
        spending_data = self.db.get_spending_by_category()
        if not spending_data:
            ax.text(0.5, 0.5, "No expense data", ha='center', va='center', color="white"); ax.axis('off')
        else:
            labels = [item['category'] for item in spending_data]; sizes = [item['total'] for item in spending_data]
            ax.pie(sizes, labels=labels, autopct=lambda p: f'{p:.0f}%', startangle=140, textprops={'color':"w"}); ax.axis('equal')
        fig.tight_layout(); self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame); self.chart_canvas.draw(); self.chart_canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    # --- BUDGETS ---
    def setup_budgets_ui(self):
        self.budgets_frame.grid_columnconfigure(0, weight=1); self.budgets_frame.grid_rowconfigure(0, weight=1)
        self.budgets_scroll_frame = ctk.CTkScrollableFrame(self.budgets_frame, label_text="Monthly Budgets"); self.budgets_scroll_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew"); self.budgets_scroll_frame.grid_columnconfigure(0, weight=1)

    def update_budgets_view(self):
        for widget in self.budgets_scroll_frame.winfo_children(): widget.destroy()
        now = datetime.datetime.now(); budget_data = self.db.get_budgets_for_month(now.month, now.year)
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
        try:
            new_budget = float(entry_widget.get()); now = datetime.datetime.now()
            self.db.set_budget(category, new_budget, now.month, now.year); self.update_budgets_view()
        except (ValueError, TypeError): print(f"Invalid budget amount for {category}")

    # --- SAVINGS ---
    def setup_savings_ui(self):
        self.savings_frame.grid_columnconfigure(0, weight=1); self.savings_frame.grid_rowconfigure(1, weight=1)
        # Create Goal Form
        form_frame = ctk.CTkFrame(self.savings_frame); form_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(form_frame, text="Create New Savings Goal", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=(10,0), sticky="w")
        self.goal_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Goal Name"); self.goal_name_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.goal_target_entry = ctk.CTkEntry(form_frame, placeholder_text="Target Amount"); self.goal_target_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(form_frame, text="Create Goal", command=self.create_goal_action).grid(row=1, column=2, padx=10, pady=10)
        # Goals List
        self.savings_scroll_frame = ctk.CTkScrollableFrame(self.savings_frame, label_text="Your Goals"); self.savings_scroll_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")

    def create_goal_action(self):
        print("[DEBUG] create_goal_action called.")
        name = self.goal_name_entry.get()
        target_str = self.goal_target_entry.get()
        print(f"[DEBUG] Goal Name: '{name}', Target String: '{target_str}'")

        if not all([name, target_str]):
            print("[DEBUG] Failed: One or more fields are empty.")
            return
        
        try:
            target = float(target_str)
            print(f"[DEBUG] Target converted to float: {target}")
        except ValueError:
            print("[DEBUG] Failed: Could not convert target amount to a number.")
            return

        print("[DEBUG] Calling db.add_savings_goal...")
        self.db.add_savings_goal(name, target)
        print("[DEBUG] Database call complete.")
        
        self.goal_name_entry.delete(0, "end")
        self.goal_target_entry.delete(0, "end")
        
        print("[DEBUG] Refreshing savings view.")
        self.update_savings_view()

    def update_savings_view(self):
        for widget in self.savings_scroll_frame.winfo_children(): widget.destroy()
        goals = self.db.get_savings_goals()
        if not goals: ctk.CTkLabel(self.savings_scroll_frame, text="No savings goals yet. Create one above!").pack(pady=10)
        else:
            for goal in goals:
                goal_id = goal['id']; name = goal['name']; target = goal['target_amount']; current = goal['current_amount']
                progress = (current / target) if target > 0 else 0; progress = min(progress, 1.0)
                item_frame = ctk.CTkFrame(self.savings_scroll_frame); item_frame.pack(fill="x", expand=True, padx=10, pady=5); item_frame.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(item_frame, text=name, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                progress_bar = ctk.CTkProgressBar(item_frame, orientation="horizontal"); progress_bar.set(progress); progress_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
                ctk.CTkLabel(item_frame, text=f"{current:,.0f} / {target:,.0f} RWF").grid(row=0, column=1, padx=10, pady=5, sticky="e")
                add_funds_entry = ctk.CTkEntry(item_frame, placeholder_text="Add Funds"); add_funds_entry.grid(row=0, column=2, padx=10, pady=5)
                ctk.CTkButton(item_frame, text="Add", width=50, command=lambda g_id=goal_id, g_name=name, e=add_funds_entry: self.add_funds_action(g_id, g_name, e)).grid(row=0, column=3, padx=10, pady=5)

    def add_funds_action(self, goal_id, goal_name, entry_widget):
        try:
            amount = float(entry_widget.get())
            if amount <= 0: return
            self.db.add_to_savings_goal(goal_id, goal_name, amount); self.update_savings_view()
        except (ValueError, TypeError): print(f"Invalid amount for {goal_name}")