from data.nation import nation
import json
import os
import time
"""
(self, name, population, area, income, commerce, commerce_buildings, 
transport, transport_buildings, gdp, gdp_per_capita, tax, world_region=None):


"""

file_path = os.path.join(os.path.dirname(__file__), "nations_save.json")

def ensure_save_exists(file_path):
    """Ensure the save file exists; if not, create it with 15 default nations."""
    dirpath = os.path.dirname(file_path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    if os.path.exists(file_path):
        return

    defaults = {}
    for i in range(1, 16):
        name = f"Nation {i}"
        defaults[name] = {
            "name": name,
            "population": 50000,
            "population_density": 100,
            "income": 100,
            "balance": 100,
            "tech_income": 10,
            "tech": 0,
            "gdp": 1000,
            "gdp_per_capita": 1000,
            "area": 1000,
            "infrastructure": 50,
            "world_region": "Unknown",
            "tax": 10,
            "commerce": 50,
            "commerce_buildings": 1,
            "transport": 50,
            "transport_buildings": 1,
            "stability": 50,
            "stability_buildings": 1,
            "healthcare": 50,
            "healthcare_buildings": 1,
            "education": 50,
            "education_buildings": 1,
            "safety": 50,
            "safety_buildings": 1,
            "research_buildings": 1,
            "historic_buildings": 1,
            "industrial": 50,
            "industrial_buildings": 1,
        }

    with open(file_path, 'w') as f:
        json.dump(defaults, f, indent=4)

def save_nation(nation_obj, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    nation_obj.last_save_time = time.time()
    # Use nation serialization helper for consistency
    data[nation_obj.name] = nation_obj.to_dict()

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_nation(file_path, name):
    if not os.path.exists(file_path):
        # create save file with default nations if missing
        ensure_save_exists(file_path)




    with open(file_path, 'r') as f:
        data = json.load(f)

    if name not in data:
        # Nation does not exist → create new with sensible defaults
        defaults = {
            "name": name,
            "population": 1000000,
            "infrastructure": 1000,
            "area": 1000,
            "income": 100,
            "balance": 100,
            "tech_income": 5,
            "tech": 10,
            "commerce": 100,
            "commerce_buildings": 5,
            "transport": 5,
            "transport_buildings": 5,
            "stability": 5,
            "stability_buildings": 5,
            "healthcare": 100,
            "healthcare_buildings": 100,
            "education": 10,
            "education_buildings": 0,
            "safety": 100,
            "safety_buildings": 0,
            "research_buildings": 0,
            "historic_buildings": 0,
            "industrial": 100,
            "industrial_buildings": 0,
            "gdp": 100,
            "gdp_per_capita": 100,
            "tax": 10,
            "world_region": "Unknown",
        }
        # persist the default so next load finds it
        data[name] = defaults
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        return nation.from_dict(defaults)

    n = data[name]
    return nation.from_dict(n)

# Ensure the save exists when this module is imported
ensure_save_exists(file_path)



