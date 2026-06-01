import streamlit as st
from database import cursor, conn
import pandas as pd
from datetime import date

st.title("🧾 Insurance Claim Form")

user = st.session_state.get("user")

# ------------------ FETCH EXISTING CLAIMS ------------------
cursor.execute("SELECT * FROM claims WHERE username=?", (user,))
records = cursor.fetchall()

st.subheader("📂 Your Previous Claims")

if records:
    df = pd.DataFrame(records, columns=[
        "id","username","full_name","age","gender","phone","email",
        "policy_number","insurance_type","incident_date","incident_type",
        "description","claim_amount","status","prediction","probability"
    ])
    st.dataframe(df)

    claim_ids = df["id"].tolist()
    edit_id = st.selectbox("Select Claim to Edit", ["New"] + claim_ids)
else:
    edit_id = "New"

# ------------------ FORM ------------------
st.subheader("📝 Fill / Edit Claim")

full_name = st.text_input("Full Name")
age = st.number_input("Age", 18, 100)
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
phone = st.text_input("Phone Number")
email = st.text_input("Email")

policy_number = st.text_input("Policy Number")
insurance_type = st.selectbox("Insurance Type", ["Health", "Vehicle", "Life"])

incident_date = st.date_input("Incident Date", date.today())
incident_type = st.selectbox("Incident Type", [
    "Accident", "Theft", "Fire", "Medical Emergency", "Other"
])

description = st.text_area("Incident Description")
claim_amount = st.number_input("Claim Amount", min_value=0.0)

# ------------------ SUBMIT ------------------
if st.button("Submit Claim"):
    if edit_id == "New":
        cursor.execute("""
        INSERT INTO claims (
            username, full_name, age, gender, phone, email,
            policy_number, insurance_type, incident_date,
            incident_type, description, claim_amount,
            status, prediction, probability
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            user, full_name, age, gender, phone, email,
            policy_number, insurance_type, str(incident_date),
            incident_type, description, claim_amount,
            "Pending", None, None
        ))
        conn.commit()
        st.success("✅ Claim Submitted!")

    else:
        cursor.execute("""
        UPDATE claims SET
            full_name=?, age=?, gender=?, phone=?, email=?,
            policy_number=?, insurance_type=?, incident_date=?,
            incident_type=?, description=?, claim_amount=?
        WHERE id=?
        """, (
            full_name, age, gender, phone, email,
            policy_number, insurance_type, str(incident_date),
            incident_type, description, claim_amount,
            edit_id
        ))
        conn.commit()
        st.success("✏️ Claim Updated!")