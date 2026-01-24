import streamlit as st
import pandas as pd
import os
import uuid
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
                (
                    current_user,
                    current_user,
                    current_user,
                    "9999999999",
                    f"{current_user}@example.com",
                    "password",
                    "user",
                ),
            )
            conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"❌ Failed to ensure user exists: {e}")
        return

    # -------------------- TRANSACTION UPLOAD --------------------
    st.markdown("### 🏦 Upload Bank Statement (.csv only)")
    uploaded_file = st.file_uploader(
        "Choose Transaction File", type=["csv"], key="bank_upload"
    )

    if uploaded_file:
        # 🔒 Safe unique filename
        filename = f"transactions_{uuid.uuid4().hex}.csv"
        path = os.path.join("data", filename)

        try:
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        except PermissionError:
            st.error("❌ Please close the CSV file if it is open and try again.")
            return

        st.session_state["transaction_file"] = path

        try:
            df = parse_csv(path)

            # ---- REQUIRED DERIVED COLUMNS ----
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date", "amount"])

            df["month"] = df["date"].dt.to_period("M").astype(str)
            df["spend"] = -df["amount"]

            # ---- STORE CANONICAL DATAFRAME ----
            st.session_state["df"] = df

            st.success("✅ Transaction file uploaded and parsed successfully.")

            # ---- INSERT INTO DATABASE ----
            conn = get_db_connection()
            cursor = conn.cursor()

            inserted = 0
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT INTO transactions (username, date, category, description, amount)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            current_user,
                            row["date"],
                            row.get("category", "misc"),
                            row["description"],
                            float(row["amount"]),
                        ),
                    )
                    inserted += 1
                except Exception:
                    pass

            conn.commit()
            conn.close()

            st.info(f"📥 {inserted} transactions stored for {current_user}")

        except Exception as e:
            st.error(f"❌ Failed to parse transaction file: {e}")
            return

    st.markdown("---")

    # -------------------- BUDGET UPLOAD --------------------
    st.markdown("### 📊 Upload Budget File (category, budget)")
    budget_file = st.file_uploader("Choose Budget File", type=["csv"], key="budget_upload")

    if budget_file:
        filename = f"budget_{uuid.uuid4().hex}.csv"
        path = os.path.join("data", filename)

        with open(path, "wb") as f:
            f.write(budget_file.getbuffer())

        df_budget = pd.read_csv(path)
        df_budget.columns = df_budget.columns.str.strip().str.lower()

        if not {"category", "budget"}.issubset(df_budget.columns):
            st.error("❌ Budget CSV must contain 'category' and 'budget' columns.")
            return

        st.session_state["budget_df"] = df_budget

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            current_month = pd.Timestamp.now().strftime("%Y-%m")
            inserted = 0

            for _, row in df_budget.iterrows():
                cursor.execute(
                    """
                    INSERT INTO budgets (username, month, category, budget_amount)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE budget_amount = VALUES(budget_amount)
                    """,
                    (
                        current_user,
                        current_month,
                        row["category"],
                        float(row["budget"]),
                    ),
                )
                inserted += 1

            conn.commit()
            conn.close()

            st.success(f"✅ {inserted} budget items saved for {current_user}")

        except Exception as e:
            st.error(f"❌ Failed to store budget data: {e}")
