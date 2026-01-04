import json
import os
import re

CATEGORY_FILE = os.path.join("config", "category_rules.json")

def load_rules():
    try:
        with open(CATEGORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load category rules: {e}")
        return {}

CATEGORIZATION_RULES = load_rules()

def categorize_transaction(description: str) -> str:
    """Categorize a transaction using regex pattern match."""
    description = str(description).lower()

    for category, keywords in CATEGORIZATION_RULES.items():
        for pattern in keywords:
            if re.search(pattern, description):  # Regex match
                return category

    return 'others'
