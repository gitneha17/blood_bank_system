import streamlit as st
from database import get_connection
from utils.logout import logout
from notifications import get_notifications, mark_as_read
from certificate import generate_certificate


# ======================= ADMIN DASHBOARD =======================
def admin_dashboard():
    st.sidebar.title("🛠 Admin Dashboard")

    menu = st.sidebar.radio(
        "Main Menu",
        [
            "👥 Manage Users",
            "🩸 Manage Blood",
            "📅 Organize Camp",
            "📜 Generate Certificate",
            "🚪 Logout"
        ],
        key="admin_menu"
    )

    
    if menu == "🚪 Logout":
        logout()
        return   # ⛔ STOP dashboard execution
    
    show_notifications()

    # ======================= MANAGE USERS =======================
    if menu == "👥 Manage Users":
        st.header("👥 User Management")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, email, role, status
            FROM users
            WHERE role != 'admin'
        """)
        users = cur.fetchall()

        if not users:
            st.info("No users found")
        else:
            for u in users:
                with st.container(border=True):
                    st.write(f"👤 **Name:** {u[1]}")
                    st.write(f"📧 **Email:** {u[2]}")
                    st.write(f"🎭 **Role:** {u[3]}")
                    st.write(f"📌 **Status:** {u[4]}")

                    col1, col2, col3 = st.columns(3)

                    if col1.button("✅ Approve", key=f"approve_{u[0]}"):
                        cur.execute(
                            "UPDATE users SET status='Approved' WHERE id=?",
                            (u[0],)
                        )
                        conn.commit()
                        st.success("User approved")
                        st.rerun()

                    if col2.button("❌ Reject", key=f"reject_{u[0]}"):
                        cur.execute(
                            "UPDATE users SET status='Rejected' WHERE id=?",
                            (u[0],)
                        )
                        conn.commit()
                        st.warning("User rejected")
                        st.rerun()

                    if col3.button("🗑 Delete", key=f"delete_{u[0]}"):
                        cur.execute("DELETE FROM users WHERE id=?", (u[0],))
                        conn.commit()
                        st.error("User deleted")
                        st.rerun()

        conn.close()

    # ======================= MANAGE BLOOD =======================
    elif menu == "🩸 Manage Blood":
        st.header("🩸 Blood Stock Management")

        bg = st.selectbox(
            "Blood Group",
            ["A+","A-","B+","B-","O+","O-","AB+","AB-"]
        )
        units = st.number_input("Units Available", min_value=0)

        if st.button("🔄 Update Stock", key="update_stock"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO blood_stock (blood_group, units)
                VALUES (?, ?)
            """, (bg, units))
            conn.commit()
            conn.close()
            st.success("Blood stock updated")

        st.subheader("📦 Available Blood")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT blood_group, units FROM blood_stock")
        stock = cur.fetchall()
        conn.close()

        for s in stock:
            st.info(f"{s[0]} → {s[1]} units")

    # ======================= ORGANIZE CAMP =======================
    elif menu == "📅 Organize Camp":
        st.header("📅 Organize Blood Donation Camp")

        camp_date = st.date_input("Camp Date")
        camp_time = st.time_input("Camp Time")
        venue = st.text_input("Venue")

        if st.button("➕ Add Camp", key="add_camp"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO camps (camp_date, camp_time, venue)
                VALUES (?, ?, ?)
            """, (
                camp_date.strftime("%Y-%m-%d"),
                camp_time.strftime("%H:%M"),
                venue
            ))
            conn.commit()
            conn.close()
            st.success("Camp added successfully")

        st.subheader("📋 Existing Camps")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT camp_date, camp_time, venue FROM camps")
        camps = cur.fetchall()
        conn.close()

        for c in camps:
            st.info(f"📆 {c[0]} | ⏰ {c[1]} | 📍 {c[2]}")

    # ======================= CERTIFICATE =======================
    elif menu == "📜 Generate Certificate":
        st.header("📜 Generate Donation Certificate")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT u.name, d.blood_group, d.units, d.donation_date
            FROM donations d
            JOIN users u ON d.donor_id = u.id
            ORDER BY d.donation_date DESC
        """)
        records = cur.fetchall()
        conn.close()

        if not records:
            st.warning("No donation records available")
        else:
            selected = st.selectbox(
                "Select Donation Record",
                records,
                format_func=lambda x: f"{x[0]} | {x[1]} | {x[2]} units | {x[3]}"
            )

            if st.button("🎉 Generate Certificate", key="generate_certificate"):
                file_path = generate_certificate(
                    donor_name=selected[0],
                    blood_group=selected[1],
                    units=selected[2],
                    donation_date=selected[3]
                )

                st.success("Certificate generated successfully")
                st.download_button(
                    "⬇️ Download Certificate",
                    data=open(file_path, "rb"),
                    file_name=file_path.split("/")[-1],
                    mime="application/pdf"
                )

# ======================= Blood Request =======================


    elif menu == "🩸 Blood Requests":
        st.header("🩸 Incoming Blood Requests")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT br.id, u.name, br.blood_group, br.units
        FROM blood_requests br
        JOIN users u ON br.hospital_id=u.id
        WHERE br.status='Pending'
    """)
    requests = cur.fetchall()

    for r in requests:
        with st.container(border=True):
            st.write(f"🏥 Hospital: {r[1]}")
            st.write(f"🩸 {r[2]} | Units: {r[3]}")

            if st.button("Notify Donors", key=f"notify_{r[0]}"):
                cur.execute("""
                    SELECT u.id
                    FROM users u
                    JOIN donors d ON u.id=d.user_id
                    WHERE d.blood_group=? AND u.status='Approved'
                """, (r[2],))
                donors = cur.fetchall()

                from notifications import send_notification
                for d in donors:
                    send_notification(
                        d[0],
                        "donor",
                        f"🩸 Blood Needed: {r[2]} ({r[3]} units)"
                    )

                cur.execute("""
                    UPDATE blood_requests SET status='Processed' WHERE id=?
                """, (r[0],))
                conn.commit()
                st.success("Donors notified")

    conn.close()


# ======================= NOTIFICATIONS =======================
def show_notifications():
    notes = get_notifications(
        st.session_state["user_id"],
        st.session_state["role"]
    )

    if notes:
        st.sidebar.markdown("### 🔔 Alerts")
        for n in notes:
            with st.sidebar.container():
                st.warning(n[1])
                st.caption(n[2])
                if st.button("Read", key=f"admin_note_{n[0]}"):
                    mark_as_read(n[0])
                    st.rerun()
