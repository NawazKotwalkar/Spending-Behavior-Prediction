import re
import streamlit as st
import mysql.connector
import os
# ---------------------- CONNECTION ----------------------
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=os.getenv("DB_SSL_CA")
    )
    return conn

# ---------------------- VALIDATORS ----------------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_contact(contact):
    return re.match(r"^\d{10}$", contact)

# ---------------------- USERS ----------------------
def create_user(username, first_name, last_name, contact, email, password, role="user"):
    if not is_valid_email(email) or not is_valid_contact(contact):
        return "invalid"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if username or email already exists
    cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
    if cursor.fetchone():
        conn.close()
        return "exists"

    try:
        cursor.execute(
            "INSERT INTO users (username, first_name, last_name, contact, email, password_, role) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, first_name, last_name, contact, email, password, role)
        )
        conn.commit()
        conn.close()
        return "success"
    except Exception as e:
        print("Error creating user:", e)
        conn.close()
        return "invalid"

def validate_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password_=%s",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        return True, f"{user['first_name']} {user['last_name']}", user.get("role", "user")
    return False, None, None

# ---------------------- SESSION HELPERS ----------------------
def is_logged_in():
    return st.session_state.get("logged_in", False)

def get_logged_in_user():
    return st.session_state.get("name", "Guest")

def get_user_role():
    return st.session_state.get("role", "user")

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, first_name, last_name, email, contact, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users