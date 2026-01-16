from data.nation import nation
from data.save_load import load_nation , save_nation
from engine.num_format import abbreviate_number
from engine.world import regions
import os
import json

# Default nation values
area = 100
population = 1000000
commercial = 5000000000
file_path = "nations_save.json"

# Helper functions
def get_nation_info(nation_obj):
    return {
        "name": nation_obj.name,
        "population": nation_obj.population,
        "area": nation_obj.area,
        "commercial": nation_obj.commercial,
        "world_region": nation_obj.world_region
    }

def get_nation_display(nation_obj):
    return (f"{nation_obj.name}: Population {abbreviate_number(nation_obj.population)}, "
            f"Area {abbreviate_number(nation_obj.area)} sq km, "
            f"GDP {abbreviate_number(nation_obj.commercial)}, "
            f"Region {nation_obj.world_region}")

# Load saved nations
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        saved_nations = json.load(f)
else:
    saved_nations = {}

# Get user input
while True:
    name = input("Enter nation name: ").strip()
    if not name:
        print("Nation name cannot be empty.")
        continue
    if name in saved_nations:
        print(f"Welcome back, {name}!")
        nation_obj = load_nation(file_path, name)
        break
    else:
        print(f"Available regions: {regions()}")
        world_region = input("Enter world region: ").strip()
        if not world_region or world_region not in regions():
            print("Invalid world region.")
            continue
        nation_obj = nation(name, population, area, commercial, world_region)
        break

while True:
    
    # Display the nation
    print(get_nation_display(nation_obj))
    
    # Show game menu
    choice = input("1. Population Upgrade\n 2. Exit Menu\nChoose an option: ")
    if choice == '1':
        nation_obj.population += 100000
        continue
    elif choice == '2':
        print("Saving and exiting...")
    else:
        print("Invalid choice. Please try again.")
        continue
    save_nation(nation_obj, file_path)
    break  # Exit after one loop for simplicity
