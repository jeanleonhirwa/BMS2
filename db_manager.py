import pymysql
from pymysql import Error
import datetime

class DBManager:
    def __init__(self, host='localhost', user='root', password='', database='bms_db'):
        """Initialize the database connection."""
        try:
            self.conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor # Return rows as dictionaries
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.conn = None

    def execute_query(self, query, params=None, fetch=False):
        """Execute a generic query."""
        if not self.conn:
            return None
        try:
            self.cursor.execute(query, params or ())
            if fetch:
                result = self.cursor.fetchall()
                return result
            else:
                self.conn.commit()
                return self.cursor.lastrowid
        except Error as e:
            print(f"Query failed: {e}")
            return None

    def get_category_id_by_name(self, category_name):
        """Finds a category's ID by its name."""
        query = "SELECT id FROM categories WHERE name = %s"
        result = self.execute_query(query, (category_name,), fetch=True)
        return result[0]['id'] if result else None

    def add_transaction(self, amount, trans_type, category_name, description, date=None):
        """Adds a new transaction to the database."""
        if date is None:
            date = datetime.date.today()
        
        category_id = self.get_category_id_by_name(category_name)
        if category_id is None:
            print(f"Category '{category_name}' not found.")
            return None

        query = """
        INSERT INTO transactions (transaction_date, amount, type, category_id, description)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (date, amount, trans_type, category_id, description)
        return self.execute_query(query, params)

    def get_transactions(self, limit=20):
        """Fetches recent transactions, joining with categories."""
        query = """
        SELECT t.id, t.transaction_date, t.amount, t.type, c.name as category, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.transaction_date DESC, t.id DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,), fetch=True)

    def search_transactions(self, description=None, category=None, trans_type=None, start_date=None, end_date=None):
        """Searches for transactions based on a set of optional criteria."""
        query_base = """
        SELECT t.id, t.transaction_date, t.amount, t.type, c.name as category, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        """
        conditions = []
        params = []

        if description:
            conditions.append("t.description LIKE %s")
            params.append(f"%{description}%")
        if category:
            conditions.append("c.name = %s")
            params.append(category)
        if trans_type:
            conditions.append("t.type = %s")
            params.append(trans_type)
        if start_date:
            conditions.append("t.transaction_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("t.transaction_date <= %s")
            params.append(end_date)

        if conditions:
            query = query_base + " WHERE " + " AND ".join(conditions)
        else:
            query = query_base
        
        query += " ORDER BY t.transaction_date DESC, t.id DESC"

        return self.execute_query(query, tuple(params), fetch=True)

    def get_monthly_summary(self):
        """Calculates total income and expense for the last 12 months."""
        query = """
        SELECT
            YEAR(transaction_date) as year,
            MONTH(transaction_date) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM transactions
        WHERE transaction_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY YEAR(transaction_date), MONTH(transaction_date)
        ORDER BY year, month;
        """
        return self.execute_query(query, fetch=True)

    def get_transaction_by_id(self, transaction_id):
        """Fetches a single transaction by its ID."""
        query = """
        SELECT t.id, t.transaction_date, t.amount, t.type, c.name as category, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.id = %s
        """
        result = self.execute_query(query, (transaction_id,), fetch=True)
        return result[0] if result else None

    def update_transaction(self, transaction_id, date, amount, trans_type, category_name, description):
        """Updates an existing transaction."""
        category_id = self.get_category_id_by_name(category_name)
        if category_id is None: return None
        query = """
        UPDATE transactions
        SET transaction_date = %s, amount = %s, type = %s, category_id = %s, description = %s
        WHERE id = %s
        """
        params = (date, amount, trans_type, category_id, description, transaction_id)
        return self.execute_query(query, params)

    def delete_transaction(self, transaction_id):
        """Deletes a transaction by its ID."""
        # Also need to handle the impact on savings goals if it was a contribution
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction and transaction['category'] == 'Savings':
            # This is a simple approach; a more complex app might link transactions to goals directly
            # For now, we alert the user that manual adjustment of goals might be needed
            pass # In a real app, you might reverse the goal contribution here.

        query = "DELETE FROM transactions WHERE id = %s"
        return self.execute_query(query, (transaction_id,))

    def get_categories(self):
        """Fetches all category names."""
        query = "SELECT name FROM categories ORDER BY name ASC"
        results = self.execute_query(query, fetch=True)
        return [row['name'] for row in results] if results else []

    def get_summary(self):
        """Calculates total income, expenses, and current balance."""
        query_income = "SELECT SUM(amount) as total FROM transactions WHERE type = 'income'"
        query_expense = "SELECT SUM(amount) as total FROM transactions WHERE type = 'expense'"
        
        total_income_result = self.execute_query(query_income, fetch=True)
        total_expense_result = self.execute_query(query_expense, fetch=True)

        total_income = total_income_result[0]['total'] or 0
        total_expense = total_expense_result[0]['total'] or 0
        balance = total_income - total_expense

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        }

    def get_spending_by_category(self):
        """Calculates total spending for each category."""
        query = """
        SELECT c.name as category, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type = 'expense'
        GROUP BY c.name
        HAVING total > 0
        ORDER BY total DESC
        """
        return self.execute_query(query, fetch=True)

    def set_budget(self, category_name, amount, month, year):
        """Sets or updates the budget for a given category, month, and year."""
        category_id = self.get_category_id_by_name(category_name)
        if not category_id:
            return None
        
        query = """
        INSERT INTO budgets (category_id, amount, month, year)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount)
        """
        params = (category_id, amount, month, year)
        return self.execute_query(query, params)

    def get_budgets_for_month(self, month, year):
        """Retrieves each category's budget and actual spending for a given month."""
        query = """
        SELECT 
            c.name AS category,
            COALESCE(b.amount, 0) AS budget_amount,
            COALESCE(spent.total_spent, 0) AS spent_amount
        FROM categories c
        LEFT JOIN budgets b ON c.id = b.category_id AND b.month = %s AND b.year = %s
        LEFT JOIN (
            SELECT category_id, SUM(amount) AS total_spent
            FROM transactions
            WHERE type = 'expense' AND MONTH(transaction_date) = %s AND YEAR(transaction_date) = %s
            GROUP BY category_id
        ) AS spent ON c.id = spent.category_id
        WHERE c.name NOT IN ('Parental Allowance', 'Savings') -- Exclude income categories
        ORDER BY c.name;
        """
        params = (month, year, month, year)
        return self.execute_query(query, params, fetch=True)

    def add_savings_goal(self, name, target_amount):
        """Adds a new savings goal."""
        query = "INSERT INTO savings_goals (name, target_amount) VALUES (%s, %s)"
        return self.execute_query(query, (name, target_amount))

    def get_savings_goals(self):
        """Retrieves all savings goals."""
        query = "SELECT * FROM savings_goals ORDER BY name"
        return self.execute_query(query, fetch=True)

    def add_to_savings_goal(self, goal_id, goal_name, amount):
        """Adds funds to a savings goal and creates a corresponding transaction."""
        # First, create the expense transaction
        self.add_transaction(amount, 'expense', 'Savings', f"Contribution to {goal_name}")
        
        # Second, update the goal's current amount
        query = "UPDATE savings_goals SET current_amount = current_amount + %s WHERE id = %s"
        return self.execute_query(query, (amount, goal_id))

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

# Example of how to use it (for testing)
if __name__ == '__main__':
    db = DBManager()
    if db.conn:
        # Add a test transaction
        # db.add_transaction(1000, 'income', 'Parental Allowance', 'Monthly allowance')
        # db.add_transaction(50, 'expense', 'Canteen/Food', 'Lunch')

        # Fetch and print summary
        summary = db.get_summary()
        print(f"Balance: {summary['balance']:.2f}")

        # Fetch and print transactions
        transactions = db.get_transactions()
        print("\n--- Recent Transactions ---")
        for t in transactions:
            print(f"{t['transaction_date']}: {t['description']} ({t['category']}) - {t['amount']:.2f} [{t['type']}]")
        
        db.close()
