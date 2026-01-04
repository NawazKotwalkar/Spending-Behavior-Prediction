import streamlit as st
import pandas as pd
import os
from scripts.csv_parser import parse_csv
from utils.auth_db import get_logged_in_user, get_db_connection

def show():
    st.title("📤 Upload Files")
    os.makedirs("data", exist_ok=True)
    current_user = get_logged_in_user()
    # -------------------- ENSURE USER EXISTS --------------------
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=%s", (current_user,))
        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO users (username, first_name, last_name, contact, email, password_, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (current_user, current_user, current_user, '9999999999',
                 f'{current_user}@example.com', 'password', 'user')
            )
            conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"❌ Failed to ensure user exists: {e}")
        return

    # -------------------- TRANSACTION UPLOAD --------------------
    st.markdown("### 🏦 Upload Bank Statement (.csv only)")
    uploaded_file = st.file_uploader("Choose Transaction File", type=["csv"], key="bank_upload")

    if "transaction_file" in st.session_state and os.path.exists(st.session_state["transaction_file"]):
        st.markdown(f'<div class="custom-alert-success">✅ Using: <code>{os.path.basename(st.session_state["transaction_file"])}</code></div>', unsafe_allow_html=True)

    if uploaded_file:
        path = os.path.join("data", uploaded_file.name)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state["transaction_file"] = path

        try:
            df = parse_csv(path)
            st.markdown(f'<div class="custom-alert-success">✅ Transaction file parsed successfully.</div>', unsafe_allow_html=True)
            
            # Insert into MySQL
            conn = get_db_connection()
            cursor = conn.cursor()
            inserted = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        "INSERT INTO transactions (username, date, category, description, amount) VALUES (%s, %s, %s, %s, %s)",
                        (current_user, row['date'], row.get('category', 'Misc'), row['description'], float(row['amount']))
                    )
                    inserted += 1
                except Exception as e:
                    st.markdown(
                        f"""<div class="custom-alert-warning">
                        ⚠️ Skipped a transaction row.
                        </div>""",
                        unsafe_allow_html=True
                    )
            conn.commit()
            conn.close()
            st.markdown(f'<div class="custom-alert-success">✅ {inserted} transactions stored for {current_user}.</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Failed to parse or insert transaction file: {e}")

    st.markdown("---")

    # -------------------- BUDGET UPLOAD --------------------
    st.markdown("### 📊 Upload Budget File (with 'category' and 'budget')")
    budget_file = st.file_uploader("Choose Budget File", type=["csv"], key="budget_upload")

    if "budget_file" in st.session_state and os.path.exists(st.session_state["budget_file"]):
        st.markdown(f'<div class="custom-alert-success">✅ Using: <code>{os.path.basename(st.session_state["budget_file"])}</code></div>', unsafe_allow_html=True)

    if budget_file:
        path = os.path.join("data", budget_file.name)
        with open(path, "wb") as f:
            f.write(budget_file.getbuffer())
        st.session_state["budget_file"] = path
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()
        st.session_state["budget_df"] = df

        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip().str.lower()

            if {"category", "budget"}.issubset(df.columns):
                st.markdown(f'<div class="custom-alert-success">✅ Budget file parsed successfully.</div>', unsafe_allow_html=True)

                conn = get_db_connection()
                cursor = conn.cursor()
                current_month = pd.Timestamp.now().strftime("%Y-%m")
                inserted = 0
                for _, row in df.iterrows():
                    try:
                        cursor.execute(
                            """
                            INSERT INTO budgets (username, month, category, budget_amount)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount)
                            """,
                            (current_user, current_month, row['category'], float(row['budget']))
                        )
                        inserted += 1
                    except Exception as e:
                        st.markdown(f""" <div class="custom-alert-warning">f"⚠️ Skipped budget row due to error: {e} </div>""", unsafe_allow_html=True)
                conn.commit()
                conn.close()
                st.markdown(f'<div class="custom-alert-success">f"✅ {inserted} budget items stored in MySQL for {current_user} ({current_month}).</div>', unsafe_allow_html=True)
            else:
                st.error("❌ Budget CSV must contain 'category' and 'budget' columns.")
        except Exception as e:
            st.error(f"❌ Failed to parse or insert budget file: {e}")
