import streamlit as st
import sqlite3

# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("insurance.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- CREATE TABLES ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS accepted (
    username TEXT,
    age INTEGER,
    bmi REAL,
    smoker INTEGER,
    result TEXT,
    reason TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS denied (
    username TEXT,
    age INTEGER,
    bmi REAL,
    smoker INTEGER,
    result TEXT,
    reason TEXT
)
""")
conn.commit()

# ---------------- DEMO LOGIN STATE ----------------
# Remove this if your login system already sets session_state['user']
if "user" not in st.session_state:
    st.session_state["user"] = "demo_user"

# ---------------- FORM ----------------
if "user" in st.session_state:
    st.header("📝 Insurance Form")

    age = st.slider("Age", 18, 100, 30)
    bmi = st.slider("BMI", 10.0, 50.0, 25.0, 0.1)
    smoker = st.selectbox("Smoker", ["no", "yes"])

    smoker_val = 1 if smoker == "yes" else 0

    if st.button("Submit Form"):

        # ---------------- SIMPLE FRAUD LOGIC ----------------
        reasons = []
        fraud = 0

        if bmi > 35:
            reasons.append("High BMI")
            fraud = 1

        if smoker_val == 1:
            reasons.append("Smoker risk")
            fraud = 1

        if fraud == 1:
            result = "Denied"
            reason = "; ".join(reasons)

            cursor.execute("""
                INSERT INTO denied (username, age, bmi, smoker, result, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                st.session_state["user"],
                age,
                bmi,
                smoker_val,
                result,
                reason
            ))

            st.error(f"🚨 Denied: {reason}")

        else:
            result = "Accepted"
            reason = "Low risk profile"

            cursor.execute("""
                INSERT INTO accepted (username, age, bmi, smoker, result, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                st.session_state["user"],
                age,
                bmi,
                smoker_val,
                result,
                reason
            ))

            st.success(f"✅ Accepted: {reason}")

        conn.commit()

        # ---------------- SUMMARY ----------------
        st.markdown("---")
        st.subheader("🧠 Why this decision was made")

        if fraud == 1:
            st.write("The application was denied because:")
            for item in reasons:
                st.write(f"• {item}")
        else:
            st.write("The application was accepted because:")
            st.write("• BMI is not in the high-risk range")
            st.write("• Applicant is not a smoker")
            st.write("• Overall profile is low risk")

else:
    st.warning("Please log in first.")
