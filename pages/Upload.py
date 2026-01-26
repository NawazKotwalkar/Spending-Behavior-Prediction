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
        cursor.execute(
            "SELECT username FROM users WHERE username=%s",
            (current_user,)
        )

        if not cursor.fetchone():
            cursor.execute(
                """
                INSERT INTO users
                (username, first_name, last_name, contact, email, password_, role)
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
        "Choose Transaction File",
        type=["csv"],
        key="bank_upload",
    )

    if uploaded_file is not None:
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
            # ---- PARSE CSV ----
            df = parse_csv(path)

            # ---- CANONICAL CLEANUP ----
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date", "amount"])

            # ❌ DO NOT CREATE month HERE
            # ❌ DO NOT CREATE spend COLUMN

            # ---- STORE IN SESSION STATE ----
            st.session_state["df"] = df

            st.success(f"✅ Loaded {len(df)} transactions successfully.")

            # ---- INSERT INTO DATABASE ----
            conn = get_db_connection()
            cursor = conn.cursor()

            records = [
                (
                    current_user,
                    row["date"],
                    row.get("category", "uncategorized"),
                    row["description"],
                    float(row["amount"]),
                )
                for _, row in df.iterrows()
            ]

            cursor.executemany(
                """
                INSERT INTO transactions
                (username, date, category, description, amount)
                VALUES (%s, %s, %s, %s, %s)
                """,
                records,
            )

            conn.commit()
            inserted = cursor.rowcount
            conn.close()

            st.info(f"📥 {inserted} transactions stored for {current_user}")

        except Exception as e:
            st.error(f"❌ Failed to parse transaction file: {e}")
            return

    st.markdown("---")

    # -------------------- BUDGET UPLOAD --------------------
    st.markdown("### 📊 Upload Budget File (category, budget)")
    budget_file = st.file_uploader(
        "Choose Budget File",
        type=["csv"],
        key="budget_upload",
    )

    if budget_file is not None:
        filename = f"budget_{uuid.uuid4().hex}.csv"
        path = os.path.join("data", filename)

        with open(path, "wb") as f:
            f.write(budget_file.getbuffer())

        df_budget = pd.read_csv(path)
        df_budget.columns = df_budget.columns.str.strip().str.lower()

        if not {"category", "budget"}.issubset(df_budget.columns):
            st.error("❌ Budget CSV must contain exactly: category, budget")
            return

        # ---- NORMALIZE CATEGORY ----
        df_budget["category"] = (
            df_budget["category"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # ---- STORE FOR CHARTS ----
        st.session_state["budget_df"] = df_budget

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            current_month = st.session_state["df"]["date"].dt.strftime("%Y-%m").mode()[0]

            records = [
                (
                    current_user,
                    current_month,
                    row["category"],
                    float(row["budget"]),
                )
                for _, row in df_budget.iterrows()
            ]

            cursor.executemany(
                """
                INSERT INTO budgets
                (username, month, category, budget_amount)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    budget_amount = VALUES(budget_amount)
                """,
                records,
            )

            conn.commit()
            conn.close()

            st.success(f"✅ {cursor.rowcount} budget items saved")

        except Exception as e:
            st.error(f"❌ Failed to store budget data: {e}")
