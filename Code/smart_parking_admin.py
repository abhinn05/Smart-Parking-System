# smart_parking_admin.py
# Admin panel with reporting and management features

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

DATA_FILE = os.path.join('..', 'data', 'parking_data.json')
HISTORY_FILE = os.path.join('..', 'data', 'booking_history.json')

def load_parking_data():
    """Load parking lot data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def load_history():
    """Load booking history"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    """Save booking history"""
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def generate_daily_report():
    """Generate daily parking report"""
    parking_lot = load_parking_data()
    history = load_history()
    
    print("\n" + "="*70)
    print("                    DAILY PARKING REPORT")
    print("                  " + datetime.now().strftime("%Y-%m-%d"))
    print("="*70)
    
    # Current status
    total = len(parking_lot)
    if total == 0:
        print("\nNo parking data available.")
        print("="*70)
        return
    
    available = sum(1 for data in parking_lot.values() if data.get('available', True))
    occupied = total - available
    
    print("\n📊 CURRENT STATUS:")
    print(f"   Total Slots:    {total}")
    print(f"   Available:      {available}")
    print(f"   Occupied:       {occupied}")
    print(f"   Occupancy Rate: {(occupied/total*100):.1f}%")
    
    # Revenue calculation (assuming $5 per hour)
    total_revenue = 0
    total_hours = 0
    
    print("\n💰 REVENUE ANALYSIS:")
    for slot, data in parking_lot.items():
        if not data.get('available', True) and data.get('booked_at'):
            try:
                booked_time = datetime.fromisoformat(data['booked_at'])
                duration = (datetime.now() - booked_time).total_seconds() / 3600
                revenue = duration * 5  # $5 per hour
                total_revenue += revenue
                total_hours += duration
            except:
                pass  # Skip invalid entries
    
    print(f"   Active Parking Hours: {total_hours:.2f} hours")
    print(f"   Current Revenue:      ${total_revenue:.2f}")
    print(f"   Average per Vehicle:  ${(total_revenue/occupied if occupied > 0 else 0):.2f}")
    
    # Popular slots
    print("\n🏆 SLOT USAGE STATISTICS:")
    slot_usage = defaultdict(int)
    for entry in history:
        if 'slot' in entry:
            slot_usage[entry['slot']] += 1
    
    if slot_usage:
        sorted_slots = sorted(slot_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (slot, count) in enumerate(sorted_slots, 1):
            print(f"   {i}. Slot {slot}: {count} bookings")
    else:
        print("   No historical data available")
    
    print("="*70)
    
def view_booking_history():
    """View complete booking history"""
    history = load_history()
    
    print("\n" + "="*70)
    print("                    BOOKING HISTORY")
    print("="*70)
    
    if not history:
        print("\nNo booking history available.")
        print("="*70)
        return
    
    print(f"\nTotal Bookings: {len(history)}\n")
    print(f"{'#':<5} {'Slot':<8} {'Vehicle':<15} {'Booked At':<20} {'Released At':<20} {'Duration'}")
    print("-"*70)
    
    for i, entry in enumerate(reversed(history[-20:]), 1):  # Show last 20
        slot = entry.get('slot', 'N/A')
        vehicle = entry.get('vehicle_id', 'N/A')
        
        # Handle booked_at safely
        booked_at = entry.get('booked_at')
        if booked_at:
            booked = booked_at[:19] if len(booked_at) >= 19 else booked_at
        else:
            booked = 'N/A'
        
        # Handle released_at safely
        released_at = entry.get('released_at')
        if released_at:
            released = released_at[:19] if len(released_at) >= 19 else released_at
        else:
            released = 'Still Parked'
        
        # Calculate duration
        if released_at and booked_at:
            try:
                duration_sec = (datetime.fromisoformat(released_at) - 
                              datetime.fromisoformat(booked_at)).total_seconds()
                duration = f"{duration_sec/3600:.2f}h"
            except:
                duration = "N/A"
        else:
            duration = "Ongoing"
        
        print(f"{i:<5} {slot:<8} {vehicle:<15} {booked:<20} {released:<20} {duration}")
    
    print("="*70)

def reset_parking_lot():
    """Reset all parking slots (Admin function)"""
    print("\n⚠️  WARNING: This will release ALL parking slots!")
    confirm = input("Type 'RESET' to confirm: ").strip()
    
    if confirm == "RESET":
        default_lot = {
            "A1": {"available": True, "vehicle_id": None, "booked_at": None},
            "A2": {"available": True, "vehicle_id": None, "booked_at": None},
            "B1": {"available": True, "vehicle_id": None, "booked_at": None},
            "B2": {"available": True, "vehicle_id": None, "booked_at": None},
            "C1": {"available": True, "vehicle_id": None, "booked_at": None},
            "C2": {"available": True, "vehicle_id": None, "booked_at": None},
        }
        
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(default_lot, f, indent=4)
            print("\n✓ Parking lot has been reset successfully!")
            return True
        except Exception as e:
            print(f"\n✗ Error resetting parking lot: {e}")
            return False
    else:
        print("\n✗ Reset cancelled.")
        return False

def add_parking_slot():
    """Add new parking slot (Admin function)"""
    parking_lot = load_parking_data()
    
    print("\n--- ADD NEW PARKING SLOT ---")
    slot_id = input("Enter new slot ID (e.g., D1, D2): ").strip().upper()
    
    if slot_id in parking_lot:
        print(f"\n✗ Error: Slot {slot_id} already exists!")
        return False
    
    parking_lot[slot_id] = {
        "available": True,
        "vehicle_id": None,
        "booked_at": None
    }
    
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(parking_lot, f, indent=4)
        print(f"\n✓ Slot {slot_id} added successfully!")
        return True
    except Exception as e:
        print(f"\n✗ Error adding slot: {e}")
        return False

def remove_parking_slot():
    """Remove parking slot (Admin function)"""
    parking_lot = load_parking_data()
    
    print("\n--- REMOVE PARKING SLOT ---")
    slot_id = input("Enter slot ID to remove: ").strip().upper()
    
    if slot_id not in parking_lot:
        print(f"\n✗ Error: Slot {slot_id} does not exist!")
        return False
    
    if not parking_lot[slot_id]['available']:
        print(f"\n✗ Error: Cannot remove occupied slot {slot_id}")
        print(f"   Vehicle {parking_lot[slot_id]['vehicle_id']} is currently parked.")
        return False
    
    confirm = input(f"Confirm removal of slot {slot_id}? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        del parking_lot[slot_id]
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(parking_lot, f, indent=4)
            print(f"\n✓ Slot {slot_id} removed successfully!")
            return True
        except Exception as e:
            print(f"\n✗ Error removing slot: {e}")
            return False
    else:
        print("\n✗ Removal cancelled.")
        return False

def export_report_to_file():
    """Export parking report to text file"""
    parking_lot = load_parking_data()
    history = load_history()
    
    filename = f"parking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join('..', 'Documentation', filename)
    
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write("="*70 + "\n")
            f.write("           SMART PARKING SYSTEM - DETAILED REPORT\n")
            f.write(f"           Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            # Current status
            total = len(parking_lot)
            available = sum(1 for data in parking_lot.values() if data['available'])
            occupied = total - available
            
            f.write("CURRENT PARKING STATUS:\n")
            f.write("-"*70 + "\n")
            for slot, data in sorted(parking_lot.items()):
                status = "Available" if data['available'] else f"Occupied by {data['vehicle_id']}"
                f.write(f"Slot {slot}: {status}\n")
            
            f.write("\nSTATISTICS:\n")
            f.write(f"Total Slots: {total}\n")
            f.write(f"Available: {available}\n")
            f.write(f"Occupied: {occupied}\n")
            f.write(f"Occupancy Rate: {(occupied/total*100):.1f}%\n\n")
            
            # History
            f.write("\nBOOKING HISTORY (Last 50 entries):\n")
            f.write("-"*70 + "\n")
            for entry in history[-50:]:
                f.write(f"Slot: {entry['slot']}, Vehicle: {entry['vehicle_id']}, ")
                f.write(f"Booked: {entry['booked_at'][:19]}\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("End of Report\n")
        
        print(f"\n✓ Report exported successfully!")
        print(f"   File: {filepath}")
        return True
        
    except Exception as e:
        print(f"\n✗ Error exporting report: {e}")
        return False

# Main Admin Panel
if __name__ == "__main__":
    print("\n" + "="*70)
    print("              SMART PARKING SYSTEM - ADMIN PANEL")
    print("="*70)
    
    # Simple password protection
    password = input("\nEnter admin password: ").strip()
    
    if password != "admin123":  # Simple password for demo
        print("\n✗ Access Denied! Incorrect password.")
        exit()
    
    print("\n✓ Access Granted!\n")
    
    while True:
        print("\n" + "="*70)
        print("                        ADMIN MENU")
        print("="*70)
        print("\n📊 REPORTS:")
        print("  1. Generate Daily Report")
        print("  2. View Booking History")
        print("  3. Export Report to File")
        print("\n🔧 MANAGEMENT:")
        print("  4. Add New Parking Slot")
        print("  5. Remove Parking Slot")
        print("  6. Reset All Slots (Clear All)")
        print("\n  7. Exit Admin Panel")
        
        choice = input("\n👉 Enter your choice (1-7): ").strip()
        
        if choice == "7":
            print("\n✓ Exiting Admin Panel. Goodbye!")
            break
        elif choice == "1":
            generate_daily_report()
            input("\nPress Enter to continue...")
        elif choice == "2":
            view_booking_history()
            input("\nPress Enter to continue...")
        elif choice == "3":
            export_report_to_file()
            input("\nPress Enter to continue...")
        elif choice == "4":
            add_parking_slot()
            input("\nPress Enter to continue...")
        elif choice == "5":
            remove_parking_slot()
            input("\nPress Enter to continue...")
        elif choice == "6":
            reset_parking_lot()
            input("\nPress Enter to continue...")
        else:
            print("\n✗ Invalid choice. Please enter 1-7.")
            input("\nPress Enter to continue...")