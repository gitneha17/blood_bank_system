import streamlit as st
from database import get_connection


def login_page():
    st.title("🩸 Blood Bank Management System")
    st.subheader("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, role, status
            FROM users
            WHERE email=? AND password=?
        """, (email, password))

        user = cur.fetchone()
        conn.close()

        if user:
            if user[2] != "Approved":
                st.error("⛔ Your account is not approved yet")
            else:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.role = user[1]
                st.rerun()
        else:
            st.error("❌ Invalid email or password")
