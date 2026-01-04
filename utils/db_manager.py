import mysql.connector
from typing import List, Optional, Dict
from datetime import datetime
import streamlit as st
import pandas as pd
from utils.auth_db import get_db_connection

# ---------------------- USERS ----------------------
def create_user(username, first, last, contact, email, password, role="user") -> str:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    if cursor.fetchone():
        conn.close()
        return "exists"

    try:
        cursor.execute(
            "INSERT INTO users (username, first_name, last_name, contact, email, password_hash, role) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, first, last, contact, email, password, role)
        )
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        print("Error creating user:", e)
        conn.close()
        return "invalid"

def validate_login(username, password) -> (bool, Optional[str], Optional[str]):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password_hash=%s", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        full_name = f"{user['first_name']} {user['last_name']}"
        return True, full_name, user.get("role", "user")
    return False, None, None

def get_all_users() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, first_name, last_name, email, contact, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(username: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    conn.commit()
    conn.close()

# ---------------------- TRANSACTIONS ----------------------
def add_transaction(user_id: int, date, category, desc, amount) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, date, category, description, amount) VALUES (%s, %s, %s, %s, %s)",
        (user_id, date, category, desc, float(amount))
    )
    conn.commit()
    conn.close()

def get_user_transactions(user_id: int) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions WHERE user_id=%s", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_transactions() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------------- BUDGETS ----------------------
def set_budget(user_id: int, month: str, category: str, amount: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    # upsert budget
    cursor.execute(
        "SELECT * FROM budgets WHERE user_id=%s AND month=%s AND category=%s",
        (user_id, month, category)
    )
    if cursor.fetchone():
        cursor.execute(
            "UPDATE budgets SET budget_amount=%s WHERE user_id=%s AND month=%s AND category=%s",
            (amount, user_id, month, category)
        )
    else:
        cursor.execute(
            "INSERT INTO budgets (user_id, month, category, budget_amount) VALUES (%s, %s, %s, %s)",
            (user_id, month, category, amount)
        )
    conn.commit()
    conn.close()

def get_budget(user_id: int, month: str) -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT category, budget_amount FROM budgets WHERE user_id=%s AND month=%s", (user_id, month))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_budgets() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM budgets")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ---------------------- REPORTS / ANALYTICS ----------------------
def get_overspending_data() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch total spent per user/category/month
    cursor.execute("""
        SELECT t.user_id, b.month, t.category, SUM(t.amount) AS total_spent, b.budget_amount
        FROM transactions t
        JOIN budgets b ON t.user_id=b.user_id AND t.category=b.category AND b.month=DATE_FORMAT(t.date, '%Y-%m')
        GROUP BY t.user_id, t.category, b.month
        HAVING total_spent > b.budget_amount
        ORDER BY b.month DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    # Add Overspending field
    for r in rows:
        r["Overspending"] = r["total_spent"] - r["budget_amount"]
    return rows

# ---------------------- CATEGORIES ----------------------
def add_category(name: str, color: str = "#FF0000"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM categories WHERE name=%s", (name,)
    )
    if cursor.fetchone():
        cursor.execute(
            "UPDATE categories SET color=%s WHERE name=%s", (color, name)
        )
    else:
        cursor.execute(
            "INSERT INTO categories (name, color) VALUES (%s, %s)", (name, color)
        )
    conn.commit()
    conn.close()

def get_categories() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM categories")
    rows = cursor.fetchall()
    conn.close()
    return [r["name"] for r in rows]
