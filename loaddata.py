import streamlit as st
import pandas as pd

@st.cache_data  # For Streamlit >= 1.18
def load_data():
    try:
        df = pd.read_csv("insurance.csv")
    except FileNotFoundError:
        st.error("❌ insurance.csv file not found")
        return pd.DataFrame()

    # 🔥 CLEAN NUMERIC COLUMNS
    for col in ['bmi', 'age', 'children', 'charges']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        else:
            st.error(f"❌ Column '{col}' not found in dataset")
            return pd.DataFrame()

    # 🔥 REMOVE BAD ROWS
    df = df.dropna()

    # ENCODING (safe mapping)
    df['sex'] = df['sex'].map({'male': 0, 'female': 1})
    df['smoker'] = df['smoker'].map({'no': 0, 'yes': 1})
    df['region'] = df['region'].astype('category').cat.codes

    # TARGET
    df['fraud'] = (df['charges'] > df['charges'].median()).astype(int)

    return df