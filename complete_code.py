# smart_parking_system.py
"""
Smart Parking System - Enhanced Implementation
Addresses FR-01 through FR-05 and NFR requirements
"""

import threading
import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple
import uuid
import os

class ParkingDatabase:
    """Handles all database operations with SQLite"""
    
    def __init__(self, db_path: str = "parking.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create slots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slots (
                slot_id TEXT PRIMARY KEY,
                is_available INTEGER DEFAULT 1,
                last_updated TIMESTAMP
            )
        ''')
        
        # Create bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id TEXT PRIMARY KEY,
                slot_id TEXT,
                user_name TEXT,
                booking_time TIMESTAMP,
                status TEXT,
                FOREIGN KEY (slot_id) REFERENCES slots(slot_id)
            )
        ''')
        
        # Initialize slots if empty
        cursor.execute('SELECT COUNT(*) FROM slots')
        if cursor.fetchone()[0] == 0:
            initial_slots = [
                ("A1", 1), ("A2", 0), ("A3", 1),
                ("B1", 1), ("B2", 0), ("B3", 1),
                ("C1", 1), ("C2", 1), ("C3", 0)
            ]
            cursor.executemany(
                'INSERT INTO slots (slot_id, is_available, last_updated) VALUES (?, ?, ?)',
                [(slot, avail, datetime.now()) for slot, avail in initial_slots]
            )
        
        conn.commit()
        conn.close()
    
    def get_slot_status(self, slot_id: str) -> Optional[bool]:
        """Get availability status of a specific slot (NFR-P2: <200ms)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT is_available FROM slots WHERE slot_id = ?', (slot_id,))
        result = cursor.fetchone()
        conn.close()
        return bool(result[0]) if result else None
    
    def get_all_slots(self) -> Dict[str, bool]:
        """Get all slots with their availability status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT slot_id, is_available FROM slots ORDER BY slot_id')
        slots = {row[0]: bool(row[1]) for row in cursor.fetchall()}
        conn.close()
        return slots
    
    def update_slot_status(self, slot_id: str, is_available: bool) -> bool:
        """Update slot availability status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE slots SET is_available = ?, last_updated = ? WHERE slot_id = ?',
            (int(is_available), datetime.now(), slot_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def create_booking(self, slot_id: str, user_name: str) -> str:
        """Create a new booking record and return booking ID (FR-05)"""
        booking_id = str(uuid.uuid4())[:8].upper()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO bookings (booking_id, slot_id, user_name, booking_time, status) VALUES (?, ?, ?, ?, ?)',
            (booking_id, slot_id, user_name, datetime.now(), 'ACTIVE')
        )
        conn.commit()
        conn.close()
        return booking_id


class SmartParkingSystem:
    """Main parking system with concurrency control"""
    
    def __init__(self):
        self.db = ParkingDatabase()
        self.slot_locks = {}  # Dictionary to hold locks for each slot (FR-03)
        self.lock_manager = threading.Lock()  # Master lock for lock dictionary
        self.running = True
        
    def get_or_create_lock(self, slot_id: str) -> threading.Lock:
        """Thread-safe lock acquisition for slots (NFR-R1)"""
        with self.lock_manager:
            if slot_id not in self.slot_locks:
                self.slot_locks[slot_id] = threading.Lock()
            return self.slot_locks[slot_id]
    
    def display_parking_status(self):
        """Display real-time parking slot availability (FR-01, NFR-U1)"""
        slots = self.db.get_all_slots()
        
        print("\n" + "="*50)
        print("        SMART PARKING SYSTEM - SLOT STATUS")
        print("="*50)
        
        if not slots:
            print("No parking slots available in the system.")
            return
        
        # Color coding using ANSI escape codes
        GREEN = '\033[92m'
        RED = '\033[91m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
        
        available_count = sum(1 for status in slots.values() if status)
        total_count = len(slots)
        
        print(f"\n{BOLD}Occupancy: {total_count - available_count}/{total_count} slots occupied{RESET}")
        print(f"{GREEN}●{RESET} Available  {RED}●{RESET} Occupied\n")
        
        # Display slots in a grid format
        for slot_id, is_available in sorted(slots.items()):
            color = GREEN if is_available else RED
            status_text = "AVAILABLE" if is_available else "OCCUPIED "
            print(f"  Slot {BOLD}{slot_id}{RESET}: {color}●{RESET} {status_text}")
        
        print("="*50)
    
    def validate_slot(self, slot_id: str) -> Tuple[bool, str]:
        """Validate slot input (NFR-R2)"""
        # Input sanitization
        slot_id = slot_id.strip().upper()
        
        # Check for SQL injection patterns
        if any(char in slot_id for char in ["'", '"', ";", "--", "/*"]):
            return False, "Invalid characters in slot ID"
        
        # Check if slot exists
        if self.db.get_slot_status(slot_id) is None:
            return False, f"Slot '{slot_id}' does not exist"
        
        return True, slot_id
    
    def book_parking_slot(self, slot_id: str, user_name: str = "Guest") -> Optional[str]:
        """
        Book a parking slot with thread-safe locking mechanism (FR-02, FR-03, FR-05)
        Returns booking ID if successful, None otherwise
        """
        # Validate input
        is_valid, result = self.validate_slot(slot_id)
        if not is_valid:
            print(f"\n❌ Error: {result}")
            return None
        
        slot_id = result
        
        # Acquire lock for this specific slot (FR-03: Prevent double booking)
        slot_lock = self.get_or_create_lock(slot_id)
        
        with slot_lock:
            # Check availability within lock
            is_available = self.db.get_slot_status(slot_id)
            
            if not is_available:
                print(f"\n❌ Slot {slot_id} is already occupied. Please choose another slot.")
                return None
            
            # Simulate booking processing time
            time.sleep(0.1)
            
            # Update slot status to occupied
            self.db.update_slot_status(slot_id, False)
            
            # Generate unique booking ID (FR-05)
            booking_id = self.db.create_booking(slot_id, user_name)
            
            print(f"\n✅ SUCCESS! Slot {slot_id} booked for {user_name}")
            print(f"   Booking ID: {booking_id}")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return booking_id
    
    def release_parking_slot(self, slot_id: str):
        """Release a parking slot (FR-04)"""
        # Validate input
        is_valid, result = self.validate_slot(slot_id)
        if not is_valid:
            print(f"\n❌ Error: {result}")
            return
        
        slot_id = result
        
        # Acquire lock for this specific slot
        slot_lock = self.get_or_create_lock(slot_id)
        
        with slot_lock:
            is_available = self.db.get_slot_status(slot_id)
            
            if is_available:
                print(f"\n⚠️  Slot {slot_id} is already available.")
                return
            
            # Update slot status to available
            self.db.update_slot_status(slot_id, True)
            print(f"\n✅ Slot {slot_id} has been released and is now available.")
    
    def simulate_concurrent_bookings(self, slot_id: str, num_users: int = 5):
        """
        Test concurrent booking scenario (NFR-R1)
        Simulates race condition to verify locking mechanism
        """
        print(f"\n{'='*50}")
        print(f"CONCURRENCY TEST: {num_users} users attempting to book slot {slot_id}")
        print(f"{'='*50}")
        
        results = []
        threads = []
        
        def attempt_booking(user_id):
            result = self.book_parking_slot(slot_id, f"User{user_id}")
            results.append((user_id, result is not None))
        
        # Create and start threads
        for i in range(num_users):
            thread = threading.Thread(target=attempt_booking, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        successful = sum(1 for _, success in results if success)
        print(f"\n{'='*50}")
        print(f"CONCURRENCY TEST RESULTS:")
        print(f"  Total attempts: {num_users}")
        print(f"  Successful bookings: {successful}")
        print(f"  Failed attempts: {num_users - successful}")
        print(f"  Status: {'✅ PASS - Only one booking succeeded' if successful == 1 else '❌ FAIL - Race condition detected'}")
        print(f"{'='*50}")


def main():
    """Main program entry point (NFR-U2: Complete booking in <30 seconds)"""
    system = SmartParkingSystem()
    
    print("\n" + "="*50)
    print("     WELCOME TO SMART PARKING SYSTEM")
    print("="*50)
    
    while system.running:
        system.display_parking_status()
        
        print("\n📋 MENU:")
        print("  1. Book a parking slot")
        print("  2. Release a parking slot")
        print("  3. Test concurrent booking (Race Condition)")
        print("  4. Refresh display")
        print("  5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            slot = input("Enter slot ID to book (e.g., A1): ").strip().upper()
            user = input("Enter your name (optional, press Enter for 'Guest'): ").strip() or "Guest"
            system.book_parking_slot(slot, user)
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            slot = input("Enter slot ID to release (e.g., A1): ").strip().upper()
            system.release_parking_slot(slot)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            slot = input("Enter slot ID to test (e.g., A1): ").strip().upper()
            num_users = input("Enter number of concurrent users (default 5): ").strip()
            num_users = int(num_users) if num_users.isdigit() else 5
            system.simulate_concurrent_bookings(slot, num_users)
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            continue
            
        elif choice == "5":
            print("\n👋 Thank you for using Smart Parking System!")
            system.running = False
            
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 5.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()