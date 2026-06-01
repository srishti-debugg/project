import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# =========================
# ✅ DATABASE CONNECTION (FIXED)
# =========================
conn = sqlite3.connect("insurance.db", check_same_thread=False)


# =========================
# 📄 PDF FUNCTION
# =========================
def generate_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    result = "Fraud Detected" if data["prediction"] == 1 else "Not Fraud"

    content = [
        Paragraph(f"Claim ID: {data['id']}", styles["Normal"]),
        Paragraph(f"Username: {data['username']}", styles["Normal"]),
        Paragraph(f"Age: {data['age']}", styles["Normal"]),
        Paragraph(f"BMI: {data['bmi']}", styles["Normal"]),
        Paragraph(f"State: {data['state']}", styles["Normal"]),
        Paragraph(f"Result: {result}", styles["Normal"]),
        Paragraph(f"Status: {data['status']}", styles["Normal"]),
    ]

    doc.build(content)
    return buffer.getvalue()


# =========================
# 🧾 SHOW CLAIM
# =========================
def show_claim(row, conn):
    st.markdown("---")

    st.write(f"**Claim ID:** {row['id']}")
    st.write(f"**Age:** {row['age']}")
    st.write(f"**BMI:** {row['bmi']}")
    st.write(f"**State:** {row['state']}")

    result = "🚨 Fraud Detected" if int(row["prediction"]) == 1 else "✅ Not Fraud"
    st.write(f"**Result:** {result}")

    st.write(f"**Status:** {row['status']}")

    pdf = generate_pdf({
        "id": int(row["id"]),
        "username": str(row["username"]),
        "age": int(row["age"]),
        "bmi": float(row["bmi"]),
        "state": str(row["state"]),
        "prediction": int(row["prediction"]),
        "status": str(row["status"])
    })

    st.download_button(
        label=f"⬇️ Download Claim {row['id']}",
        data=pdf,
        file_name=f"claim_{row['id']}.pdf",
        mime="application/pdf",
        key=f"download_{row['id']}"
    )

    # DELETE FIX
    cursor = conn.cursor()
    if st.button(f"❌ Delete Claim {row['id']}", key=f"delete_{row['id']}"):
        cursor.execute(
            "DELETE FROM claims WHERE id = ?",
            (row["id"],)
        )
        conn.commit()

        st.success(f"Claim {row['id']} deleted")
        st.rerun()


# =========================
# 📂 HISTORY PAGE
# =========================
def history_page(conn):
    st.title("📂 My Claims")

    if "user" not in st.session_state:
        st.session_state["user"] = "test"  # temp fix

    # 🔍 DEBUG TABLE NAME
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    st.write("Tables:", cursor.fetchall())

    try:
        # ⚠️ CHANGE TABLE NAME HERE IF NEEDED
        df = pd.read_sql_query(
            "SELECT * FROM claims ORDER BY id DESC",
            conn
        )
    except Exception as e:
        st.error(f"Error loading claims: {e}")
        return

    if df.empty:
        st.info("No claims submitted yet.")
        return

    # ✅ FIXED STATUS CLEANING
    df["status_clean"] = df["status"].astype(str).str.strip().str.lower()

    accepted_df = df[df["status_clean"].isin(["accepted", "approved"])]
    rejected_df = df[df["status_clean"].isin(["rejected", "denied"])]

    st.write(f"✅ Accepted: {len(accepted_df)} | ❌ Rejected: {len(rejected_df)}")

    # ACCEPTED
    st.subheader("✅ Accepted Claims")
    for _, row in accepted_df.iterrows():
        show_claim(row, conn)

    # REJECTED
    st.subheader("❌ Rejected Claims")
    for _, row in rejected_df.iterrows():
        show_claim(row, conn)


# =========================
# 🚀 RUN
# =========================
history_page(conn)