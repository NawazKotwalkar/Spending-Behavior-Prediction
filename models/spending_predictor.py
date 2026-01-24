import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_model(monthly_df: pd.DataFrame):
    """
    Train a spending prediction model.
    Expected columns: month, category, total_spend
    """

    df = monthly_df.copy()

    # Convert month to numeric timeline
    df["month_idx"] = pd.PeriodIndex(df["month"], freq="M").astype(int)

    X = df[["month_idx", "category"]]
    X = pd.get_dummies(X, columns=["category"], drop_first=True)

    y = df["total_spend"]

    # Time-based split (NO shuffle)
    split_idx = max(1, int(len(df) * 0.8))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=6
    )

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
    Predict spend for a given future month & category.
    """

    month_idx = pd.Period(month, freq="M").ordinal

    X_new = pd.DataFrame([{
        "month_idx": month_idx,
        "category": category
    }])

    X_new = pd.get_dummies(X_new)

    # Align columns with training
    for col in model.feature_names_in_:
        if col not in X_new.columns:
            X_new[col] = 0

    X_new = X_new[model.feature_names_in_]

    prediction = model.predict(X_new)[0]
    return float(max(0, prediction))