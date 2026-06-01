import streamlit as st
from database import cursor, conn
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_page():
    st.title("🔐 Insurance System Login")

    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox(
    "Menu",
    ["Login", "Signup"],
    key="login_menu"
)

    # ---------- SIGNUP ----------
    if choice == "Signup":
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type='password')

        # 👉 PUT YOUR CODE HERE 👇
        if st.button("Signup"):
            if not new_user or not new_pass:
                st.warning("Please fill all fields")
            else:
                try:
                    cursor.execute(
                        "INSERT INTO users (username, password) VALUES (?,?)",
                        (new_user, hash_password(new_pass))
                    )
                    conn.commit()

                    st.success("Account Created!")

                    # ✅ AUTO LOGIN + REDIRECT
                    st.session_state["user"] = new_user
                    st.rerun()

                except:
                    st.error("Username already exists")

    # ---------- LOGIN ----------
    elif choice == "Login":
        user = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (user, hash_password(password))
            )
            data = cursor.fetchone()

            if data:
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Invalid credentials")