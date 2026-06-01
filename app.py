import numpy as np
import pandas as pd
import streamlit as st
import hashlib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


st.set_page_config(page_title="Fraud Detection", page_icon="🚗", layout="centered")

FEATURE_COLUMNS = ["age", "sex", "bmi", "children", "smoker", "region"]

locations = [
    "California", "Florida", "Georgia", "Illinois", "New York", "Ohio", "Texas", "Washington",
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands",
    "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

REGION_BY_STATE = {
    "California": 0, "Washington": 0, "Illinois": 1, "Ohio": 1,
    "Florida": 2, "Georgia": 2, "New York": 3, "Texas": 3,
    "Andhra Pradesh": 1, "Arunachal Pradesh": 2, "Assam": 2, "Bihar": 2,
    "Chhattisgarh": 1, "Goa": 3, "Gujarat": 3, "Haryana": 0,
    "Himachal Pradesh": 0, "Jharkhand": 2, "Karnataka": 1, "Kerala": 1,
    "Madhya Pradesh": 1, "Maharashtra": 3, "Manipur": 2, "Meghalaya": 2,
    "Mizoram": 2, "Nagaland": 2, "Odisha": 2, "Punjab": 0,
    "Rajasthan": 0, "Sikkim": 2, "Tamil Nadu": 1, "Telangana": 1,
    "Tripura": 2, "Uttar Pradesh": 0, "Uttarakhand": 0, "West Bengal": 2,
    "Andaman and Nicobar Islands": 1, "Chandigarh": 0,
    "Dadra and Nagar Haveli and Daman and Diu": 3, "Delhi": 0,
    "Jammu and Kashmir": 0, "Ladakh": 0, "Lakshadweep": 1, "Puducherry": 1,
}


def get_region(state):
    return REGION_BY_STATE.get(state, 0)


@st.cache_data
def load_data():
    rng = np.random.default_rng(42)
    rows = 1500

    age = rng.integers(18, 86, rows)
    sex = rng.integers(0, 3, rows)
    bmi = rng.normal(28, 6, rows).clip(10, 50).round(1)
    children = rng.integers(0, 6, rows)
    smoker = rng.integers(0, 2, rows)
    region = rng.integers(0, 4, rows)

    risk = (
        0.018 * (age - 18)
        + 0.09 * np.maximum(bmi - 30, 0)
        + 0.75 * smoker
        + 0.16 * np.maximum(children - 2, 0)
        + 0.08 * region
        + rng.normal(0, 0.55, rows)
    )

    fraud = (risk > 1.65).astype(int)

    charges = (
        2500
        + age * 90
        + bmi * 170
        + children * 650
        + smoker * 14000
        + fraud * 8000
        + rng.normal(0, 1500, rows)
    ).clip(1000, None).round(2)

    return pd.DataFrame({
        "age": age,
        "sex": sex,
        "bmi": bmi,
        "children": children,
        "smoker": smoker,
        "region": region,
        "charges": charges,
        "fraud": fraud,
    })


@st.cache_resource
def train_model():
    df = load_data()

    X = df[FEATURE_COLUMNS]
    y = df["fraud"]

    X_train, _, y_train, _ = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=250,
        random_state=42,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)
    return model


def encode_sex(sex):
    return {"male": 0, "female": 1, "other": 2}[sex]


def build_input(age, sex, bmi, children, smoker, state):
    return pd.DataFrame(
        [{
            "age": age,
            "sex": encode_sex(sex),
            "bmi": bmi,
            "children": children,
            "smoker": 1 if smoker == "yes" else 0,
            "region": get_region(state),
        }],
        columns=FEATURE_COLUMNS,
    )


def initialize_claim_history():
    if "accepted_claims" not in st.session_state:
        st.session_state.accepted_claims = []

    if "rejected_claims" not in st.session_state:
        st.session_state.rejected_claims = []


