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
        if "amount" not in df.columns:
            raise ValueError("CSV must contain an 'amount' column")

        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.strip()
        )

        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

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