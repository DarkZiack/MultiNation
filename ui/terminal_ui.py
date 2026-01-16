from data.nation import nation
from data.save_load import load_nation, save_nation
from engine.num_format import abbreviate_number
from engine.world import regions

def get_nation_info(nation_obj):
    return {
        "name": nation_obj.name,
        "population": nation_obj.population,
        "area": nation_obj.area,
        "commercial": nation_obj.commercial,
        "world_region": nation_obj.world_region
    }

def get_nation_display(nation_obj):
    return f"{nation_obj.name}: Population {nation_obj.population}, Area {nation_obj.area} sq km, GDP {nation_obj.commercial}, Region {nation_obj.world_region}"
# Get user input
name = input("Enter nation name: ")
if name == "":
    print("Nation name cannot be empty.")
    exit(1)
print(f"Available regions: {regions()}\n")
world_region = "Aurelia"
area = 100
population = 1000000
commercial = 5000000000
# Save and load nation to demonstrate functionality
nation_obj = nation(name, world_region, area, population, commercial)

load_nation("nations_save.json", name)


# Create nation object
nation_obj = nation(name, world_region, area, population, commercial)

# Display the nation
print(get_nation_display(nation_obj))

input("Press Enter to exit...")
save_nation(nation_obj, "nations_save.json")