def initialize_auth():
    if "users" not in st.session_state:
        st.session_state.users = {}

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_page():
    st.title("🔐 Login")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            username = username.strip()

            if not username or not password:
                st.error("Please enter username and password.")
            elif username not in st.session_state.users:
                st.error("User does not exist. Please sign up first.")
            elif st.session_state.users[username] != hash_password(password):
                st.error("Incorrect password.")
            else:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.success("Login successful.")
                st.rerun()

    with signup_tab:
        new_username = st.text_input("Create Username", key="signup_username")
        new_password = st.text_input("Create Password", type="password", key="signup_password")
        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="signup_confirm_password",
        )

        if st.button("Sign Up"):
            new_username = new_username.strip()

            if not new_username or not new_password or not confirm_password:
                st.error("Please fill all sign up fields.")
            elif new_username in st.session_state.users:
                st.error("Username already exists. Please choose another username.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                st.session_state.users[new_username] = hash_password(new_password)
                st.success("Account created successfully. Please log in.")


def save_claim(claim):
    if claim["Status"] == "Accepted":
        st.session_state.accepted_claims.append(claim)
    else:
        st.session_state.rejected_claims.append(claim)


def predict_claim(model, age, sex, bmi, children, smoker, state):
    input_df = build_input(age, sex, bmi, children, smoker, state)
    prediction = int(model.predict(input_df)[0])
    prob = float(model.predict_proba(input_df)[0][1])
    prob = max(0.0, min(prob, 1.0))
    return prediction, prob


def fraud_app():
    st.title("🚗 Fraud Detection")

    model = train_model()

    age = st.slider("Age", 18, 100, 30)
    sex = st.selectbox("Gender", ["male", "female", "other"])
    bmi = st.slider("BMI", 10.0, 50.0, 25.0, step=0.1)
    children = st.slider("Children", 0, 5, 1)
    smoker = st.selectbox("Smoker", ["no", "yes"])
    state = st.selectbox("Location", locations)

    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None

    if st.button("Predict Fraud", type="primary"):
        prediction, prob = predict_claim(model, age, sex, bmi, children, smoker, state)

        st.session_state.prediction_result = {
            "prediction": prediction,
            "prob": prob,
            "age": age,
            "bmi": bmi,
            "children": children,
            "smoker": 1 if smoker == "yes" else 0,
        }

    if st.session_state.prediction_result is not None:
        show_result(st.session_state.prediction_result)


def claim_form_page():
    st.title("📝 Claim Form")

    model = train_model()

    with st.form("claim_form"):
        claimant_name = st.text_input("Claimant Name")
        policy_number = st.text_input("Policy Number")
        claim_amount = st.number_input("Claim Amount", min_value=0.0, step=500.0)
        claim_reason = st.text_area("Claim Reason")

        st.markdown("### Applicant Details")
        age = st.slider("Age", 18, 100, 30)
        sex = st.selectbox("Gender", ["male", "female", "other"])
        bmi = st.slider("BMI", 10.0, 50.0, 25.0, step=0.1)
        children = st.slider("Children", 0, 5, 1)
        smoker = st.selectbox("Smoker", ["no", "yes"])
        state = st.selectbox("Location", locations)

        submitted = st.form_submit_button("Submit Claim", type="primary")

    if submitted:
        if not claimant_name.strip() or not policy_number.strip():
            st.error("Please enter both claimant name and policy number.")
            return

        prediction, prob = predict_claim(model, age, sex, bmi, children, smoker, state)
        status = "Rejected" if prediction == 1 else "Accepted"

        claim = {
            "Claimant Name": claimant_name.strip(),
            "Policy Number": policy_number.strip(),
            "Claim Amount": claim_amount,
            "Claim Reason": claim_reason.strip(),
            "Age": age,
            "Gender": sex,
            "BMI": bmi,
            "Children": children,
            "Smoker": smoker,
            "Location": state,
            "Fraud Probability": round(prob, 2),
            "Status": status,
        }

        save_claim(claim)

        if status == "Rejected":
            st.error(f"🚨 Claim Rejected - Fraud Probability: {prob:.2f}")
        else:
            st.success(f"✅ Claim Accepted - Fraud Probability: {prob:.2f}")

        st.dataframe(pd.DataFrame([claim]))


def history_page():
    st.title("📚 Claim History")

    accepted_claims = st.session_state.accepted_claims
    rejected_claims = st.session_state.rejected_claims

    st.subheader(f"✅ Accepted Claims Pile ({len(accepted_claims)})")
    if accepted_claims:
        st.dataframe(pd.DataFrame(accepted_claims), use_container_width=True)
    else:
        st.info("No accepted claims yet.")

    st.markdown("---")

    st.subheader(f"🚨 Rejected Claims Pile ({len(rejected_claims)})")
    if rejected_claims:
        st.dataframe(pd.DataFrame(rejected_claims), use_container_width=True)
    else:
        st.info("No rejected claims yet.")

    if accepted_claims or rejected_claims:
        if st.button("Clear Claim History"):
            st.session_state.accepted_claims = []
            st.session_state.rejected_claims = []
            st.success("Claim history cleared.")
            st.rerun()


def show_result(data):
    prediction = data["prediction"]
    prob = data["prob"]
    age = data["age"]
    bmi = data["bmi"]
    children = data["children"]
    smoker_val = data["smoker"]

    if prediction == 1:
        st.error(f"🚨 Fraud Detected (Probability: {prob:.2f})")
    else:
        st.success(f"✅ Not Fraud (Probability: {prob:.2f})")

    st.markdown("---")
    st.subheader("🧠 Why this decision was made")

    risk_score = 0
    reasons = []
    safe_points = []

    if smoker_val == 1:
        risk_score += 2
        reasons.append("🚬 Applicant is a smoker, which increases medical claim risk.")
    else:
        safe_points.append("🚭 Applicant is not a smoker, reducing health risk.")

    if bmi > 30:
        risk_score += 2
        reasons.append(f"⚖️ High BMI ({bmi:.1f}) indicates higher medical expenses.")
    else:
        safe_points.append(f"⚖️ BMI ({bmi:.1f}) is within a healthy range.")

    if age > 60:
        risk_score += 2
        reasons.append(f"👴 Higher age ({age}) increases probability of claims.")
    else:
        safe_points.append(f"🧑 Age ({age}) is within a low-risk range.")

    if children >= 3:
        risk_score += 1
        reasons.append(f"👨‍👩‍👧 More dependents ({children}) increase claim burden.")
    else:
        safe_points.append(f"👨‍👩‍👧 Fewer dependents ({children}) indicate controlled risk.")

    if prob > 0.7:
        risk_score += 2
        reasons.append(
            f"📊 Model confidence is high ({prob:.2f}), indicating strong fraud likelihood."
        )
    else:
        safe_points.append(
            f"📊 Model confidence is low ({prob:.2f}), indicating normal behavior."
        )

    if prediction == 1:
        st.markdown("### 🚨 Why this claim is classified as FRAUD")

        for reason in reasons:
            st.write("•", reason)

        if safe_points:
            st.markdown("#### ⚠️ Some normal factors were also observed:")
            for point in safe_points:
                st.write("•", point)

        st.markdown("#### 📌 Final Conclusion:")
        st.write(
            "The claim shows multiple high-risk indicators and abnormal patterns, "
            "which strongly suggest potential fraud."
        )

        st.warning(f"⚠️ Overall Risk Score: {risk_score}/10")

    else:
        st.markdown("### ✅ Why this claim is classified as NOT FRAUD")

        for point in safe_points:
            st.write("•", point)

        if reasons:
            st.markdown("#### ⚠️ Minor risk factors:")
            for reason in reasons:
                st.write("•", reason)

        st.markdown("#### 📌 Final Conclusion:")
        st.write(
            "The claim falls within expected and normal patterns. "
            "No strong fraud indicators were detected."
        )

        st.success(f"✔️ Overall Risk Score: {risk_score}/10 (Low Risk)")

    st.markdown("---")
    st.subheader("📊 Fraud Probability Meter")

    st.progress(prob)
    st.caption(f"Fraud Probability Score: {prob:.2f}")


if __name__ == "__main__":
    initialize_auth()
    initialize_claim_history()

    if not st.session_state.logged_in:
        login_page()
        st.stop()

    st.sidebar.success(f"Logged in as {st.session_state.current_user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    page = st.sidebar.radio(
        "Navigation",
        ["Fraud Detection", "Claim Form", "History"],
    )

    if page == "Fraud Detection":
        fraud_app()
    elif page == "Claim Form":
        claim_form_page()
    else:
        history_page()
