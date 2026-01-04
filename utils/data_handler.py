import pandas as pd
from pandas.tseries.offsets import MonthBegin
from utils.category_mapper import categorize_transaction  # Or .py if that's where it lives

def clean_and_prepare(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    if 'category' not in df.columns or df['category'].isna().all() or (df['category'] == "").all():
        df['category'] = df['description'].apply(lambda x: categorize_transaction(x) or "Uncategorized")

    df['month'] = df['date'].dt.to_period('M').astype(str)
    return df

def get_months_for_prediction(df):
    full_months = df['date'].dt.to_period('M').unique().astype(str).tolist()
    last_month = pd.to_datetime(max(full_months)) + MonthBegin(1)
    next_month_str = last_month.to_period('M').strftime('%Y-%m')
    if next_month_str not in full_months:
        full_months.append(next_month_str)
    return sorted(full_months)