import streamlit as st
from database import get_connection

def login(role):
    st.subheader(f"🔐 {role.capitalize()} Login")

    email = st.text_input("Email", key=f"login_email_{role}")
    password = st.text_input("Password", type="password", key=f"login_pass_{role}")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT id, role, status FROM users
        WHERE email=? AND password=? AND role=?
        """, (email, password, role))

        user = cur.fetchone()
        conn.close()

        if not user:
            st.error("Invalid credentials")
            return

        if user[2] != "Approved":
            st.warning(f"Your account is {user[2]}. Please wait for admin approval.")
            return

        # ✅ SET SESSION STATE (MOST IMPORTANT)
        st.session_state.logged_in = True
        st.session_state.user_id = user[0]
        st.session_state.role = user[1]

        st.success("Login successful")
        st.rerun()


def register(role):
    st.subheader(f"📝 {role.capitalize()} Registration")

    name = st.text_input("Name", key=f"reg_name_{role}")
    email = st.text_input("Email", key=f"reg_email_{role}")
    password = st.text_input("Password", type="password", key=f"reg_pass_{role}")

    if st.button("Register"):
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
            INSERT INTO users (name, email, password, role, status)
            VALUES (?, ?, ?, ?, 'Pending')
            """, (name, email, password, role))
            conn.commit()
            st.success("Registration submitted. Await admin approval.")
        except:
            st.error("Email already exists")

        conn.close()
