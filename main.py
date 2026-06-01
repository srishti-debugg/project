import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

print("RUNNING ✅")

# Load data
df = pd.read_csv("insurance.csv")

# Clean column names
df.columns = df.columns.str.strip()
print("Columns:", df.columns)

# 🔥 Fix BMI column
df['bmi'] = df['bmi'].astype(str)
df['bmi'] = df['bmi'].str.replace(r'[^0-9.]', '', regex=True)
df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')

# Encode categorical columns FIRST
df['sex'] = df['sex'].map({'male': 0, 'female': 1})
df['smoker'] = df['smoker'].map({'no': 0, 'yes': 1})
df['region'] = df['region'].astype('category').cat.codes

# Convert remaining numeric columns safely
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['children'] = pd.to_numeric(df['children'], errors='coerce')
df['charges'] = pd.to_numeric(df['charges'], errors='coerce')

# NOW drop invalid rows (correct place)
df = df.dropna()

# Target
df['fraud'] = (df['charges'] > df['charges'].median()).astype(int)

# Features & target
X = df.drop(['charges', 'fraud'], axis=1)
y = df['fraud']

# Final safety
X = X.apply(pd.to_numeric, errors='coerce')
X = X.dropna()
y = y.loc[X.index]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Accuracy
print("Model Accuracy:", model.score(X_test, y_test))

# Test sample
sample = pd.DataFrame([{
    "age": 45,
    "sex": 0,
    "bmi": 25.3,
    "children": 2,
    "smoker": 1,
    "region": 1
}])

prediction = model.predict(sample)[0]

if prediction == 1:
    print("Fraud Detected 🚨")
else:
    print("Not Fraud ✅")