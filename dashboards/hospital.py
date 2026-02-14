import streamlit as st
from database import get_connection
from utils.logout import logout
from utils.notification import send_notification
from notifications import get_notifications, mark_as_read


# ======================= HOSPITAL DASHBOARD =======================
def hospital_dashboard():
    st.sidebar.title("🏥 Hospital Panel")

    # 🔔 Notifications (always visible)
    show_notifications()

    menu = st.sidebar.radio(
        "Navigation",
        [
            "🔍 Search Donor",
            "🩸 Request Blood",
            "📦 Blood Availability",
            "📋 Donation Records",
            "🚨 Emergency Request",
            "🚪 Logout"
        ],
        key="hospital_menu"
    )

    if menu == "🚪 Logout":
        logout()
        return

    # ================= SEARCH DONOR =================
    if menu == "🔍 Search Donor":
        st.header("🔍 Search Donors")

        bg = st.selectbox(
            "Select Blood Group",
            ["A+","A-","B+","B-","O+","O-","AB+","AB-"]
        )

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.name, u.phone, d.age, d.weight
            FROM users u
            JOIN donors d ON u.id=d.user_id
            WHERE d.blood_group=? AND u.status='Approved'
        """, (bg,))
        donors = cur.fetchall()
        conn.close()

        if donors:
            for d in donors:
                st.info(f"👤 {d[0]} | 📞 {d[1]} | Age {d[2]} | Weight {d[3]} kg")
        else:
            st.warning("No donors found")

    # ================= REQUEST BLOOD =================
    elif menu == "🩸 Request Blood":
        st.header("🩸 Request Blood")

    bg = st.selectbox("Blood Group", ["A+","A-","B+","B-","O+","O-","AB+","AB-"])
    units = st.number_input("Units Required", 1)

    if st.button("Send Request", key="req_blood"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO blood_requests (hospital_id, blood_group, units, created_at)
            VALUES (?, ?, ?, datetime('now'))
        """, (st.session_state["user_id"], bg, units))

        # Notify Admin
        cur.execute("SELECT id FROM users WHERE role='admin'")
        admin = cur.fetchone()
        if admin:
            from notifications import send_notification
            send_notification(
                admin[0],
                "admin",
                f"🩸 Blood Request: {bg} ({units} units)"
            )

        conn.commit()
        conn.close()
        st.success("Blood request sent to Admin")


    # ================= BLOOD STOCK =================
    elif menu == "📦 Blood Availability":
        st.header("📦 Available Blood Stock")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT blood_group, units FROM blood_stock")
        stock = cur.fetchall()
        conn.close()

        if stock:
            for s in stock:
                st.success(f"{s[0]} → {s[1]} units")
        else:
            st.warning("No blood stock available")

    # ================= DONATION RECORDS =================
    elif menu == "📋 Donation Records":
        st.header("📋 Donation Records")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.name, d.blood_group, d.units, d.donation_date
            FROM donations d
            JOIN users u ON d.donor_id=u.id
            ORDER BY d.donation_date DESC
        """)
        data = cur.fetchall()
        conn.close()

        if data:
            for r in data:
                st.info(f"{r[0]} → {r[1]} → {r[2]} units on {r[3]}")
        else:
            st.warning("No donation records found")

    # ================= EMERGENCY REQUEST =================
    elif menu == "🚨 Emergency Request":
        st.header("🚨 Emergency Blood Alert")

    bg = st.selectbox("Blood Group Needed", ["A+","A-","B+","B-","O+","O-","AB+","AB-"])
    units = st.number_input("Units", 1)
    reason = st.text_area("Reason")

    if st.button("Send Emergency Alert", key="emergency"):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.id
            FROM users u
            JOIN donors d ON u.id=d.user_id
            WHERE d.blood_group=? AND u.status='Approved'
        """, (bg,))
        donors = cur.fetchall()

        from notifications import send_notification
        for d in donors:
            send_notification(
                d[0],
                "donor",
                f"🚨 EMERGENCY: {bg} blood needed ({units} units)\nReason: {reason}"
            )

        # Notify Admin
        cur.execute("SELECT id FROM users WHERE role='admin'")
        admin = cur.fetchone()
        if admin:
            send_notification(
                admin[0],
                "admin",
                f"🚨 Emergency Blood Alert: {bg} ({units} units)"
            )

        conn.close()
        st.success("Emergency alert sent successfully")

    
# ======================= NOTIFICATIONS =======================
def show_notifications():
    notes = get_notifications(
        st.session_state["user_id"],
        st.session_state["role"]
    )

    if notes:
        st.sidebar.markdown("### 🔔 Notifications")
        for n in notes:
            st.sidebar.info(f"{n[1]}\n🕒 {n[2]}")
            if st.sidebar.button("Mark as read", key=f"h_note_{n[0]}"):
                mark_as_read(n[0])
                st.rerun()
