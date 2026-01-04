import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

MODEL_PATH = os.path.join(model_dir, "spending_model.pkl")
MONTH_ENCODER_PATH = os.path.join(model_dir, "month_encoder.pkl")
CATEGORY_ENCODER_PATH = os.path.join(model_dir, "category_encoder.pkl")

def train_model(df: pd.DataFrame):
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date', 'category', 'amount'], inplace=True)
        df['month'] = df['date'].dt.to_period('M').astype(str)

        grouped = df.groupby(['month', 'category'])['amount'].sum().reset_index()

        le_month = LabelEncoder()
        le_category = LabelEncoder()
        grouped['month_encoded'] = le_month.fit_transform(grouped['month'])
        grouped['category_encoded'] = le_category.fit_transform(grouped['category'])

        X = grouped[['month_encoded', 'category_encoded']]
        y = grouped['amount'].abs()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(le_month, MONTH_ENCODER_PATH)
        joblib.dump(le_category, CATEGORY_ENCODER_PATH)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print("✅ Model trained.")
        print(f"📊 MAE: ₹{mae:.2f}, RMSE: ₹{rmse:.2f}, R²: {r2:.4f}")

        return mae, rmse, r2

    except Exception as e:
        print(f"❌ Training failed: {e}")
        return None, None, None

def predict_spending(month_str: str, category_str: str):
    try:
        model = joblib.load(MODEL_PATH)
        le_month = joblib.load(MONTH_ENCODER_PATH)
        le_category = joblib.load(CATEGORY_ENCODER_PATH)

        if category_str not in le_category.classes_:
            return f"⚠️ Category '{category_str}' not seen during training."

        category_encoded = le_category.transform([category_str])[0]

        if month_str not in le_month.classes_:
            all_months = list(le_month.classes_)
            all_months_sorted = sorted(all_months)
            last_seen_index = le_month.transform([all_months_sorted[-1]])[0]
            month_encoded = last_seen_index + 1
        else:
            month_encoded = le_month.transform([month_str])[0]

        prediction = model.predict([[month_encoded, category_encoded]])
        return abs(prediction[0])

    except FileNotFoundError:
        return "🚫 Model not trained yet."

    except Exception as e:
        return f"❌ Prediction error: {str(e)}"
