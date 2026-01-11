# smart_parking_enhanced.py
# Enhanced Smart Parking System with Data Persistence and Vehicle Tracking

import json
import os
from datetime import datetime

# Data file path
DATA_FILE = os.path.join('..', 'data', 'parking_data.json')

def load_parking_data():
    """Load parking lot data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                print("✓ Parking data loaded from file.")
                return data
        except json.JSONDecodeError:
            print("⚠ Warning: Could not read data file. Using default data.")
            return get_default_parking_lot()
    else:
        print("ℹ No existing data found. Creating new parking lot.")
        return get_default_parking_lot()

def get_default_parking_lot():
    """Return default parking lot configuration"""
    return {
        "A1": {"available": True, "vehicle_id": None, "booked_at": None},
        "A2": {"available": True, "vehicle_id": None, "booked_at": None},
        "B1": {"available": True, "vehicle_id": None, "booked_at": None},
        "B2": {"available": True, "vehicle_id": None, "booked_at": None},
        "C1": {"available": True, "vehicle_id": None, "booked_at": None},
        "C2": {"available": True, "vehicle_id": None, "booked_at": None},
    }

def save_parking_data(parking_lot):
    """Save parking lot data to JSON file"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        with open(DATA_FILE, 'w') as f:
            json.dump(parking_lot, f, indent=4)
        return True
    except Exception as e:
        print(f"✗ Error saving data: {e}")
        return False

# Load parking data at startup
parking_lot = load_parking_data()

def display_parking_status():
    """Display current status of all parking slots"""
    print("\n" + "="*70)
    print("                    PARKING LOT STATUS")
    print("="*70)
    print(f"{'Slot':<8} {'Status':<15} {'Vehicle ID':<20} {'Booked At'}")
    print("-"*70)
    
    available_count = 0
    occupied_count = 0
    
    for slot, data in sorted(parking_lot.items()):
        if data['available']:
            available_count += 1
            status = 'Available ✓'
            vehicle = '-'
            booked = '-'
        else:
            occupied_count += 1
            status = 'Occupied ✗'
            vehicle = data['vehicle_id'] if data['vehicle_id'] else 'Unknown'
            booked = data['booked_at'][:19] if data['booked_at'] else '-'
        
        print(f"{slot:<8} {status:<15} {vehicle:<20} {booked}")
    
    print("-"*70)
    print(f"Total Slots: {len(parking_lot)} | Available: {available_count} | Occupied: {occupied_count}")
    print("="*70)

def validate_slot(slot):
    """Check if slot exists in parking lot"""
    return slot in parking_lot

def validate_vehicle_id(vehicle_id):
    """Validate vehicle ID format"""
    if not vehicle_id or len(vehicle_id.strip()) == 0:
        return False, "Vehicle ID cannot be empty"
    if len(vehicle_id) < 3:
        return False, "Vehicle ID must be at least 3 characters"
    return True, "Valid"

def book_parking_slot(slot, vehicle_id):
    """Book a parking slot if available"""
    # Validate slot
    if not validate_slot(slot):
        print(f"\n✗ Error: Slot '{slot}' does not exist.")
        print(f"   Available slots: {', '.join(sorted(parking_lot.keys()))}")
        return False
    
    # Validate vehicle ID
    is_valid, message = validate_vehicle_id(vehicle_id)
    if not is_valid:
        print(f"\n✗ Error: {message}")
        return False
    
    # Check if slot is available
    if parking_lot[slot]['available']:
        # Check if vehicle is already parked somewhere
        for other_slot, data in parking_lot.items():
            if not data['available'] and data['vehicle_id'] == vehicle_id:
                print(f"\n✗ Error: Vehicle {vehicle_id} is already parked in slot {other_slot}")
                print(f"   Please release that slot first or use a different vehicle ID.")
                return False
        
        # Book the slot
        parking_lot[slot]['available'] = False
        parking_lot[slot]['vehicle_id'] = vehicle_id
        parking_lot[slot]['booked_at'] = datetime.now().isoformat()
        
        if save_parking_data(parking_lot):
            add_to_history(slot, vehicle_id, "book")
            print(f"\n✓ SUCCESS! Slot {slot} booked for vehicle {vehicle_id}")
            print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        else:
            print("\n⚠ Warning: Slot booked but could not save to file.")
            return True
    else:
        vehicle = parking_lot[slot]['vehicle_id']
        booked_time = parking_lot[slot]['booked_at']
        print(f"\n✗ Error: Slot {slot} is already occupied")
        print(f"   Vehicle: {vehicle}")
        if booked_time:
            print(f"   Booked at: {booked_time[:19]}")
        return False


def release_parking_slot(slot):
    """Release an occupied parking slot"""
    if not validate_slot(slot):
        print(f"\n✗ Error: Slot '{slot}' does not exist.")
        print(f"   Available slots: {', '.join(sorted(parking_lot.keys()))}")
        return False
    
    if not parking_lot[slot]['available']:
        vehicle = parking_lot[slot]['vehicle_id']
        booked_at = parking_lot[slot]['booked_at']
        
        # Calculate parking duration
        if booked_at:
            booked_time = datetime.fromisoformat(booked_at)
            duration = datetime.now() - booked_time
            hours = duration.total_seconds() / 3600
            duration_str = f"{hours:.2f} hours"
        else:
            duration_str = "Unknown"
        
        parking_lot[slot]['available'] = True
        parking_lot[slot]['vehicle_id'] = None
        parking_lot[slot]['booked_at'] = None
        
        if save_parking_data(parking_lot):
            add_to_history(slot, vehicle, "release")
            print(f"\n✓ SUCCESS! Slot {slot} has been released")
            print(f"   Vehicle: {vehicle}")
            print(f"   Parking duration: {duration_str}")
            return True
        else:
            print("\n⚠ Warning: Slot released but could not save to file.")
            return True
    else:
        print(f"\n✗ Error: Slot {slot} is already available.")
        return False

