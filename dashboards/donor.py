import streamlit as st
from database import get_connection
from utils.logout import logout
from notifications import get_notifications, mark_as_read


# ======================= DONOR DASHBOARD =======================
def donor_dashboard():
    st.sidebar.title("🧑‍🦱 Donor Panel")
    
    show_notifications()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "👤 Manage Profile",
            "📅 View Camp Details",
            "🩸 Blood Details",
            "📜 History",
            "🚪 Logout"
        ],
        key="donor_menu"
    )


    # 🔐 LOGOUT MUST BE HANDLED FIRST
    if menu == "🚪 Logout":
        logout()
        return

    user_id = st.session_state["user_id"]

    # ================= MANAGE PROFILE =================
    if menu == "👤 Manage Profile":
        st.header("👤 Manage Profile")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.name, u.phone, u.address, u.gender,
                   d.age, d.weight, d.blood_group
            FROM users u
            LEFT JOIN donors d ON u.id = d.user_id
            WHERE u.id=?
        """, (user_id,))
        profile = cur.fetchone()
        conn.close()

        name = st.text_input("Full Name", profile[0] if profile else "")
        phone = st.text_input("Mobile", profile[1] if profile else "")
        address = st.text_area("Address", profile[2] if profile else "")
        gender = st.selectbox(
            "Gender", ["Male", "Female", "Other"],
            index=["Male","Female","Other"].index(profile[3]) if profile and profile[3] else 0
        )
        age = st.number_input(
    "Age",
    min_value=18,
    max_value=65,
    value=int(profile[4]) if profile and profile[4] is not None else 18,
    step=1
)

        weight = st.number_input(
    "Weight (kg)",
    min_value=40.0,max_value=150.0,value=float(profile[5]) if profile and profile[5] is not None else 45.0,step=0.5
)

        blood_group = st.selectbox(
            "Blood Group",
            ["A+","A-","B+","B-","O+","O-","AB+","AB-"],
            index=["A+","A-","B+","B-","O+","O-","AB+","AB-"].index(profile[6]) if profile and profile[6] else 0
        )

        if st.button("💾 Save / Update Profile", key="save_profile"):
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                UPDATE users
                SET name=?, phone=?, address=?, gender=?
                WHERE id=?
            """, (name, phone, address, gender, user_id))

            cur.execute("""
                INSERT OR REPLACE INTO donors
                (user_id, age, weight, blood_group)
                VALUES (?, ?, ?, ?)
            """, (user_id, age, weight, blood_group))

            conn.commit()
            conn.close()
            st.success("Profile updated successfully")

    # ================= CAMPS =================
    elif menu == "📅 View Camp Details":
        st.header("📅 Blood Donation Camps")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT camp_date, camp_time, venue FROM camps")
        camps = cur.fetchall()
        conn.close()

        if camps:
            for c in camps:
                st.info(f"📆 {c[0]} | ⏰ {c[1]} | 📍 {c[2]}")
        else:
            st.warning("No camps available")

    # ================= BLOOD DETAILS =================
    elif menu == "🩸 Blood Details":
        st.header("🩺 Health Screening Details")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT hemoglobin, heart_rate,
                   temperature, status, remarks
            FROM health_screening
            WHERE donor_id=?
        """, (user_id,))
        record = cur.fetchone()
        conn.close()

        if record:
            st.success(f"Hemoglobin: {record[0]} g/dL")
            st.success(f"Heart Rate: {record[1]} bpm")
            st.success(f"Temperature: {record[2]} °C")
            st.info(f"Status: {record[3]}")
            st.write(f"Remarks: {record[4]}")
        else:
            st.warning("No screening data found")

    # ================= HISTORY =================
    elif menu == "📜 History":
        st.header("🩸 Donation History")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT donation_date, units, result
            FROM donations
            WHERE donor_id=?
            ORDER BY donation_date DESC
        """, (user_id,))
        history = cur.fetchall()
        conn.close()

        if history:
            for h in history:
                st.success(f"{h[0]} → {h[1]} units → {h[2]}")
        else:
            st.warning("No donation history")



# ======================= NOTIFICATIONS =======================

def show_notifications():
    notes = get_notifications(
        st.session_state["user_id"],
        "donor"
    )

    if notes:
        st.sidebar.markdown("### 🔔 Alerts")
        for n in notes:
            st.sidebar.error(n[1])
            st.sidebar.caption(n[2])
            if st.sidebar.button("Mark Read", key=f"don_{n[0]}"):
                mark_as_read(n[0])
                st.rerun()
