import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_model(df: pd.DataFrame):
    """
    Train a FAST & LIGHT Ridge regression model.
    Expected input df columns:
    date | category | amount
    """

    df = df.copy()

    # --- Basic cleanup ---
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "category", "amount"])

    # --- Monthly aggregation ---
    df["month"] = df["date"].dt.to_period("M").astype(str)

    grouped = (
        df.groupby(["month", "category"])["amount"]
        .sum()
        .abs()
        .reset_index(name="total_spend")
    )

    if grouped.empty:
        return None, (0.0, 0.0)

    # --- Encode time numerically ---
    grouped["month_idx"] = pd.PeriodIndex(
        grouped["month"], freq="M"
    ).astype(int)

    X = grouped[["month_idx", "category"]]
    X = pd.get_dummies(X, columns=["category"], drop_first=True)

    y = grouped["total_spend"]

    # --- Time-based split (NO shuffle) ---
    split_idx = max(1, int(len(grouped) * 0.8))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # --- Ridge model (FAST) ---
    model = Ridge(alpha=1.0)
    model.fit(X_train, y_train)

    if len(X_test) > 0:
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
    else:
        mae, rmse = 0.0, 0.0

    return model, (mae, rmse)


def predict_spending(model, month: str, category: str):
    """
    Predict spend for a future month & category.
    """

    month_idx = pd.Period(month, freq="M").ordinal

    X_new = pd.DataFrame(
        [{
            "month_idx": month_idx,
            "category": category
        }]
    )

    X_new = pd.get_dummies(X_new)
    # Align with training columns
    for col in model.feature_names_in_:
        if col not in X_new.columns:
            X_new[col] = 0

    X_new = X_new[model.feature_names_in_]

    prediction = model.predict(X_new)[0]
    return float(max(0, prediction))