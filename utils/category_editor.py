import streamlit as st
import json
import os

CATEGORY_FILE = os.path.join("config", "category_rules.json")

def load_category_rules():
    try:
        with open(CATEGORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_category_rules(rules):
    try:
        with open(CATEGORY_FILE, "w") as f:
            json.dump(rules, f, indent=4)
        return True
    except Exception as e:
        st.error(f"❌ Failed to save: {e}")
        return False

def category_editor_ui():
    st.subheader("🛠 Category Rules Editor")

    rules = load_category_rules()

    category_list = list(rules.keys())
    selected_category = st.selectbox("Select Category to Edit", category_list)

    if selected_category:
        st.write(f"**Keywords for `{selected_category}`**")
        keyword_input = st.text_input("Add new keyword (supports regex):")
        if st.button("➕ Add Keyword"):
            if keyword_input and keyword_input not in rules[selected_category]:
                rules[selected_category].append(keyword_input)
                save_category_rules(rules)
                st.success("✅ Keyword added!")
            else:
                st.warning("⚠️ Enter a new, unique keyword.")

        # Show and remove keywords
        st.write("**Current Keywords:**")
        for word in rules[selected_category]:
            col1, col2 = st.columns([0.9, 0.1])
            col1.write(f"- `{word}`")
            if col2.button("❌", key=f"remove_{word}"):
                rules[selected_category].remove(word)
                save_category_rules(rules)
                st.success(f"✅ Removed `{word}`")

    # Add new category
    with st.expander("➕ Add New Category"):
        new_cat = st.text_input("New Category Name:")
        if st.button("Add Category"):
            if new_cat and new_cat not in rules:
                rules[new_cat] = []
                save_category_rules(rules)
                st.success(f"✅ Category `{new_cat}` added!")
            else:
                st.warning("⚠️ Already exists or empty name.")
