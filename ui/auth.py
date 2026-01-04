import streamlit as st
import string
import re
from utils.auth_db import create_user, validate_login 

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_contact(contact):
    return re.match(r"^\d{10}$", contact)

def is_strong_password(pw):
    return (
        len(pw) >= 8 and
        any(c.isdigit() for c in pw) and
        any(c in string.punctuation for c in pw)
    )

def auth_ui():
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    if st.session_state.auth_mode == "login":
        st.title("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            is_valid, name, role = validate_login(username, password)
            if is_valid:
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.session_state["name"] = name
                st.session_state["role"] = role
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

        st.markdown("---")
        if st.button("📝 Don't have an account? Sign Up"):
            st.session_state.auth_mode = "signup"
            st.rerun()

    elif st.session_state.auth_mode == "signup":
        st.title("🆕 Create Account")

        username = st.text_input("Username")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        contact = st.text_input("Mobile Number")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if not all([username, first_name, last_name, contact, email, password]):
                st.error("⚠️ All fields are required.")
            elif not is_valid_email(email):
                st.error("📧 Invalid email format.")
            elif not is_valid_contact(contact):
                st.error("📱 Mobile number must be 10 digits.")
            elif password != confirm_password:
                st.error("🚫 Passwords do not match.")
            elif not is_strong_password(password):
                st.markdown(f""" <div class="custom-alert-warning">"🔐 Password must be 8+ chars, with digits & special chars.</div>""", unsafe_allow_html=True)
            else:
                result = create_user(
                    username,
                    first_name,
                    last_name,
                    contact,
                    email,
                    password  
                )
                if result == "success":
                    st.markdown(f'<div class="custom-alert-success">"✅ Account created! Please login.</div>', unsafe_allow_html=True)
                    st.session_state.auth_mode = "login"
                    st.rerun()
                elif result == "exists":
                    st.error("😕 Username or email already exists.")
                elif result == "invalid":
                    st.error("🚫 Invalid email or phone number.")

        st.markdown("---")
        if st.button("🔙 Already have an account? Login"):
            st.session_state.auth_mode = "login"

            st.rerun()
