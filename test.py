import unittest
import os
import sqlite3
import threading
import time
from complete_code import SmartParkingSystem, ParkingDatabase

class TestSmartParkingSystem(unittest.TestCase):   
    @classmethod
    def setUpClass(cls):
        """Create a dummy database for testing"""
        cls.test_db = "test_parking.db"  
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
            
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE slots (
                slot_id TEXT PRIMARY KEY,
                is_available INTEGER,
                last_updated DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE bookings (
                booking_id TEXT PRIMARY KEY,
                slot_id TEXT,
                user_name TEXT,
                booking_time DATETIME,
                status TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO slots VALUES ('A1', 1, '2023-01-01')")
        cursor.execute("INSERT INTO slots VALUES ('A2', 1, '2023-01-01')")
        conn.commit()
        conn.close()

    def setUp(self):
        """Initialize system pointing to test database""" 
        self.system = SmartParkingSystem()
        self.system.db = ParkingDatabase(db_path=self.test_db)

    def test_booking_success(self):
        """Test basic successful booking (FR-02)"""
        booking_id = self.system.book_parking_slot("A1", "Alice")
        self.assertIsNotNone(booking_id)
        self.assertFalse(self.system.db.get_slot_status("A1"))

    def test_double_booking_prevention(self):
        """Test that an occupied slot cannot be booked (FR-03)"""
        self.system.book_parking_slot("A2", "Bob")
        second_booking = self.system.book_parking_slot("A2", "Charlie")
        self.assertIsNone(second_booking)

    def test_release_slot(self):
        """Test releasing a slot via booking ID (FR-05)"""
        self.system.db.update_slot_status("A1", True)      
        booking_id = self.system.book_parking_slot("A1", "Alice")    
        self.assertIsNotNone(booking_id, "Booking failed, returned None")     
        self.system.release_parking_slot_by_booking_id(booking_id)
        self.assertTrue(self.system.db.get_slot_status("A1"))

    def test_invalid_slot_validation(self):
        """Test validation for non-existent slots (NFR-R2)"""
        is_valid, msg = self.system.validate_slot("Z99")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", msg)

    def test_concurrency_race_condition(self):
        """Test high-concurrency: multiple threads trying to book the same slot"""
        results = []
        slot_to_book = "A2"
        self.system.db.update_slot_status(slot_to_book, True)

        def attempt_booking():
            res = self.system.book_parking_slot(slot_to_book, "ThreadUser")
            if res:
                results.append(res)

        threads = []
        for _ in range(10): 
            t = threading.Thread(target=attempt_booking)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(len(results), 1, "Concurrency Error: Multiple users booked the same slot!")

    @classmethod
    def tearDownClass(cls):
        """Clean up the test database file"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

if __name__ == "__main__":
    unittest.main()
