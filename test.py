import unittest
import os
import sqlite3
from smart_parking import SmartParkingSystem, ParkingDatabase

class TestSmartParkingFullSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.test_db = "full_system_test.db"
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
            
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE slots (slot_id TEXT PRIMARY KEY, is_available INTEGER, last_updated DATETIME)')
        cursor.execute('CREATE TABLE bookings (booking_id TEXT PRIMARY KEY, slot_id TEXT, user_name TEXT, booking_time DATETIME, status TEXT)')
        
        cls.all_slots = []
        for row in ['A', 'B', 'C']:
            for num in ['1', '2', '3']:
                sid = f"{row}{num}"
                cls.all_slots.append(sid)
                cursor.execute("INSERT INTO slots (slot_id, is_available) VALUES (?, 1)", (sid,))
        conn.commit()
        conn.close()

        cls.system = SmartParkingSystem()
        cls.system.db = ParkingDatabase(db_path=cls.test_db)
        cls.booking_registry = {}

    def test_01_mass_booking_all_slots(self):
        for slot in self.all_slots:
            bid = self.system.book_parking_slot(slot, f"User_{slot}")
            self.assertIsNotNone(bid, f"Failed to book available slot {slot}")
            self.__class__.booking_registry[slot] = bid
            self.assertFalse(self.system.db.get_slot_status(slot))

    def test_02_double_booking_edge_case(self):
        for slot in self.all_slots:
            second_attempt = self.system.book_parking_slot(slot, "Intruder")
            self.assertIsNone(second_attempt, f"System allowed double booking on {slot}!")

    def test_03_invalid_inputs_edge_case(self):
        injections = ["' OR 1=1 --", "D1", "A4", " ", "A1; DROP TABLE slots;"]
        for bad_input in injections:
            res = self.system.book_parking_slot(bad_input)
            self.assertIsNone(res, f"System failed to reject malicious/invalid input: {bad_input}")

    def test_04_partial_release_and_verify(self):
        b_slots = ['B1', 'B2', 'B3']
        for slot in b_slots:
            bid = self.__class__.booking_registry[slot]
            self.system.release_parking_slot_by_booking_id(bid)
            self.assertTrue(self.system.db.get_slot_status(slot))

        for slot in ['A1', 'A2', 'A3', 'C1', 'C2', 'C3']:
            self.assertFalse(self.system.db.get_slot_status(slot), f"Slot {slot} was freed unexpectedly!")

    def test_05_case_sensitivity_release(self):
        a1_bid = self.__class__.booking_registry['A1'].lower()
        self.system.release_parking_slot_by_booking_id(a1_bid)
        self.assertTrue(self.system.db.get_slot_status('A1'))

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

if __name__ == "__main__":
    unittest.main(failfast=True)
