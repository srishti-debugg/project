import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("insurance.csv")

    # 🔥 CLEAN BAD VALUES (fix your error)
    for col in ['age', 'bmi', 'children', 'charges']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 🔥 REMOVE INVALID ROWS
    df = df.dropna()

    # ENCODE CATEGORICAL
    df['sex'] = df['sex'].map({'male': 0, 'female': 1})
    df['smoker'] = df['smoker'].map({'no': 0, 'yes': 1})
    df['region'] = df['region'].astype('category').cat.codes

    # CREATE TARGET COLUMN
    df['fraud'] = (df['charges'] > df['charges'].median()).astype(int)

    return df