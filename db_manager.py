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
        SELECT t.transaction_date, t.amount, t.type, c.name as category, t.description
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        ORDER BY t.transaction_date DESC, t.id DESC
        LIMIT %s
        """
        return self.execute_query(query, (limit,), fetch=True)

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
