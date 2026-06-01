import joblib
import pandas as pd

def predict(input_data):
    model = joblib.load("models/model.pkl")

    df = pd.DataFrame([input_data])

    prediction = model.predict(df)[0]

    return "Fraud" if prediction == 1 else "Not Fraud"