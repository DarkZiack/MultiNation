from data.nation import nation
from engine.num_format import abbreviate_number
from data.save_load import load_nation, save_nation

def get_nation_info(nation_obj):
    return {
        "name": nation_obj.name,
        "population": nation_obj.population,
        "area": nation_obj.area,
        "gdp": nation_obj.gdp,
        "region": nation_obj.region
    }

def get_nation_display(nation_obj):
    return f"{nation_obj.name}: Population {abbreviate_number(nation_obj.population)}, Area {abbreviate_number(nation_obj.area)} sq km, GDP {abbreviate_number(nation_obj.gdp)}, Region {nation_obj.region}"

# Get user input
name = input("Enter nation name: ")
if name == "":
    print("Nation name cannot be empty.")
    exit(1)
region = input("Enter nation region: ")
area = 100
population = 1000000
load_nation
save_nation

# Create nation object
nation_obj = nation(name, region, area, population)

# Display the nation
print(get_nation_display(nation_obj))