import pandas as pd

df = pd.read_csv("insurance.csv")

print(df.columns.tolist())  # 👈 add this line

X = df.drop("fraud_reported", axis=1)