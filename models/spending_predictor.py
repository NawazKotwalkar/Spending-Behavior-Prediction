import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_models_by_category(monthly_df: pd.DataFrame):
    """
    Train one model per category using lag features.

    Expected columns:
    month | category | total_spend

    Returns:
    models_dict, metrics_dict
    """

    df = monthly_df.copy()

    required_cols = {"month", "category", "total_spend"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Expected columns {required_cols}")

    df["month"] = pd.PeriodIndex(df["month"], freq="M")
    df = df.sort_values(["category", "month"])

    models = {}
    metrics = {}

    for category, g in df.groupby("category"):
        g = g.copy()

        # --- Lag features ---
        g["lag_1"] = g["total_spend"].shift(1)
        g["roll_3"] = g["total_spend"].rolling(3).mean()

        g = g.dropna()

        if len(g) < 3:
            continue

        X = g[["lag_1", "roll_3"]]
        y = g["total_spend"]

        split_idx = max(1, int(len(g) * 0.8))

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        model = Ridge(alpha=1.0)
        model.fit(X_train, y_train)

        if len(X_test) > 0:
            preds = model.predict(X_test)
            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
        else:
            mae, rmse = 0.0, 0.0

        models[category] = model
        metrics[category] = (mae, rmse)

    return models, metrics
def predict_next_month(models, history_df, category: str):
    """
    Predict next month's spending for a category.
    """

    if category not in models:
        return 0.0

    g = (
        history_df[history_df["category"] == category]
        .sort_values("month")
        .tail(3)
    )

    if len(g) < 2:
        return float(g["total_spend"].mean()) if not g.empty else 0.0

    lag_1 = g.iloc[-1]["total_spend"]
    roll_3 = g["total_spend"].mean()

    X_new = pd.DataFrame([{
        "lag_1": lag_1,
        "roll_3": roll_3
    }])

    pred = models[category].predict(X_new)[0]
    return float(max(0, pred))
