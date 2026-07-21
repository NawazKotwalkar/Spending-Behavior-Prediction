# Expenxo
## Spending Behaviour Prediction Model

**Know where your money goes—before it's gone.** Expenxo is a personal finance web app that analyzes historical transaction data to uncover spending patterns, track budget adherence, and forecast future expenses using machine learning.

---

## The Problem

- Most people **track spending reactively**, only noticing overspending after the statement arrives
- Category-wise budgeting is **manual and error-prone** without automation
- Personal finance apps typically show **historical data only**, with no forward-looking insight

Expenxo closes this gap by combining transaction history with a Random Forest model to answer not just "what did I spend?" but **"what will I spend next month?"**

---

## What Expenxo Does

| Capability | Impact |
|---|---|
| **Spending pattern analysis** | Understand habits across categories and time |
| **Category-wise tracking** | Break down expenses by grocery, utilities, entertainment, etc. |
| **Budget vs. actual comparison** | Instantly see where you're over or under budget |
| **Monthly spend forecasting** | Predict next month's spending before it happens |
| **Trend visualization** | Spot recurring patterns and seasonal spikes |
| **PDF/report export** | Generate spending reports for personal records |

---

## Technical Implementation

### Model & Approach

- **Algorithm:** Random Forest (Scikit-learn)
- **Feature engineering:** Category-wise aggregation, rolling/time-based features derived from transaction history
- **Prediction granularity:** Monthly spend forecasts, per-category and aggregate
- **Data leakage prevention:** Strict train/prediction separation — no future information leaks into training

### Architecture

| Layer | Technology |
|---|---|
| **Backend / App** | Python, Streamlit |
| **ML framework** | Scikit-learn (Random Forest) |
| **Database** | MySQL (remote server) |
| **Data handling** | Pandas, NumPy |
| **Visualization** | Streamlit charts / Plotly |
| **Reporting** | PDF generation (DejaVu fonts bundled for report rendering) |
| **Dev environment** | Devcontainer-based setup |

---

## Live Demo

**[https://expenxo.streamlit.app](https://expenxo.streamlit.app)**

---

## Data Requirements

### Transaction Data

Must be provided in **CSV format** with the following columns:

| Column | Description |
|---|---|
| `date` | Transaction date |
| `amount` | Transaction amount |
| `description` | Description of the transaction |
| `category` | Spending category |

**Example:**
```csv
date,amount,description,category
2024-01-05,450.00,Grocery Store,Groceries
2024-01-07,1200.00,Electricity Bill,Utilities
```

### Budget Data

Must be provided in **CSV format** with the following columns:

| Column | Description |
|---|---|
| `category` | Spending category |
| `budget` | Budget amount for that category |

**Example:**
```csv
category,budget
Groceries,5000
Utilities,2000
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- MySQL server access
- pip

### Install & Run Locally

```bash
# Clone repository
git clone https://github.com/NawazKotwalkar/Spending-Behavior-Prediction.git
cd Spending-Behavior-Prediction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database connection
# Update credentials in config/

# Run the app
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

> **Note:** The application connects to a remote MySQL database. Initial connection and data loading may take a moment depending on server response — please allow for a short delay on first load.

---

## Project Structure

```
Spending-Behavior-Prediction/
├── app.py                         # Streamlit application entry point
├── .devcontainer/                 # Dev container configuration
├── config/                        # App & database configuration
├── data/                          # Transaction / budget sample data
├── models/                        # Trained Random Forest model artifacts
├── pages/                         # Streamlit multi-page app views
├── reports/                       # Generated report outputs
├── scripts/                       # Training / preprocessing scripts
├── styles/                        # Custom CSS for Streamlit UI
├── ui/                            # UI components
├── utils/                         # Helper utilities (DB connectors, etc.)
├── fonts/dejavu-fonts-ttf-2.37/   # Fonts bundled for PDF report rendering
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Features in Detail

### 1. Spending Overview
Aggregated view of total spend across all categories, with month-over-month comparisons.

### 2. Category-wise Breakdown
Visual breakdown of spending by category, helping identify where money is actually going.

### 3. Budget vs. Actual
Side-by-side comparison of budgeted vs. actual spend per category, flagging overspend areas.

### 4. Monthly Spend Prediction
Random Forest–driven forecast of next month's total and category-wise spend, based on historical trends.

### 5. Report Export
Generate downloadable spending reports (PDF) for personal record-keeping.

---

## Data Integrity & Leakage Prevention

- Training data and prediction targets are strictly separated
- No future information is used during model training
- Feature engineering respects temporal order (no look-ahead bias)

---

## Known Limitations

- **Cold start:** Requires a minimum history of transactions for reliable predictions
- **External shocks:** Does not account for one-off, unpredictable expenses (medical emergencies, major purchases)
- **Category dependency:** Prediction quality depends on consistent, accurate category labeling in source data
- **Database latency:** Remote MySQL connection may introduce delay on first load

---

## Roadmap

### Current (Shipped)
- [x] Transaction & budget CSV ingestion
- [x] Category-wise aggregation and visualization
- [x] Budget vs. actual comparison
- [x] Monthly spend prediction (Random Forest)
- [x] Streamlit multi-page dashboard
- [x] PDF report export

### Upcoming
- [ ] Anomaly detection for unusual transactions
- [ ] Multi-month forecast horizon
- [ ] Recurring expense detection (subscriptions, bills)
- [ ] Model confidence intervals on predictions
- [ ] Bank statement import (auto-parsing)

---

## Development

### Code Standards
- PEP8 compliant
- Type hints encouraged throughout

### Contributing
Pull requests welcome. Please open an issue first to discuss major changes.

---

## Disclaimer

Predictions are based on historical patterns and are intended for **analytical purposes only**. Actual spending may vary due to external or unexpected factors. This tool is not a substitute for professional financial advice.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## About

**Nawaz**
B.Sc. Data Science
Based in Mumbai, India • Open to remote roles

[GitHub](https://github.com/NawazKotwalkar) — [Live App](https://expenxo.streamlit.app)

---

Made with 📊 for smarter spending
