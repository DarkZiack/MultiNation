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
        "balance": nation_obj.balance,
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
        "tourism_buildings": nation_obj.tourism_buildings,
        "industrial": nation_obj.industrial,
        "industrial_buildings": nation_obj.industrial_buildings,
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_nation(file_path, name):
    if not os.path.exists(file_path):
        raise FileNotFoundError("Save file not found")

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
        n["tourism_buildings"],
        n["industrial"],
        n["industrial_buildings"],
        n["gdp"],
        n["gdp_per_capita"],
        n["tax"],
        n.get("world_region")
    )



