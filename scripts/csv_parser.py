import pandas as pd
import difflib

def match_column(possible_names, df_columns, cutoff=0.6):
    for name in possible_names:
        match = difflib.get_close_matches(name.lower(), df_columns, n=1, cutoff=cutoff)
        if match:
            return match[0]
    return None

def parse_csv(file_path: str) -> pd.DataFrame:
    """Smart CSV parser that handles generic bank formats with credit/debit columns."""
    try:
        df = pd.read_csv(file_path)
        df = df.copy()
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        col_list = df.columns.tolist()

        print(f"✅ Parsed CSV Columns: {col_list}")

        # Date
        date_col = match_column(['date', 'transaction_date', 'timestamp', 'txn_date', 'value_date'], col_list)

        # Amount handling
        withdrawal_col = match_column(['withdrawal', 'withdrawal_amt', 'withdraw'], col_list)
        deposit_col = match_column(['deposit', 'deposit_amt', 'credit'], col_list)

        if withdrawal_col and deposit_col:
            df['amount'] = (
                pd.to_numeric(df[deposit_col], errors='coerce').fillna(0) -
                pd.to_numeric(df[withdrawal_col], errors='coerce').fillna(0)
            )
        elif withdrawal_col:
            df['amount'] = -pd.to_numeric(df[withdrawal_col], errors='coerce')
        elif deposit_col:
            df['amount'] = pd.to_numeric(df[deposit_col], errors='coerce')
        else:
            amount_col = match_column(['amount', 'transaction_amount', 'amt', 'value'], col_list)
            if amount_col:
                df['amount'] = pd.to_numeric(df[amount_col], errors='coerce')
            else:
                raise ValueError("❌ Could not infer the transaction amount column.")

        # Description
        desc_col = match_column(['description', 'narration', 'details', 'remarks', 'transaction_details'], col_list)
        if desc_col:
            df['description'] = df[desc_col].astype(str)
        else:
            sender_col = match_column(['sender', 'sender_account', 'sender_id'], col_list)
            receiver_col = match_column(['receiver', 'receiver_account', 'receiver_id'], col_list)
            if sender_col and receiver_col:
                df['description'] = df[sender_col].astype(str) + " → " + df[receiver_col].astype(str)
            else:
                df['description'] = "No description"

        print(f"🔎 Matched columns - Date: {date_col} | Amount: {withdrawal_col or deposit_col or amount_col} | Desc: {desc_col}")
        
        # Parse date
        df['date'] = pd.to_datetime(df[date_col], errors='coerce') if date_col else pd.NaT

        # Clean rows
        df = df.dropna(subset=['date', 'amount', 'description'])

        if df.empty:
            raise ValueError("❌ Parsed dataframe is empty after cleaning. Please check the file format.")

        print(f"📊 Rows after cleaning: {len(df)}")
        if "category" not in df.columns:
            df["category"] = "uncategorized"

        df["category"] = (
            df["category"]
            .astype(str)
            .str.strip()
            .str.lower()
        )
        return df
    except Exception as e:
        raise Exception(f"CSV parsing failed: {str(e)}")
