import json
import random
from datetime import datetime
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'fleet_stats.json')

ROUTES = ['Route A', 'Route B', 'Route C', 'Route D', 'Express Line']
STATUSES = ['On Time', 'Delayed', 'Maintenance', 'Out of Service']

def generate_stats():
    today = datetime.now().strftime('%Y-%m-%d')
    
    stats = {
        "date": today,
        "total_active_buses": random.randint(20, 50),
        "busiest_route": random.choice(ROUTES),
        "average_delay_minutes": round(random.uniform(0, 15), 1),
        "maintenance_schedule": f"{random.randint(1, 5)} buses scheduled",
        "passenger_satisfaction": f"{random.randint(85, 99)}%"
    }

    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Successfully generated fleet stats for {today}: {stats}")
    except Exception as e:
        print(f"Error generating stats: {e}")
        exit(1)

if __name__ == "__main__":
    generate_stats()
