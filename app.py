import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from Smart_Parking_System import ParkingDatabase, SmartParkingSystem

def setup_database():
    """Ensure the DB exists and is pre-populated"""
    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS slots 
                     (slot_id TEXT PRIMARY KEY, is_available INTEGER, last_updated TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings 
                     (booking_id TEXT PRIMARY KEY, slot_id TEXT, user_name TEXT, 
                      booking_time TEXT, status TEXT)''')
    
    cursor.execute("SELECT COUNT(*) FROM slots")
    if cursor.fetchone()[0] == 0:
        initial_slots = [('A1', 1), ('A2', 1), ('B1', 1), ('B2', 1), ('C1', 1)]
        for s_id, avail in initial_slots:
            cursor.execute("INSERT INTO slots (slot_id, is_available, last_updated) VALUES (?, ?, ?)",
                           (s_id, avail, datetime.now()))
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Smart Parking Pro", page_icon="🚗")

    
    st.markdown("""
        <style>
        div[data-baseweb="select"] svg { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    setup_database()
    
    @st.cache_resource
    def get_system():
        return SmartParkingSystem()

    system = get_system()

    
    if 'msg' not in st.session_state:
        st.session_state['msg'] = None
    if 'msg_owner_tab' not in st.session_state:
        st.session_state['msg_owner_tab'] = None

    st.title("🚗 Smart Parking System")
    st.markdown("---")

    
    slots = system.db.get_all_slots()
    available_list = [s for s, avail in slots.items() if avail]
    
    st.sidebar.header("System Dashboard")
    st.sidebar.metric("Available Slots", f"{len(available_list)}/{len(slots)}")
    
    
    tab1, tab2, tab3 = st.tabs(["📍 View & Book", "🔓 Release Slot", "📊 Admin View"])

    
    with tab1:
        st.subheader("Parking Floor Map")
        cols = st.columns(3)
        for i, (slot_id, is_available) in enumerate(sorted(slots.items())):
            with cols[i % 3]:
                if is_available: st.success(f"Slot {slot_id}: Available")
                else: st.error(f"Slot {slot_id}: Occupied")

        st.markdown("---")
        with st.form("booking_form", clear_on_submit=True):
            selected_slot = st.selectbox("Select Slot ID", available_list)
            user_name = st.text_input("Enter Name", placeholder="Guest")
            if st.form_submit_button("Confirm Booking"):
                if selected_slot:
                    b_id = system.book_parking_slot(selected_slot, user_name)
                    if b_id:
                        st.session_state['msg'] = f"✅ Slot {selected_slot} booked. ID: {b_id}"
                        st.session_state['msg_owner_tab'] = "tab1"
                        st.rerun()

    
    with tab2:
        st.subheader("Release Your Slot")
        with st.form("release_form", clear_on_submit=True):
            booking_id_input = st.text_input("Enter Booking ID").strip().upper()
            if st.form_submit_button("Release Slot"):
                details = system.db.get_booking_by_id(booking_id_input)
                if details:
                    system.release_parking_slot_by_booking_id(booking_id_input)
                    st.session_state['msg'] = f"✅ Slot {details[0]} released."
                    st.session_state['msg_owner_tab'] = "tab2"
                    st.rerun()
                else:
                    st.error("❌ Invalid Booking ID.")

    
    with tab3:
        st.subheader("Admin Control Panel")
        if st.button("RESET ALL SLOTS", type="primary"):
            if system.db.release_all_slots():
                st.session_state['msg'] = "🚨 ADMIN ACTION: All slots reset."
                st.session_state['msg_owner_tab'] = "tab3"
                st.rerun()

        st.markdown("---")
        conn = sqlite3.connect("parking.db")
        st.dataframe(pd.read_sql_query("SELECT * FROM slots", conn), use_container_width=True)
        st.dataframe(pd.read_sql_query("SELECT * FROM bookings", conn), use_container_width=True)
        conn.close()

    
    
    
    if st.session_state['msg']:
        st.markdown("---")
        st.info(st.session_state['msg'])
        
        
        if st.button("Clear Notification"):
            st.session_state['msg'] = None
            st.rerun()

if __name__ == "__main__":
    main()
