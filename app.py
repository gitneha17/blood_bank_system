import streamlit as st
from database import create_tables, create_admin
from auth import login, register
from dashboards.admin import admin_dashboard
from dashboards.donor import donor_dashboard
from dashboards.hospital import hospital_dashboard

# ---------- DB INIT ----------
create_tables()
create_admin()

st.set_page_config(page_title="Blood Bank System", layout="centered")
st.title("🩸 Blood Bank Management System")

# ---------- NOT LOGGED IN ----------
if "user_id" not in st.session_state:

    option = st.radio("Choose Option", ["Login", "Register"])
    role = st.selectbox("Select Role", ["donor", "hospital", "admin"])

    if option == "Login":
        login(role)

    elif option == "Register":
        if role == "admin":
            st.warning("❌ Admin cannot be registered")
        else:
            register(role)

# ---------- LOGGED IN ----------
else:
    if st.session_state["role"] == "admin":
        admin_dashboard()

    elif st.session_state["role"] == "donor":
        donor_dashboard()

    elif st.session_state["role"] == "hospital":
        hospital_dashboard()
