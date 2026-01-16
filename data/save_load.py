from data.nation import nation
import json
import os

def save_nation(nation_obj, file_path):
    # Load existing data if file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    # Save or update by nation name
    data[nation_obj.name] = {
        "population": nation_obj.population,
        "area": nation_obj.area,
        "commercial": nation_obj.commercial,
        "world_region": nation_obj.world_region
    }

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_nation(file_path, name):
    with open(file_path, 'r') as f:
        data = json.load(f)

    if name not in data:
        raise ValueError(f"Nation '{name}' not found")

    n = data[name]
    return nation(
        name,
        n["population"],
        n["area"],
        n["commercial"],
        n["world_region"]
    )

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
        "population": nation_obj.population,
        "area": nation_obj.area,
        "commercial": nation_obj.commercial,
        "world_region": nation_obj.world_region
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
        return nation(name, 10000, 10000, 10000, "Unknown")

    # Nation exists → load it
    n = data[name]
    return nation(
        name,
        n["population"],
        n["area"],
        n["commercial"],
        n["world_region"]
    )


