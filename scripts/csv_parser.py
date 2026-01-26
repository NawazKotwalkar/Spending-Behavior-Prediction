import pandas as pd
import difflib


def match_column(possible_names, df_columns, cutoff=0.6):
    for name in possible_names:
        match = difflib.get_close_matches(
            name.lower(), df_columns, n=1, cutoff=cutoff
        )
        if match:
            return match[0]
    return None


def parse_csv(file_path: str) -> pd.DataFrame:
    """
    Robust CSV parser for bank statements.

    Guarantees canonical columns:
    - date        (datetime)
    - amount      (POSITIVE ONLY)
    - description (string)
    - category    (string)

    NOTE:
    - Does NOT generate 'month'
    - Month must be derived later (visualize.py)
    """

    try:
        df = pd.read_csv(file_path).copy()

        # ---------------- NORMALIZE COLUMNS ----------------
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        columns = df.columns.tolist()

        # ---------------- DATE ----------------
        date_col = match_column(
            ["date", "transaction_date", "txn_date", "timestamp", "value_date"],
            columns,
        )
        if not date_col:
            raise ValueError("❌ Could not detect a date column.")

        df["date"] = pd.to_datetime(df[date_col], errors="coerce")

        # ---------------- AMOUNT ----------------
        withdrawal_col = match_column(
            ["withdrawal", "debit", "withdrawal_amt", "dr_amount"],
            columns,
        )
        deposit_col = match_column(
            ["deposit", "credit", "deposit_amt", "cr_amount"],
            columns,
        )

        if withdrawal_col and deposit_col:
            amount = (
                pd.to_numeric(df[deposit_col], errors="coerce").fillna(0)
                - pd.to_numeric(df[withdrawal_col], errors="coerce").fillna(0)
            )
        elif withdrawal_col:
            amount = -pd.to_numeric(df[withdrawal_col], errors="coerce")
        elif deposit_col:
            amount = pd.to_numeric(df[deposit_col], errors="coerce")
        else:
            amount_col = match_column(
                ["amount", "transaction_amount", "amt", "value"],
                columns,
            )
            if not amount_col:
                raise ValueError("❌ Could not detect an amount column.")
            amount = pd.to_numeric(df[amount_col], errors="coerce")

        # ✅ FORCE POSITIVE AMOUNT (FINAL RULE)
        df["amount"] = amount.abs()

        # ---------------- DESCRIPTION ----------------
        desc_col = match_column(
            ["description", "narration", "details", "remarks", "transaction_details"],
            columns,
        )

        df["description"] = (
            df[desc_col].astype(str) if desc_col else "no description"
        )

        # ---------------- CATEGORY ----------------
        if "category" not in df.columns:
            df["category"] = "uncategorized"

        df["category"] = (
            df["category"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # ---------------- CLEAN ----------------
        df = df.dropna(subset=["date", "amount"]).reset_index(drop=True)

        if df.empty:
            raise ValueError("❌ No valid rows after parsing.")

        return df

    except Exception as e:
        raise Exception(f"CSV parsing failed: {e}")