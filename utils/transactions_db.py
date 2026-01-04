import mysql.connector
from datetime import datetime

# ---------------------- CONNECTION ----------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="62929",
        database="finance_tracker"
    )
    return conn

# ---------------------- TRANSACTIONS ----------------------
def add_transaction(username, date, category, description, amount):
    """Insert a new transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (username, date, category, description, amount) "
            "VALUES (%s, %s, %s, %s, %s)",
            (username, date, category, description, amount)
        )
        conn.commit()
    except Exception as e:
        print("Error inserting transaction:", e)
    finally:
        conn.close()

def get_transactions(username, start_date=None, end_date=None, category=None):
    """Fetch transactions with optional filters."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM transactions WHERE username = %s"
    params = [username]

    if start_date and end_date:
        query += " AND date BETWEEN %s AND %s"
        params.extend([start_date, end_date])
    if category:
        query += " AND category = %s"
        params.append(category)

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_transaction(txn_id, username):
    """Delete a transaction by ID (for the logged-in user)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=%s AND username=%s", (txn_id, username))
    conn.commit()
    conn.close()

def get_monthly_summary(username):
    """Aggregate spending by category and month."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT DATE_FORMAT(date, '%Y-%m') AS month, category, SUM(amount) AS total_spent
        FROM transactions
        WHERE username = %s
        GROUP BY DATE_FORMAT(date, '%Y-%m'), category
        ORDER BY month DESC
        """,
        (username,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
