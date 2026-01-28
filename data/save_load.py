from data.nation import nation
import json
import os

"""
(self, name, population, area, income, commerce, commerce_buildings, 
transport, transport_buildings, gdp, gdp_per_capita, tax, world_region=None):


"""

file_path = "data/nations_save.json"

def save_nation(nation_obj, file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # This line handles BOTH cases:
    # - updates if name exists
    # - creates if it doesn't
    data[nation_obj.name] = {
        "name": nation_obj.name,
        "population": nation_obj.population,
        "population_density": nation_obj.population_density,
        "income": nation_obj.income,
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
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_nation(file_path, name):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Save file not found")

    with open(file_path, 'r') as f:
        data = json.load(f)

    if name not in data:
        # Nation does not exist → create new
        return nation(name, 10000, 10000, 0, 0, 0, 0, "Unknown")

    n = data[name]

    return nation(
        n["name"],
        n["population"],
        n["area"],
        n["infrastructure"],
        n["income"],
        n["gdp"],
        n["gdp_per_capita"],
        n["tax"],
        n["commerce"],
        n["transport"],
        n["commerce_buildings"],
        n["transport_buildings"],
        n.get("world_region")
    )



