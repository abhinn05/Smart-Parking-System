# Smart Parking System

A robust, real-time parking management web application built with **Python**, and **SQLite**. This system allows users to view slot availability, book parking spaces instantly, and release them using a unique Booking ID.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite)

---

## Features

- **Real-time Floor Map**: Visual grid showing which slots are `Available` (Green) or `Occupied` (Red).
- **Concurrent Booking**: Thread-safe locking mechanism using Python's `threading.Lock` to prevent double-booking.
- **Easy Release**: Relinquish slots instantly using a generated 8-character unique Booking ID.
- **Admin Control**: Dedicated tab for administrators to monitor live records and perform a full system reset.
- **Secure Database**: Persistent storage using SQLite with input validation to protect against SQL injection.

---

## Tech Stack

- **Backend**: Python 3 (Threading for concurrency control)
- **Database**: SQLite3 (Lightweight, serverless relational database)
- **Styling**: Custom CSS for a clean UI (removes default dropdown arrows).

---

## Getting Started

### Prerequisites

- Python 3.8 or higher installed on your machine.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abhinn05/Smart-Parking-System.git](https://github.com/abhinn05/Smart-Parking-System.git)
   cd Smart-Parking-System
   ```
2. **Setup virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install pandas
   ```
4. **Run the application:**
   ```bash
   python smart_parking.py
   ```
