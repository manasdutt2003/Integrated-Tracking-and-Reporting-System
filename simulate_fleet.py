import json
import random
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'fleet_stats.json')

ZONES = ['Downtown', 'Suburb A', 'Suburb B', 'Industrial Park', 'Airport']
STATUSES = ['Active', 'Maintenance', 'Inactive', 'Charging']

def update_fleet_simulation():
    # Load existing data or create new structure
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {"fleet": []}
    else:
        # Create directory if needed
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        data = {"fleet": []}
        # Initialize fleet if empty
        for i in range(1, 11):
            data["fleet"].append({
                "bus_id": f"B{1000+i}",
                "route": f"R{10+i}",
                "capacity": 50
            })

    # Update random bus
    bus = random.choice(data["fleet"])
    
    # Simulate movement
    bus["last_updated"] = datetime.now().isoformat()
    bus["current_zone"] = random.choice(ZONES)
    bus["status"] = random.choice([s for s in STATUSES if s != 'Inactive'] + ['Active']*5) # Bias towards Active
    bus["passengers"] = random.randint(0, bus["capacity"])
    bus["fuel_level"] = round(random.uniform(10.0, 100.0), 1)
    
    # Add maintenance log if status is Maintenance
    if bus["status"] == 'Maintenance':
        bus["maintenance_reason"] = random.choice(['Oil Change', 'Tire Pressure', 'Engine Check', 'Cleaning'])
    elif "maintenance_reason" in bus:
        del bus["maintenance_reason"]

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated simulation for Bus {bus['bus_id']}: {bus['status']} at {bus['current_zone']}")

if __name__ == "__main__":
    update_fleet_simulation()
