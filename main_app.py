import customtkinter as ctk
from db_manager import DBManager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

        # ---- Sidebar ----
        self.sidebar_frame = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BMS", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # ---- Main Content Area ----
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # ---- Top Frame: Summary Metrics ----
        self.summary_frame = ctk.CTkFrame(self.main_frame)
        self.summary_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.balance_label = ctk.CTkLabel(self.summary_frame, text="BALANCE\n--.--", font=ctk.CTkFont(size=18))
        self.balance_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.income_label = ctk.CTkLabel(self.summary_frame, text="INCOME\n--.--", font=ctk.CTkFont(size=18))
        self.income_label.grid(row=0, column=1, padx=10, pady=10)

        self.expense_label = ctk.CTkLabel(self.summary_frame, text="EXPENSE\n--.--", font=ctk.CTkFont(size=18))
        self.expense_label.grid(row=0, column=2, padx=10, pady=10)

        # ---- Middle Frame: Quick Actions ----
        self.actions_frame = ctk.CTkFrame(self.main_frame)
        self.actions_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
        self.actions_frame.grid_columnconfigure((0,1,2), weight=1)
        self.actions_frame.grid_columnconfigure((3,4), weight=0)

        self.amount_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Amount")
        self.amount_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.desc_entry = ctk.CTkEntry(self.actions_frame, placeholder_text="Description")
        self.desc_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.category_combobox = ctk.CTkComboBox(self.actions_frame, values=[])
        self.category_combobox.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        self.add_income_button = ctk.CTkButton(self.actions_frame, text="Add Income", command=self.add_income_action)
        self.add_income_button.grid(row=0, column=3, padx=5, pady=10)

        self.add_expense_button = ctk.CTkButton(self.actions_frame, text="Add Expense", command=self.add_expense_action)
        self.add_expense_button.grid(row=0, column=4, padx=(5, 10), pady=10)

        # ---- Bottom Content Area (Chart and Transactions) ----
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        self.chart_frame = ctk.CTkFrame(self.bottom_frame)
        self.chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.transactions_frame = ctk.CTkScrollableFrame(self.bottom_frame, label_text="Recent Transactions")
        self.transactions_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # ---- Initial Data Load ----
        self.update_dashboard()

    def add_income_action(self): self.add_transaction("income")
    def add_expense_action(self): self.add_transaction("expense")

    def add_transaction(self, trans_type):
        amount_str = self.amount_entry.get()
        description = self.desc_entry.get()
        category = self.category_combobox.get()

        if not all([amount_str, description, category]):
            print("Error: All fields are required.")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            print("Error: Amount must be a number.")
            return

        self.db.add_transaction(amount, trans_type, category, description)
        self.amount_entry.delete(0, "end")
        self.desc_entry.delete(0, "end")
        self.category_combobox.set("")
        self.update_dashboard()

    def update_dashboard(self):
        # ---- Update Summary ----
        summary = self.db.get_summary()
        self.balance_label.configure(text=f"BALANCE\n{summary['balance']:,.0f} RWF")
        self.income_label.configure(text=f"INCOME\n{summary['total_income']:,.0f} RWF")
        self.expense_label.configure(text=f"EXPENSE\n{summary['total_expense']:,.0f} RWF")

        # ---- Update Categories ----
        self.category_combobox.configure(values=self.db.get_categories())

        # ---- Update Recent Transactions ----
        for widget in self.transactions_frame.winfo_children(): widget.destroy()
        transactions = self.db.get_transactions(limit=50)
        if not transactions:
            ctk.CTkLabel(self.transactions_frame, text="No transactions yet.").pack(pady=10)
        else:
            for trans in transactions:
                trans_frame = ctk.CTkFrame(self.transactions_frame)
                trans_frame.pack(fill="x", padx=5, pady=5)
                trans_frame.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(trans_frame, text=trans['transaction_date'].strftime("%b %d"), width=50).grid(row=0, column=0, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['description'], anchor="w").grid(row=0, column=1, padx=5, pady=5, sticky="w")
                ctk.CTkLabel(trans_frame, text=trans['category'], anchor="w", text_color="gray60").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                amount_text = f"{trans['amount']:,.0f} RWF"
                amount_color = "#4CAF50" if trans['type'] == 'income' else "#F44336"
                ctk.CTkLabel(trans_frame, text=amount_text, text_color=amount_color, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        
        # ---- Update Pie Chart ----
        self.update_pie_chart()

    def update_pie_chart(self):
        spending_data = self.db.get_spending_by_category()
        
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        bg_color = self.chart_frame.cget("fg_color")[1] # Get the dark theme color
        
        fig = Figure(figsize=(5, 5), dpi=100, facecolor=bg_color)
        ax = fig.add_subplot(111)
        
        if not spending_data:
            ax.text(0.5, 0.5, "No expense data to display", ha='center', va='center', color="white")
            ax.axis('off')
        else:
            labels = [item['category'] for item in spending_data]
            sizes = [item['total'] for item in spending_data]
            
            ax.pie(sizes, labels=labels, autopct=lambda p: f'{p:,.0f}%', startangle=140, textprops={'color':"w"})
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a planet.
            fig.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)