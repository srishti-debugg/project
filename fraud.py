import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


st.set_page_config(page_title="Fraud Detection System", page_icon="🕵️")


def clean_feature_column(series):
    numeric_series = pd.to_numeric(series, errors="coerce")

    if numeric_series.notna().sum() >= len(series) * 0.8:
        return numeric_series.fillna(numeric_series.median())

    text_series = series.astype(str).fillna("Unknown")
    encoder = LabelEncoder()
    return encoder.fit_transform(text_series)


def clean_target_column(series):
    cleaned = series.astype(str).str.strip().str.lower()

    fraud_mapping = {
        "1": 1,
        "yes": 1,
        "true": 1,
        "fraud": 1,
        "fraudulent": 1,
        "0": 0,
        "no": 0,
        "false": 0,
        "not fraud": 0,
        "non fraud": 0,
        "non-fraud": 0,
    }

    mapped = cleaned.map(fraud_mapping)

    if mapped.notna().sum() > 0:
        return mapped

    return pd.to_numeric(series, errors="coerce")


def prepare_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    if "fraud" not in df.columns:
        return None, None, "The CSV must contain a column named 'fraud'."

    df = df.dropna(how="all")

    if df.empty:
        return None, None, "The uploaded CSV does not contain usable rows."

    y = clean_target_column(df["fraud"]).fillna(0).astype(int)
    X = df.drop(columns=["fraud"])

    if X.empty:
        return None, None, "The CSV must contain at least one feature column besides 'fraud'."

    cleaned_features = pd.DataFrame(index=X.index)

    for column in X.columns:
        cleaned_features[column] = clean_feature_column(X[column])

    cleaned_features = cleaned_features.fillna(0)

    if y.nunique() < 2:
        return None, None, "The 'fraud' column must contain both classes: 0 and 1."

    return cleaned_features, y, None


def fraud_app():
    st.title("🕵️ Fraud Detection System")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is None:
        st.info("Upload a CSV file that contains a 'fraud' column.")
        return

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read the CSV file: {error}")
        return

    st.subheader("📄 Raw Data")
    st.dataframe(df.head())

    X, y, error_message = prepare_data(df)

    if error_message:
        st.error(error_message)
        return

    st.subheader("✅ Cleaned Training Data")
    cleaned_preview = X.copy()
    cleaned_preview["fraud"] = y
    st.dataframe(cleaned_preview.head())

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
    )

    try:
        model.fit(X, y)
    except Exception as error:
        st.error(f"🚨 Training failed: {error}")
        return

    st.success("✅ Model trained successfully")

    if st.button("Run Prediction", type="primary"):
        predictions = model.predict(X)

        result_df = df.copy()
        result_df["Prediction"] = predictions

        if hasattr(model, "predict_proba"):
            result_df["Fraud Probability"] = model.predict_proba(X)[:, 1].round(3)

        st.subheader("🔍 Prediction Results")
        st.dataframe(result_df)


if __name__ == "__main__":
    fraud_app()
