# 🚗 Smart Parking System 

A robust, real-time parking management web application built with **Streamlit**, **Python**, and **SQLite**. This system allows users to view slot availability, book parking spaces instantly, and release them using a unique Booking ID.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20%2B-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)

---

## ✨ Features

- **📍 Real-time Floor Map**: Visual grid showing which slots are `Available` (Green) or `Occupied` (Red).
- **🔒 Concurrent Booking**: Thread-safe locking mechanism using Python's `threading.Lock` to prevent double-booking.
- **🔓 Easy Release**: Relinquish slots instantly using a generated 8-character unique Booking ID.
- **📊 Admin Control**: Dedicated tab for administrators to monitor live records and perform a full system reset.
- **⚡ Reactive UI**: Statuses update immediately across the app without manual page refreshes using `st.rerun()`.
- **🛡️ Secure Database**: Persistent storage using SQLite with input validation to protect against SQL injection.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (for the interactive web interface)
- **Backend**: Python 3 (Threading for concurrency control)
- **Database**: SQLite3 (Lightweight, serverless relational database)
- **Styling**: Custom CSS for a clean UI (removes default dropdown arrows).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abhinn05/Smart-Parking-System.git](https://github.com/abhinn05/Smart-Parking-System.git)
   cd Smart-Parking-System
   ```
2. **Install dependencies:**
   ```bash
   pip install streamlit pandas
   ```
3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 📖 How to Use

1. **View & Book**:
   - Navigate to the **📍 View & Book** tab.
   - Select an available slot from the dropdown.
   - Enter your name and click **Confirm Booking**.
   - **Save your Booking ID!** You will need it to release the slot later.

2. **Release a Slot**:
   - Navigate to the **🔓 Release Slot** tab.
   - Enter your unique Booking ID and click **Release Slot**.
   - The slot will immediately turn green on the map and the sidebar occupancy will update.

3. **Admin Actions**:
   - Switch to **📊 Admin View** to see full database tables of every booking and slot status.
   - Use the **Reset All Slots** button in the "Danger Zone" to clear the entire parking lot instantly.

---

## 📂 Project Structure

```text
.
├── app.py                   # Main Streamlit web application
├── Smart_Parking_System.py  # Core logic and Database management
├── parking.db               # SQLite Database (Auto-generated)
└── README.md                # Project documentation
```
