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
    # This line handles BOTH cases:
    # - updates if name exists
    # - creates if it doesn't
    data[nation_obj.name] = {
        "name": nation_obj.name,
        "population": nation_obj.population,
        "population_density": nation_obj.population_density,
        "income": nation_obj.income,
        "balance": nation_obj.balance,
        "tech_income": nation_obj.tech_income,
        "tech": nation_obj.tech_balance,
        "gdp": nation_obj.gdp,
        "gdp_per_capita": nation_obj.gdp_per_capita,
        "area": nation_obj.area,
        "infrastructure": nation_obj.infrastructure,
        "world_region": nation_obj.world_region,
        "tax": nation_obj.tax,
        "commerce": nation_obj.commerce,
        "commerce_buildings": nation_obj.commerce_buildings,
        "transport": nation_obj.transport,
        "transport_buildings": nation_obj.transport_buildings,
        "stability": nation_obj.stability,
        "stability_buildings": nation_obj.stability_buildings,
        "healthcare": nation_obj.healthcare,
        "healthcare_buildings": nation_obj.healthcare_buildings,
        "education": nation_obj.education,
        "education_buildings": nation_obj.education_buildings,
        "safety": nation_obj.safety,
        "safety_buildings": nation_obj.safety_buildings,
        "research_buildings": nation_obj.research_buildings,
        "historic_buildings": nation_obj.historic_buildings,
        "industrial": nation_obj.industrial,
        "industrial_buildings": nation_obj.industrial_buildings,
        "last_save_time": nation_obj.last_save_time
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_nation(file_path, name):
    if not os.path.exists(file_path):
        # create save file with default nations if missing
        ensure_save_exists(file_path)




    with open(file_path, 'r') as f:
        data = json.load(f)

    if name not in data:
        # Nation does not exist → create new with default values
        return nation(name, 1000000, 1000, 1000, 100, 100, 5, 10, 100, 5, 5, 5, 5, 5, 100, 100, 10, "Unknown")

    n = data[name]

    return nation(
        n["name"],
        n["population"],
        n["infrastructure"],
        n["area"],
        n["income"],
        n["balance"],
        n["tech_income"],
        n["tech"],
        n["commerce"],
        n["commerce_buildings"],
        n["transport"],
        n["transport_buildings"],
        n["stability"],
        n["stability_buildings"],
        n["healthcare"],
        n["healthcare_buildings"],
        n["education"],
        n["education_buildings"],
        n["safety"],
        n["safety_buildings"],
        n["research_buildings"],
        n["historic_buildings"],
        n["industrial"],
        n["industrial_buildings"],
        n["gdp"],
        n["gdp_per_capita"],
        n["tax"],
        n.get("world_region")
    )

# Ensure the save exists when this module is imported
ensure_save_exists(file_path)