def search_available_slots():
    """Display all available parking slots"""
    available = [slot for slot, data in sorted(parking_lot.items()) if data['available']]
    
    print("\n" + "="*50)
    print("            AVAILABLE PARKING SLOTS")
    print("="*50)
    
    if available:
        print(f"\nTotal Available: {len(available)} slot(s)\n")
        for i, slot in enumerate(available, 1):
            print(f"  {i}. Slot {slot}")
    else:
        print("\n  ⚠ PARKING LOT FULL - No slots available!")
        print("  Please wait for a slot to be released.")
    
    print("="*50)
    return available

def search_vehicle(vehicle_id):
    """Search for a vehicle in the parking lot"""
    print("\n" + "="*50)
    print(f"         SEARCHING FOR VEHICLE: {vehicle_id}")
    print("="*50)
    
    found = False
    for slot, data in parking_lot.items():
        if not data['available'] and data['vehicle_id'] == vehicle_id:
            found = True
            print(f"\n✓ Vehicle found!")
            print(f"  Slot: {slot}")
            print(f"  Vehicle ID: {vehicle_id}")
            if data['booked_at']:
                booked_time = datetime.fromisoformat(data['booked_at'])
                duration = datetime.now() - booked_time
                hours = duration.total_seconds() / 3600
                print(f"  Booked at: {data['booked_at'][:19]}")
                print(f"  Duration: {hours:.2f} hours")
            break
    
    if not found:
        print(f"\n✗ Vehicle {vehicle_id} not found in parking lot.")
    
    print("="*50)
    return found

def display_statistics():
    """Display parking lot statistics"""
    total = len(parking_lot)
    available = sum(1 for data in parking_lot.values() if data['available'])
    occupied = total - available
    occupancy_rate = (occupied / total * 100) if total > 0 else 0
    
    print("\n" + "="*50)
    print("           PARKING LOT STATISTICS")
    print("="*50)
    print(f"\nTotal Slots:      {total}")
    print(f"Available:        {available} ({available/total*100:.1f}%)")
    print(f"Occupied:         {occupied} ({occupancy_rate:.1f}%)")
    print(f"Occupancy Rate:   {'█' * int(occupancy_rate/5)}{' ' * (20-int(occupancy_rate/5))} {occupancy_rate:.1f}%")
    
    if occupied > 0:
        print("\nCurrently Parked Vehicles:")
        for slot, data in sorted(parking_lot.items()):
            if not data['available']:
                print(f"  • {slot}: {data['vehicle_id']}")
    
    print("="*50)

HISTORY_FILE = os.path.join('..', 'data', 'booking_history.json')

def load_history():
    """Load booking history"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    """Save booking history"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        return True
    except:
        return False

def add_to_history(slot, vehicle_id, action):
    """Add entry to booking history"""
    history = load_history()
    entry = {
        "slot": slot,
        "vehicle_id": vehicle_id,
        "booked_at": parking_lot[slot]['booked_at'],
        "action": action,
        "timestamp": datetime.now().isoformat()
    }
    
    if action == "release":
        entry["released_at"] = datetime.now().isoformat()
    
    history.append(entry)
    save_history(history)
# Main program
if __name__ == "__main__":
    print("\n" + "="*70)
    print("                   SMART PARKING SYSTEM v2.0")
    print("              (Enhanced with Data Persistence)")
    print("="*70)
    
    while True:
        display_parking_status()
        
        print("\n📋 MENU OPTIONS:")
        print("  1. Book a parking slot")
        print("  2. Release a parking slot")
        print("  3. Search available slots")
        print("  4. Find my vehicle")
        print("  5. View statistics")
        print("  6. Exit")
        
        choice = input("\n👉 Enter your choice (1-6): ").strip()
        
        if choice == "6":
            print("\n" + "="*70)
            print("         Thank you for using Smart Parking System!")
            print("                   ✓ All data has been saved")
            print("="*70)
            break
            
        elif choice == "1":
            print("\n--- BOOK PARKING SLOT ---")
            slot = input("Enter slot ID (e.g., A1, B2, C1): ").strip().upper()
            vehicle_id = input("Enter vehicle number/ID: ").strip().upper()
            book_parking_slot(slot, vehicle_id)
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            print("\n--- RELEASE PARKING SLOT ---")
            slot = input("Enter slot ID to release: ").strip().upper()
            release_parking_slot(slot)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            search_available_slots()
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            print("\n--- FIND VEHICLE ---")
            vehicle_id = input("Enter vehicle number/ID: ").strip().upper()
            search_vehicle(vehicle_id)
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            display_statistics()
            input("\nPress Enter to continue...")
            
        else:
            print("\n✗ Invalid choice. Please enter a number between 1-6.")
            input("\nPress Enter to continue...")