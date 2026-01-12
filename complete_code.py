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
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file '{self.db_path}' not found. Please ensure the database exists.")
    
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
    
    def get_booking_by_id(self, booking_id: str) -> Optional[Tuple[str, str]]:
        """Get booking details by booking ID. Returns (slot_id, user_name) or None"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT slot_id, user_name FROM bookings WHERE booking_id = ? AND status = ?',
            (booking_id, 'ACTIVE')
        )
        result = cursor.fetchone()
        conn.close()
        return result if result else None
    
    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE bookings SET status = ? WHERE booking_id = ?',
            (status, booking_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success


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
            print(f"   📋 Booking ID: {booking_id}")
            print(f"   ⚠️  IMPORTANT: Save this Booking ID to release your slot later!")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return booking_id
    
    def release_parking_slot_by_booking_id(self, booking_id: str):
        """Release a parking slot using booking ID"""
        # Validate and sanitize input
        booking_id = booking_id.strip().upper()
        
        # Check for SQL injection patterns
        if any(char in booking_id for char in ["'", '"', ";", "--", "/*"]):
            print(f"\n❌ Error: Invalid characters in booking ID")
            return
        
        # Get booking details
        booking_details = self.db.get_booking_by_id(booking_id)
        
        if not booking_details:
            print(f"\n❌ Error: Booking ID '{booking_id}' not found or already released.")
            return
        
        slot_id, user_name = booking_details
        
        # Acquire lock for this specific slot
        slot_lock = self.get_or_create_lock(slot_id)
        
        with slot_lock:
            # Update slot status to available
            self.db.update_slot_status(slot_id, True)
            
            # Update booking status to completed
            self.db.update_booking_status(booking_id, 'COMPLETED')
            
            print(f"\n✅ Slot {slot_id} has been released successfully!")
            print(f"   User: {user_name}")
            print(f"   Booking ID: {booking_id}")
            print(f"   Released at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


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
        print("  3. Refresh display")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            slot = input("Enter slot ID to book (e.g., A1): ").strip().upper()
            user = input("Enter your name (optional, press Enter for 'Guest'): ").strip() or "Guest"
            system.book_parking_slot(slot, user)
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            booking_id = input("Enter your Booking ID to release the slot: ").strip().upper()
            system.release_parking_slot_by_booking_id(booking_id)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            continue
            
        elif choice == "4":
            print("\n👋 Thank you for using Smart Parking System!")
            system.running = False
            
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 4.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()