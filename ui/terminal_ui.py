import pygame
import os
import json
import math
import time
from data.nation import nation
from data.save_load import load_nation, save_nation
from engine.num_format import abbreviate_number
from engine.world import regions

#   CONFIG --------------------
WIDTH, HEIGHT = 1920, 1080
FPS = 60

spectated_nation = None

population_growth_per_minute = 5000
file_path = "data/nations_save.json"

# PANEL CONFIG -------------------- 
PANEL_WIDTH = 350
PANEL_CLOSED_X = WIDTH
PANEL_OPEN_X = WIDTH - PANEL_WIDTH
PANEL_ANIMATION_SPEED = 20
PANEL_TABS = ["Buildings", "Investments", "Tech", "Warfare", "Leaderboard"]

# Tech base costs per key
TECH_BASE_COSTS = {
    "commerce": 1000,
    "transport": 1200,
    "stability": 1500,
    "healthcare": 1300,
    "education": 1100,
    "safety": 900,
    "research": 2000,
    "historic": 800,
    "industrial": 1400,
    "infrastructure_cost": 2500,
    "tech_gain": 3000,
    "tech_cost": 4000,
    "building_slots": 5000,
}
# Nation Search
user_search = ""
search_active = False
search_message = ""

# INIT --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nation Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 40)

#   LOAD SAVE DATA --------------------
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        saved_nations = json.load(f)
else:
    saved_nations = {}

# -------------------- NATION SETUP (PYGAME MENU)  
input_text = ""
active_input = "land"
quantityland_input = ""
quantityinfra_input = ""
phase = "name"  # name -> region -> done
message = ""
nation_obj = None
# PANEL STATE ----
panel_is_open = False
panel_x = PANEL_CLOSED_X
panel_screen = "nation"


region_index = 0  # Track which region is selected
available_regions = regions()  # List of regions

def draw_text(surface, text, pos, color=(255,255,255), big=False):
    txt_surf = big_font.render(text, True, color) if big else font.render(text, True, color)
    surface.blit(txt_surf, pos)

def get_nation_projections(nation, overrides=None):
    """
    Calculates nation stats. 
    Use 'overrides' to simulate adding a building (e.g., {'commerce': +1})
    """
    # Use current buildings as base, apply overrides if they exist
    b = {
        "comm": nation.commerce_buildings,
        "trans": nation.transport_buildings,
        "ind": nation.industrial_buildings,
        "edu": nation.education_buildings,
        "safe": nation.safety_buildings,
        "health": nation.healthcare_buildings,
        "stab": nation.stability_buildings,
        "hist": nation.historic_buildings
    }
    if overrides:
        for key, val in overrides.items():
            b[key] += val

    # --- 1. Calculate Developments (Denominators) ---
    comm_dev = max(1, 2 * (nation.infrastructure + (nation.area / 10)))
    trans_dev = max(1, nation.infrastructure * (1 + 0/20) + 0 + (nation.infrastructure + nation.area) / 10)
    edu_dev  = max(1, 2 * (nation.infrastructure + (nation.area / 10)))
    safe_dev = max(1, 2 * (nation.population / 100))
    health_dev = max(1, 2 * (nation.population / 100))
    ind_dev  = max(1, 2 * (nation.infrastructure + (nation.area / 10)))
    stab_dev = max(1, 2 * (nation.infrastructure + (nation.area / 10)))

    # --- 2. Apply Tech Multipliers ---
    e_comm   = b["comm"] * nation.get_tech_multiplier("commerce")
    e_trans  = b["trans"] * nation.get_tech_multiplier("transport")
    e_ind    = b["ind"] * nation.get_tech_multiplier("industrial")
    e_edu    = b["edu"] * nation.get_tech_multiplier("education")
    e_hist   = b["hist"] * nation.get_tech_multiplier("historic")
    e_safe   = b["safe"] * nation.get_tech_multiplier("safety")
    e_health = b["health"] * nation.get_tech_multiplier("healthcare")
    e_stab   = b["stab"] * nation.get_tech_multiplier("stability")

    # --- 3. Core Formulas ---
    res = {}
    res["commerce"] = 100 * math.sqrt(((e_comm * 3.33) * (nation.transport-100) + ((nation.industrial-100)/2)) / comm_dev) + (e_comm * 10000) / comm_dev + 100
    res["transport"] = 100 * math.sqrt((e_trans * 4.55) / trans_dev) + (e_trans * 10000) / trans_dev + 100
    res["industrial"] = 100 * math.sqrt((e_ind * 2.9) / ind_dev) + (e_ind * 10000) / ind_dev + 100
    res["safety"] = 100 * math.sqrt((e_safe * 3.35) / safe_dev) + (e_safe * 10000) / safe_dev + 100
    res["healthcare"] = 100 * math.sqrt((e_health * 4.55) / health_dev) + (e_health * 10000) / health_dev + 100
    
    # Education involves both building types
    res["education"] = 100 * math.sqrt(((e_edu + e_hist) * 5.33 * nation.safety) / edu_dev) + (e_edu * 10000 + e_hist * 5000) / edu_dev + 100
    
    # Stability relies on the results above
    res["stability"] = ((res["commerce"] + res["transport"] + res["education"] + res["healthcare"] + res["safety"] / 5) / stab_dev) + (100 * math.sqrt((e_stab * 1000) / stab_dev)) + 100

    return res

setup_done = False
while not setup_done:
    screen.fill((30, 30, 30))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if phase == "name":
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    name = input_text.strip()
                    if not name:
                        message = "Nation name cannot be empty."
                    elif name in saved_nations:
                        message = f"Welcome back, {name}!"
                        nation_obj = load_nation(file_path, name)
                        if nation_obj and hasattr(nation_obj, 'last_save_time'):
                            current_time = time.time()
                            elapsed_seconds = current_time - nation_obj.last_save_time
                            elapsed_minutes = elapsed_seconds / 60
                            if elapsed_minutes >= 1:
                                proc_mins = min(int(elapsed_minutes), 1440)  # Cap at 24 hours and use integer minutes
                                # Compute gains
                                pop_gain = (nation_obj.population * 0.015) * (nation_obj.healthcare / 100) * proc_mins
                                money_gain = (nation_obj.income / 1440) * proc_mins
                                tech_gain = (nation_obj.tech_income / 1440) * proc_mins
                                nation_obj.population += pop_gain
                                nation_obj.balance += money_gain
                                nation_obj.tech_balance += tech_gain
                                # Show a concise offline summary to the player
                                message = f"Welcome back, {name}! Away {proc_mins}m: +{abbreviate_number(pop_gain)} pop, +${abbreviate_number(money_gain)}, +{abbreviate_number(tech_gain)} tech"
                        setup_done = True
                    elif len(name) > 15:
                        message = "Nation name too long (max 15 characters)."
                    elif len(name) < 2:
                        message = "Nation name too short (min 3 characters)."
                    else:
                        phase = "region"
                        message = "Use UP/DOWN keys to select region and press ENTER"
                else:
                    input_text += event.unicode
            elif phase == "region":
                if event.key == pygame.K_UP:
                    region_index = (region_index - 1) % len(available_regions)
                elif event.key == pygame.K_DOWN:
                    region_index = (region_index + 1) % len(available_regions)
                elif event.key == pygame.K_RETURN:
                    selected_region = available_regions[region_index]
                    nation_obj = nation.from_dict({
                        "name": input_text.strip(),
                        "population": 100000,
                        "infrastructure": 1000,
                        "area": 1000,
                        "income": 100,
                        "balance": 10000000,
                        "tech_income": 100,
                        "tech": 0,
                        "commerce": 100,
                        "commerce_buildings": 0,
                        "transport": 100,
                        "transport_buildings": 0,
                        "stability": 100,
                        "stability_buildings": 0,
                        "healthcare": 100,
                        "healthcare_buildings": 0,
                        "education": 100,
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
                        "world_region": selected_region,
                    })
                    """
                (self, name, population, infrastructure, area, income, balance, commerce, commerce_buildings, 
                transport, transport_buildings, stability, stability_buildings, healthcare, healthcare_buildings
                , education, education_buildings, safety, safety_buildings , research_buildings, turism_buildings, industrial,
                industrial_buildings, gdp, gdp_per_capita, tax, world_region=None):
                    """
                    setup_done = True

    # Draw input interface ----
    if phase == "name":
        draw_text(screen, "Enter nation name:", (50, 50), big=True)
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(45, 95, 200, 30))
        draw_text(screen, input_text, (50, 100))
    else:
        draw_text(screen, "Select a world region:", (50, 50), big=True)
        draw_text(screen, message, (50, 100), color=(255, 200, 200))
        # Draw each region
        start_y = 150
        for i, region_name in enumerate(available_regions):
            color = (255, 255, 0) if i == region_index else (220, 220, 220)
            draw_text(screen, f"{region_name}", (70, start_y + i * 40), color=color)

    pygame.display.flip()
    clock.tick(FPS)

#  UI ELEMENTS ----
upgrade_button = pygame.Rect(50, 480, 300, 50)
exit_button = pygame.Rect(WIDTH - 350, HEIGHT - 100, 300, 50)
# Buildings

commerce_button = pygame.Rect(315, 250, 300, 50)
transport_button = pygame.Rect(315, 600, 300, 50)
industrial_button = pygame.Rect(315, 950, 300, 50)

education_button = pygame.Rect(935, 250, 300, 50) 
safety_button = pygame.Rect(935, 600, 300, 50)
historic_button = pygame.Rect(935, 950, 300, 50)

research_button = pygame.Rect(1555, 250, 300, 50)
healthcare_button = pygame.Rect(1555, 600, 300, 50)
stability_button = pygame.Rect(1555, 950, 300, 50)


commercial_image = pygame.image.load("data/assets/commercial.jpg")
transport_image = pygame.image.load("data/assets/transport.jpg")
education_image = pygame.image.load("data/assets/education.jpg")
healthcare_image = pygame.image.load("data/assets/healthcare.jpg")
safety_image = pygame.image.load("data/assets/safety.jpg")
stability_image = pygame.image.load("data/assets/stability.jpg")
industrial_image = pygame.image.load("data/assets/industry.jpg")
research_image = pygame.image.load("data/assets/research.jpg")
historic_image = pygame.image.load("data/assets/historic.jpg")

IMAGE_SIZE_BUILDINGS = (225, 225)

commercial_image = pygame.transform.smoothscale(pygame.image.load("data/assets/commercial.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
transport_image = pygame.transform.smoothscale(pygame.image.load("data/assets/transport.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
education_image = pygame.transform.smoothscale(pygame.image.load("data/assets/education.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
healthcare_image = pygame.transform.smoothscale(pygame.image.load("data/assets/healthcare.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
safety_image = pygame.transform.smoothscale(pygame.image.load("data/assets/safety.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
stability_image = pygame.transform.smoothscale(pygame.image.load("data/assets/stability.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
industrial_image = pygame.transform.smoothscale(pygame.image.load("data/assets/industry.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
research_image = pygame.transform.smoothscale(pygame.image.load("data/assets/research.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
historic_image = pygame.transform.smoothscale(pygame.image.load("data/assets/historic.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)

# Investments
land_button = pygame.Rect(100, 390, 480, 50)
infrastructure_button = pygame.Rect(720, 390, 480, 50)

infrastructure_image = pygame.image.load("data/assets/infrastructure.jpg")
area_image = pygame.image.load("data/assets/area.jpg")

IMAGE_SIZE_INVESTMENTS = (480, 270)

infrastructure_image = pygame.transform.smoothscale(pygame.image.load("data/assets/infrastructure.jpg").convert_alpha(),IMAGE_SIZE_INVESTMENTS)
area_image = pygame.transform.smoothscale(pygame.image.load("data/assets/area.jpg").convert_alpha(),IMAGE_SIZE_INVESTMENTS)

# MAIN LOOP ----
running = True
timer = 0
timer_minute = 0

#  Economic Stats 

commerce_income = 0
tax_income = 0


while running:
    timer += 1
    if timer == 62:
        timer_minute += 1
        timer = 0
    
    # Panel Animation ----
    target_x = PANEL_OPEN_X if panel_is_open else PANEL_CLOSED_X
    if panel_x != target_x:
        if panel_x < target_x:
            panel_x = min(panel_x + PANEL_ANIMATION_SPEED, target_x)
        else:
            panel_x = max(panel_x - PANEL_ANIMATION_SPEED, target_x)

    # Events ----
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_nation(nation_obj, file_path)
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if exit_button.collidepoint(event.pos):
                save_nation(nation_obj, file_path)
                running = False
            # Buildings
            if panel_screen == "buildings":
                search_active = False
                if used_building_slots < nation_obj.building_slots:
                    if commerce_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.commerce_buildings))):
                        nation_obj.commerce_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.commerce_buildings)
                    elif transport_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.transport_buildings))):
                        nation_obj.transport_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.transport_buildings)
                    elif stability_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.stability_buildings))):
                        nation_obj.stability_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.stability_buildings)
                    elif healthcare_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.healthcare_buildings))):
                        nation_obj.healthcare_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.healthcare_buildings)
                    elif education_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.education_buildings))):
                        nation_obj.education_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.education_buildings)
                    elif safety_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.safety_buildings))):
                        nation_obj.safety_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.safety_buildings)
                    elif research_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.research_buildings))):
                        nation_obj.research_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.research_buildings)
                    elif industrial_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.industrial_buildings))):
                        nation_obj.industrial_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.industrial_buildings)
                    elif historic_button.collidepoint(event.pos) and (nation_obj.balance >= (100_000 * (1.08 ** nation_obj.historic_buildings))):
                        nation_obj.historic_buildings += 1
                        nation_obj.balance -= 100_000 * (1.08 ** nation_obj.historic_buildings)
            
            used_building_slots = (
                nation_obj.commerce_buildings + nation_obj.transport_buildings
                + nation_obj.stability_buildings + nation_obj.healthcare_buildings
                + nation_obj.education_buildings + nation_obj.safety_buildings
                + nation_obj.research_buildings + nation_obj.industrial_buildings + nation_obj.historic_buildings
            )
            # Dev
            if panel_screen == "investments":
                if land_button.collidepoint(event.pos):
                    qty = float(quantityland_input) if quantityland_input else 0
                    base_land_cost = (qty * (nation_obj.area / 100) ** 2) / 2
                    land_discount = nation_obj.get_cost_multiplier('land_cost')
                    land_cost = base_land_cost * land_discount
                    if qty > 0 and nation_obj.balance >= land_cost:
                        nation_obj.balance -= land_cost
                        nation_obj.area += qty
                        quantityland_input = ""
                if infrastructure_button.collidepoint(event.pos):
                    qty = float(quantityinfra_input) if quantityinfra_input else 0
                    infra_discount = nation_obj.get_cost_multiplier('infrastructure_cost', per_level=0.005, min_mult=0.2)
                    infra_cost = infrastructure_cost_reduction * qty * (nation_obj.infrastructure / 100) ** 2 * infra_discount
                    if qty > 0 and nation_obj.balance >= infra_cost:
                        nation_obj.balance -= infra_cost
                        nation_obj.infrastructure += qty
                        quantityinfra_input = ""
            infrastructure_cost_reduction = max((nation_obj.infrastructure / (nation_obj.area*0.9)) ** 2, 0)

            # UI cost multipliers
            infra_display_discount = nation_obj.get_cost_multiplier('infrastructure_cost', per_level=0.005, min_mult=0.2)

            # Panel events: dynamic toggle attached to panel edge
            toggle_rect = pygame.Rect(int(panel_x) - 40, 0, 40, 50)
            if toggle_rect.collidepoint(event.pos):
                panel_is_open = not panel_is_open

            if panel_x < WIDTH:  # Panel is visible (or sliding)
            # Panel navigation screens
                nation_screen_button = pygame.Rect(panel_x + 20, 70, PANEL_WIDTH -40, 50)
                buildings_screen_button = pygame.Rect(panel_x + 20, 140, PANEL_WIDTH - 40, 50)
                investments_screen_button = pygame.Rect(panel_x + 20, 210, PANEL_WIDTH - 40, 50)
                tech_screen_button = pygame.Rect(panel_x + 20, 280, PANEL_WIDTH - 40, 50)
                warfare_screen_button = pygame.Rect(panel_x + 20, 350, PANEL_WIDTH - 40, 50)
                leaderboard_screen_button = pygame.Rect(panel_x + 20, 840, PANEL_WIDTH - 40, 50)
                if nation_screen_button.collidepoint(event.pos):
                    panel_screen = "nation"
                    spectated_nation = None
                    search_message = ""
                elif buildings_screen_button.collidepoint(event.pos):
                    panel_screen = "buildings"
                    spectated_nation = None
                    search_message = ""
                elif investments_screen_button.collidepoint(event.pos):
                    panel_screen = "investments"
                    spectated_nation = None
                    search_message = ""
                elif tech_screen_button.collidepoint(event.pos):
                    panel_screen = "tech"
                    spectated_nation = None
                    search_message = ""
                elif warfare_screen_button.collidepoint(event.pos):
                    panel_screen = "warfare"
                    spectated_nation = None
                    search_message = ""
                elif leaderboard_screen_button.collidepoint(event.pos):
                    panel_screen = "leaderboard"
                    spectated_nation = None
                    search_message = ""
                # Activate search box if clicked
                search_box = pygame.Rect(panel_x + 20, 950, PANEL_WIDTH - 40, 50)
                if search_box.collidepoint(event.pos):
                    search_active = True
                else:
                    search_active = False

            # Tech panel purchases
            if panel_screen == "tech":
                # define UI positions for tech list
                tech_start_x = 100
                tech_start_y = 150
                tech_width = 500
                tech_height = 48
                gap = 12
                tech_items = [
                    ("commerce", "Commerce"),
                    ("transport", "Transport"),
                    ("industrial", "Industry"),
                    ("education", "Education"),
                    ("healthcare", "Healthcare"),
                    ("safety", "Safety"),
                    ("research", "Research"),
                    ("infrastructure_cost", "Infra Cost"),
                    ("tech_gain", "Tech Gain"),
                    ("tech_cost", "Tech Cost Discount"),
                    ("building_slots", "Building Slots"),
                    ("land_cost", "Land Cost Reduction"),
                ]
                for i, (key, label) in enumerate(tech_items):
                    y = tech_start_y + i * (tech_height + gap)
                    buy1_rect = pygame.Rect(tech_start_x + tech_width + 20, y, 100, tech_height)
                    buy5_rect = pygame.Rect(tech_start_x + tech_width + 140, y, 100, tech_height)
                    if buy1_rect.collidepoint(event.pos) or buy5_rect.collidepoint(event.pos):
                        amt = 1 if buy1_rect.collidepoint(event.pos) else 5
                        base = TECH_BASE_COSTS.get(key, 1000)
                        # purchase_tech now uses tech currency (`tech_balance`)
                        success = nation_obj.purchase_tech(key, levels=amt, base_cost=base)
                        if success:
                            save_nation(nation_obj, file_path)
                        break

            elif panel_screen == "buildings":
                commerce_panel_button = pygame.Rect(panel_x + 20, 200, PANEL_WIDTH - 40, 50)
                transport_panel_button = pygame.Rect(panel_x + 20, 270, PANEL_WIDTH - 40, 50)
                stability_panel_button = pygame.Rect(panel_x + 20, 340, PANEL_WIDTH - 40, 50)
                healthcare_panel_button = pygame.Rect(panel_x + 20, 410, PANEL_WIDTH - 40, 50)
                education_panel_button = pygame.Rect(panel_x + 20, 480, PANEL_WIDTH - 40, 50)
                safety_panel_button = pygame.Rect(panel_x + 20, 550, PANEL_WIDTH - 40, 50)
                research_panel_button = pygame.Rect(panel_x + 20, 620, PANEL_WIDTH - 40, 50)
                industrial_panel_button = pygame.Rect(panel_x + 20, 690, PANEL_WIDTH - 40, 50)
                tourism_panel_button = pygame.Rect(panel_x + 20, 760, PANEL_WIDTH - 40, 50)

            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                active_input = "infra" if active_input == "land" else "land"
            elif event.key == pygame.K_BACKSPACE:
                if active_input == "land":
                    quantityland_input = quantityland_input[:-1]
                else:
                    quantityinfra_input = quantityinfra_input[:-1]
            elif event.key == pygame.K_RETURN:
                # Convert input strings to floats safely
                try:
                    quantityland = float(quantityland_input) if quantityland_input else 0
                except ValueError:
                    quantityland = 0
                try:
                    quantityinfra = float(quantityinfra_input) if quantityinfra_input else 0
                except ValueError:
                    quantityinfra = 0
            
            if search_active:
                if event.key == pygame.K_BACKSPACE:
                    user_search = user_search[:-1]
                    search_message = ""  # Clear message when deleting too
                elif event.key == pygame.K_RETURN:
                    # Reload saved nations
                    if os.path.exists(file_path):
                        with open(file_path, "r") as f:
                            saved_nations = json.load(f)
                    else:
                        saved_nations = {}
                    if user_search in saved_nations:
                        spectated_nation = load_nation(file_path, user_search)
                        search_message = f"Spectating {user_search}"
                        user_search = ""
                        panel_screen = "nation"
                    else:
                        search_message = "Nation not found."
                        user_search = ""
                else:
                    # Any other key adds a character → clear the message
                    search_message = ""
        elif event.type == pygame.TEXTINPUT:
            char = event.text
            if char.isdigit():
                if active_input == "land":
                    quantityland_input += char
                else:
                    quantityinfra_input += char
            if search_active:
                user_search += event.text

    # Update economic stats ----
    # Commerce Index ----
    
        # Economic growth
    commerce_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    commerce_development = max(commerce_development, 1)
    effective_commerce_buildings = nation_obj.commerce_buildings * nation_obj.get_tech_multiplier("commerce")
    nation_obj.commerce = round(100 * math.sqrt(((effective_commerce_buildings * 3.33) * (nation_obj.transport-100) + ((nation_obj.industrial-100)/2))
                        / commerce_development)+(effective_commerce_buildings * 10000) / commerce_development + 100,2)

    # Transportation Development ----
    integrated_public_transport = 0        # future tech / policy
    bonus_transport_dev_reduction = 0       # modifiers
    development = nation_obj.infrastructure # using infrastructure as dev proxy

    transportation_development = (
        nation_obj.infrastructure *
        (1 + integrated_public_transport / 20)
        + bonus_transport_dev_reduction
        + (development + nation_obj.area) / 10)
    transportation_development = max(transportation_development, 1)
    effective_transport_buildings = nation_obj.transport_buildings * nation_obj.get_tech_multiplier("transport")
    nation_obj.transport = round(100 * math.sqrt(((effective_transport_buildings) * 4.55)
                        / transportation_development)+(effective_transport_buildings * 10000) / transportation_development + 100,2)
    
    
    
    # Education Index ----
    education_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    effective_education_buildings = nation_obj.education_buildings * nation_obj.get_tech_multiplier("education")
    effective_historic_buildings = nation_obj.historic_buildings * nation_obj.get_tech_multiplier("historic")
    nation_obj.education = round(100 * math.sqrt(((effective_education_buildings+effective_historic_buildings) * 5.33 * nation_obj.safety)
                        / education_development)+(effective_education_buildings * 10000 + effective_historic_buildings * 5000) / education_development + 100,2)
    
    # Safety Index ----
    
    safety_development = 2 * (nation_obj.population/100)
    effective_safety_buildings = nation_obj.safety_buildings * nation_obj.get_tech_multiplier("safety")
    nation_obj.safety = round(100 * math.sqrt((effective_safety_buildings * 3.35)
                        / safety_development)+(effective_safety_buildings * 10000) / safety_development + 100,2)
    
    # Healthcare Index
    
    healthcare_development = 2 * (nation_obj.population/100)
    effective_healthcare_buildings = nation_obj.healthcare_buildings * nation_obj.get_tech_multiplier("healthcare")
    nation_obj.healthcare = round(100 * math.sqrt((effective_healthcare_buildings * 4.55)
                        / healthcare_development)+(effective_healthcare_buildings * 10000) / healthcare_development + 100,2)
    # Industrial Index
    industrial_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    effective_industrial_buildings = nation_obj.industrial_buildings * nation_obj.get_tech_multiplier("industrial")
    nation_obj.industrial = round(100 * math.sqrt((effective_industrial_buildings * 2.9)
                        / industrial_development)+(effective_industrial_buildings * 10000) / industrial_development + 100,2)
    
    # Stability Index
    
    stability_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    effective_stability_buildings = nation_obj.stability_buildings * nation_obj.get_tech_multiplier("stability")
    nation_obj.stability = round(
        ((nation_obj.commerce + nation_obj.transport + nation_obj.education + nation_obj.healthcare + nation_obj.safety / 5) / stability_development)
         + ((100 * math.sqrt(((effective_stability_buildings) * 1000)/ stability_development))) + 100,2)
    
    # Income Calculation ----
    commerce_income = (nation_obj.population * (nation_obj.commerce * 0.1))
    transport_income = (nation_obj.population * (nation_obj.transport * 0.06))
    healthcare_income = (nation_obj.population * (nation_obj.healthcare * 0.02))
    safety_income = (nation_obj.population * (nation_obj.safety * 0.03))
    education_income = (nation_obj.population * (nation_obj.education * 0.04))
    tax_income = (100 * (nation_obj.tax * ( nation_obj.population * 0.06)) * (nation_obj.commerce / 100))
    nation_obj.income = (commerce_income + tax_income + transport_income + healthcare_income + safety_income + education_income)
    nation_obj.gdp = (nation_obj.income * 365)
    nation_obj.gdp_per_capita = (nation_obj.gdp/nation_obj.population)
    
    effective_research_buildings = nation_obj.research_buildings * nation_obj.get_tech_multiplier("research")
    nation_obj.tech_income = (effective_research_buildings * (100 *nation_obj.education * 0.8))
    
    # Population Stats ----
    population_growth_per_minute = round((nation_obj.population * 0.0155) * (nation_obj.healthcare / 100), 0)
    nation_obj.population_density = nation_obj.calculate_density()
    if timer_minute >= 60:
        nation_obj.population += population_growth_per_minute 
        nation_obj.balance += (nation_obj.income/1440)
        nation_obj.tech_balance += (nation_obj.tech_income/1440)
        save_nation(nation_obj, file_path) 
        timer_minute = 0
    
    # Draw ----
    
    screen.fill((25, 25, 30))
    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(0, 0, 1920,50))
    title = big_font.render(nation_obj.name, True, (255, 255, 255))
    screen.blit(title, (50, 12.5))
    title = big_font.render(f"Money: {abbreviate_number(nation_obj.balance)}", True, (255, 255, 255))
    screen.blit(title, (230, 12.5))
    title = big_font.render(f"Tech: {abbreviate_number(nation_obj.tech_balance)}", True, (255, 255, 255))
    screen.blit(title, (500, 12.5))
    timer_text = font.render(str(60 - timer_minute), True, (220, 220, 220))
    screen.blit(timer_text, (30, HEIGHT - 40))
    region_text = big_font.render(nation_obj.world_region, True, (220, 220, 220))
    region_rect = region_text.get_rect(midtop=(WIDTH // 2, 12.5))
    screen.blit(region_text, region_rect)


    # Panel Drawing ----
    # Draw toggle button attached to panel edge (always visible)
    toggle_rect = pygame.Rect(int(panel_x) - 40, 0, 40, 50)
    pygame.draw.rect(screen, (70,70,80), toggle_rect)
    arrow = "<" if panel_is_open else ">"
    screen.blit(font.render(arrow, True, (255, 255, 255)), (toggle_rect.x + 10, toggle_rect.y + 10))
    used_building_slots = (
        nation_obj.commerce_buildings + nation_obj.transport_buildings
        + nation_obj.stability_buildings + nation_obj.healthcare_buildings
        + nation_obj.education_buildings + nation_obj.safety_buildings + 
        nation_obj.research_buildings + nation_obj.industrial_buildings + 
        nation_obj.historic_buildings)


    
    if panel_screen == "nation":
        display_nation = spectated_nation if spectated_nation else nation_obj
        # Stats ----
        stats_left = [
            f"Nation: {display_nation.name}",
            f"Income: ${abbreviate_number(display_nation.income)}",
            f"Population: {abbreviate_number(display_nation.population)}",
            f"Population Growth/min: {abbreviate_number(population_growth_per_minute)}",
            f"Infrastructure: {abbreviate_number(display_nation.infrastructure)}",
            f"Area: {abbreviate_number(display_nation.area)} sq km",
            f"GDP: ${abbreviate_number(display_nation.gdp)}",
            f"GDP per Capita: ${abbreviate_number(display_nation.gdp_per_capita)}",
            f"Tech Gain: {abbreviate_number(display_nation.tech_income)}",
            f"Population Density: {abbreviate_number(display_nation.population_density)} people/sq km",
        ]  
        stats_right = [
            f"Building Slots: {used_building_slots}/{display_nation.building_slots}",
            f"Stability: {display_nation.stability}%",
            f"Commerce: {display_nation.commerce}%",
            f"Transport: {display_nation.transport}%",
            f"Industrial: {display_nation.industrial}%",
            f"Healthcare: {display_nation.healthcare}%",
            f"Education: {display_nation.education}%",
            f"Safety: {display_nation.safety}%",
        ]
        y = 100
        for stat in stats_left:
            text = font.render(stat, True, (220, 220, 220))
            screen.blit(text, (50, y))
            y += 40
        y = 100
        for stat in stats_right:
            text = font.render(stat, True, (220, 220, 220))
            screen.blit(text, (WIDTH // 2 + 50, y))
            y += 40
    
    elif panel_screen == "buildings":
        
        building_buttons = [
            (commerce_button, (60, 90, 220), f"Commercial (${abbreviate_number(100_000 * (1.08 ** (nation_obj.commerce_buildings+1)))})"),
            (transport_button, (60, 90, 220), f"Transport (${abbreviate_number(100_000 * (1.08 ** (nation_obj.transport_buildings+1)))})"),
            (stability_button, (60, 90, 220), f"Stability (${abbreviate_number(100_000 * (1.08 ** (nation_obj.stability_buildings+1)))})"),
            (healthcare_button, (60, 90, 220), f"Healthcare (${abbreviate_number(100_000 * (1.08 ** (nation_obj.healthcare_buildings+1)))})"),
            (education_button, (60, 90, 220), f"Education (${abbreviate_number(100_000 * (1.08 ** (nation_obj.education_buildings+1)))})"),
            (safety_button, (60, 90, 220), f"Safety (${abbreviate_number(100_000 * (1.08 ** (nation_obj.safety_buildings+1)))})"),
            (research_button, (60, 90, 220), f"Research (${abbreviate_number(100_000 * (1.08 ** (nation_obj.research_buildings+1)))})"),
            (historic_button, (60, 90, 220), f"Historic (${abbreviate_number(100_000 * (1.08 ** (nation_obj.historic_buildings+1)))})"),
            (industrial_button, (60, 90, 220), f"Industrial (${abbreviate_number(100_000 * (1.08 ** (nation_obj.industrial_buildings+1)))})"),
        ]

        for button_rect, color, label in building_buttons:
            pygame.draw.rect(screen, color, button_rect)
            screen.blit(font.render(label, True, (255, 255, 255)),(button_rect.x + 20, button_rect.y + 12))

            # Calculate CURRENT state
            current = get_nation_projections(nation_obj)

            # Calculate PROJECTIONS (Current + 1 of that specific building)
            p_comm   = get_nation_projections(nation_obj, {"comm": 1})["commerce"]
            p_trans  = get_nation_projections(nation_obj, {"trans": 1})["transport"]
            p_ind    = get_nation_projections(nation_obj, {"ind": 1})["industrial"]
            p_edu    = get_nation_projections(nation_obj, {"edu": 1})["education"]
            p_safe   = get_nation_projections(nation_obj, {"safe": 1})["safety"]
            p_hist   = get_nation_projections(nation_obj, {"hist": 1})["education"] # Historic affects Education
            p_health = get_nation_projections(nation_obj, {"health": 1})["healthcare"]
            p_stab   = get_nation_projections(nation_obj, {"stab": 1})["stability"]

            stats_right = [
                (f"Building Slots: {used_building_slots}/{nation_obj.building_slots}", (1135, 30)),
                
                # First Column
                (f"Owned: {nation_obj.commerce_buildings}", (315, 110)),
                (f"Commerce: {nation_obj.commerce}%", (315, 150)),
                (f"+ {round(p_comm - current['commerce'], 2)}%", (315, 190)),
                
                (f"Owned: {nation_obj.transport_buildings}", (315, 460)),
                (f"Transport: {nation_obj.transport}%", (315, 500)),
                (f"+ {round(p_trans - current['transport'], 2)}%", (315, 540)),
                
                (f"Owned: {nation_obj.industrial_buildings}", (315, 810)),
                (f"Industrial: {nation_obj.industrial}%", (315, 850)),
                (f"+ {round(p_ind - current['industrial'], 2)}%", (315, 890)),

                # Second Column
                (f"Owned: {nation_obj.education_buildings}", (935, 110)),
                (f"Education: {nation_obj.education}%", (935, 150)),
                (f"+ {round(p_edu - current['education'], 2)}%", (935, 190)),
                
                (f"Owned: {nation_obj.safety_buildings}", (935, 460)),
                (f"Safety: {nation_obj.safety}%", (935, 500)),
                (f"+ {round(p_safe - current['safety'], 2)}%", (935, 540)),
                
                (f"Owned: {nation_obj.historic_buildings}", (935, 810)),
                (f"Education: {nation_obj.education}%", (935, 850)),
                (f"+ {round(p_hist - current['education'], 2)}%", (935, 890)),

                # Third Column
                (f"Owned: {nation_obj.research_buildings}", (1555, 110)),
                (f"Tech Income {round(nation_obj.tech_income)}", (1555, 150)),
                (f"Tech Gain + {round(100 * nation_obj.education * 0.8, 2)}", (1555, 190)),
                
                (f"Owned: {nation_obj.healthcare_buildings}", (1555, 460)),
                (f"Healthcare {nation_obj.healthcare}%", (1555, 500)),
                (f"+ {round(p_health - current['healthcare'], 2)}%", (1555, 540)),
                
                (f"Owned: {nation_obj.stability_buildings}", (1555, 810)),
                (f"Stability: {nation_obj.stability}%", (1555, 850)),
                (f"+ {round(p_stab - current['stability'], 2)}%", (1555, 890)),
            ]
        for stat_text, pos in stats_right:
            text = font.render(stat_text, True, (220, 220, 220))
            screen.blit(text, pos)

        images = [
            (commercial_image, (65, 90)),
            (transport_image, (65, 440)),
            (industrial_image, (65, 790)),
            
            (education_image, (685, 90)),
            (safety_image, (685, 440)),
            (historic_image, (685, 790)), 
            
            (research_image, (1305, 90)),
            (healthcare_image, (1305, 440)),
            (stability_image, (1305, 790)),
            
        ]
        for img, pos in images:
            screen.blit(img, pos)
        
        
        

    elif panel_screen == "investments":
        pygame.draw.rect(screen, (200, 80, 80), exit_button)
        pygame.draw.rect(screen, (60, 140, 220), land_button)
        pygame.draw.rect(screen, (60, 140, 220), infrastructure_button)
        screen.blit(font.render("Save & Exit", True, (255, 255, 255)),(exit_button.x + 90, exit_button.y + 12))
        # compute discounts and base costs for display
        land_display_discount = nation_obj.get_cost_multiplier('land_cost')
        base_land_cost_display = ((float(quantityland_input) if quantityland_input else 0)  * (nation_obj.area / 100) ** 2) / 2
        screen.blit(font.render(f"Purchase {abbreviate_number(float(quantityland_input) if quantityland_input else 0)} Land for ${abbreviate_number(base_land_cost_display * land_display_discount)}", True, (255, 255, 255)),(land_button.x + 20, land_button.y + 15))
        infrastructure_cost_reduction = max((nation_obj.infrastructure / (nation_obj.area*0.9)) ** 2, 0)
        infra_display_discount = nation_obj.get_cost_multiplier('infrastructure_cost')
        infra_cost_display = infrastructure_cost_reduction * (float(quantityinfra_input) if quantityinfra_input else 0) * (nation_obj.infrastructure / 100) ** 2 * infra_display_discount
        screen.blit(font.render(f"Purchase {abbreviate_number(float(quantityinfra_input) if quantityinfra_input else 0)} Infrastructure for ${abbreviate_number(infra_cost_display)}", True, (255, 255, 255)),(infrastructure_button.x + 20, infrastructure_button.y + 15))

        stats_right = [
            (f"Building Slots: {used_building_slots}/{nation_obj.building_slots}", (1135, 30)),
            (f"Owned: {nation_obj.area}", (110,460)),
            (f"Cost Reduction: {abbreviate_number((1 - nation_obj.get_cost_multiplier('land_cost'))*100)}%", (110, 500)),
            (f"Owned: {nation_obj.infrastructure}", (720, 460)),
            (f"Cost Reduction: {abbreviate_number((1 - nation_obj.get_cost_multiplier('infrastructure_cost'))*100)}%", (720, 500)),
        ]
        for stat_text, pos in stats_right:
            text = font.render(stat_text, True, (220, 220, 220))
            screen.blit(text, pos)
        
        images = [
            (area_image, (100, 110)),
            (infrastructure_image, (720, 110)),
        ]
        for img, pos in images:
            screen.blit(img, pos)
        
        pygame.draw.rect(screen, (255, 255, 255) if active_input == "land" else (180, 180, 180), (100, 645, 480, 30), 2)
        pygame.draw.rect(screen, (255, 255, 255) if active_input == "infra" else (180, 180, 180), (720, 645, 480, 30), 2)
        draw_text(screen, "Press TAB to switch", (100, 680), color=(220, 220, 220))
        draw_text(screen, quantityland_input, (105, 650))
        draw_text(screen, quantityinfra_input, (725, 650))
    
    elif panel_screen == "tech":
        # Render tech upgrade panel
        tech_start_x = 100
        tech_start_y = 150
        tech_width = 500
        tech_height = 48
        gap = 12
        tech_items = [
            ("commerce", "Commerce"),
            ("transport", "Transport"),
            ("industrial", "Industry"),
            ("education", "Education"),
            ("healthcare", "Healthcare"),
            ("safety", "Safety"),
            ("research", "Research"),
            ("infrastructure_cost", "Infrastructure Cost Reduction"),
            ("tech_gain", "Tech Gain"),
            ("tech_cost", "Tech Cost Discount"),
            ("building_slots", "Building Slots"),
            ("land_cost", "Land Cost Reduction"),
        ]

        for i, (key, label) in enumerate(tech_items):
            y = tech_start_y + i * (tech_height + gap)
            rect = pygame.Rect(tech_start_x, y, tech_width, tech_height)
            pygame.draw.rect(screen, (60, 60, 70), rect)
            level = nation_obj.get_tech_level(key)
            next_cost = nation_obj.next_level_cost(key, base_cost=TECH_BASE_COSTS.get(key, 1000))
            buy1_rect = pygame.Rect(tech_start_x + tech_width + 20, y, 100, tech_height)
            buy5_rect = pygame.Rect(tech_start_x + tech_width + 140, y, 100, tech_height)
            # Draw buttons (wider)
            pygame.draw.rect(screen, (80, 160, 80) if next_cost > 0 else (80,80,80), buy1_rect)
            pygame.draw.rect(screen, (80, 120, 200) if next_cost > 0 else (80,80,80), buy5_rect)
            # Text
            screen.blit(font.render(f"{label}", True, (255,255,255)), (rect.x + 10, rect.y + 8))
            screen.blit(font.render(f"Level: {level}", True, (220,220,220)), (rect.x + 200, rect.y + 8))
            cost_text = f"1: ${abbreviate_number(next_cost)} / 5: ${abbreviate_number(nation_obj.total_cost_for_levels(key, 5, base_cost=TECH_BASE_COSTS.get(key,1000)))}"
            screen.blit(font.render(cost_text, True, (220,220,220)), (rect.x + 260, rect.y + 8))
            screen.blit(font.render("Buy 1 (T)", True, (0,0,0)), (buy1_rect.x + 8, buy1_rect.y + 12))
            screen.blit(font.render("Buy 5 (T)", True, (255,255,255)), (buy5_rect.x + 8, buy5_rect.y + 12))
        
    elif panel_screen == "warfare":
        print("Warfare screen - coming soon!")
    elif panel_screen == "leaderboard":
        leaderboard_title = big_font.render("Global Leaderboard", True, (255,255,255))
        leaderboard_rect = leaderboard_title.get_rect(center=(WIDTH // 2, 120))
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                saved_nations = json.load(f)
        else:
            saved_nations = {}
        all_nations = []
        for name, data in saved_nations.items():
            all_nations.append({
                "name": name,
                "gdp": data["gdp"],
                "population": data["population"],
                "gpc": data["gdp_per_capita"]
            })
        gdp_board = sorted(all_nations, key=lambda x: x["gdp"], reverse=True)
        pop_board = sorted(all_nations, key=lambda x: x["population"], reverse=True)
        gpc_board = sorted(all_nations, key=lambda x: x["gpc"], reverse=True)
        column_width = WIDTH // 3
        pygame.draw.rect(screen, (142, 142, 142), pygame.Rect((column_width * 0 + column_width // 2 - 225, 120, 450, 900)))
        pygame.draw.rect(screen, (146, 114, 82), pygame.Rect((column_width * 1 + column_width // 2 - 225, 120, 450, 900)))
        pygame.draw.rect(screen, (205, 165, 0), pygame.Rect((column_width * 2 + column_width // 2 - 225, 120, 450, 900)))
        gdp_x = column_width * 0 + column_width // 2
        pop_x = column_width * 1 + column_width // 2
        gpc_x = column_width * 2 + column_width // 2
        titles = [
            ("GDP Ranking", gdp_x),
            ("Population Ranking", pop_x),
            ("GDP Per Capita Ranking", gpc_x)
        ]
        for title_text, x in titles:
            title_surface = big_font.render(title_text, True, (255,255,255))
            rect = title_surface.get_rect(center=(x, 150))
            screen.blit(title_surface, rect)
        start_y = 215
        line_spacing = 55
        max_entries = min(15, len(all_nations))
        
        for i in range(max_entries):
            # GDP
            gdp_line = font.render(f"{i+1}. {gdp_board[i]['name']} - ${abbreviate_number(gdp_board[i]['gdp'])}",True,(255,255,255))
            screen.blit(gdp_line, gdp_line.get_rect(center=(gdp_x, start_y + i*line_spacing)))
            # Population
            pop_line = font.render(f"{i+1}. {pop_board[i]['name']} - {abbreviate_number(pop_board[i]['population'])}",True,(255,255,255))
            screen.blit(pop_line, pop_line.get_rect(center=(pop_x, start_y + i*line_spacing)))
            # GDP Per Capita
            gpc_line = font.render(f"{i+1}. {gpc_board[i]['name']} - ${abbreviate_number(gpc_board[i]['gpc'])}",True,(255,255,255))
            screen.blit(gpc_line, gpc_line.get_rect(center=(gpc_x, start_y + i*line_spacing)))



    if panel_x < WIDTH:  # Only draw panel background and contents when open/visible
        # Panel background
        pygame.draw.rect(screen, (40, 40, 50), pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT))
        pygame.draw.rect(screen, (70,70,80), (panel_x, 910, PANEL_WIDTH, 500))
        # Panel header
        header = big_font.render("Menu", True, (255, 255, 255))
        pygame.draw.rect(screen, (70,70,80), (panel_x, 0, PANEL_WIDTH, 50))
        screen.blit(header, (panel_x + 60, 12.5))

        # Panel screens
        exit_button = pygame.Rect(panel_x + 20, 1010, PANEL_WIDTH - 40, 50)
        nation_screen_button = pygame.Rect(panel_x + 20, 70, PANEL_WIDTH - 40, 50)
        buildings_screen_button = pygame.Rect(panel_x + 20, 140, PANEL_WIDTH - 40, 50)
        investments_screen_button = pygame.Rect(panel_x + 20, 210, PANEL_WIDTH - 40, 50)
        tech_screen_button = pygame.Rect(panel_x + 20, 280, PANEL_WIDTH - 40, 50)
        warfare_screen_button = pygame.Rect(panel_x + 20, 350, PANEL_WIDTH - 40, 50)
        leaderboard_screen_button = pygame.Rect(panel_x + 20, 840, PANEL_WIDTH - 40, 50)
        pygame.draw.rect(screen, (200, 80, 80), exit_button)
        pygame.draw.rect(screen, (80, 120, 200), nation_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), buildings_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), investments_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), tech_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), warfare_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), leaderboard_screen_button)
        
        screen.blit(font.render("Save & Exit", True, (255, 255, 255)),(exit_button.x + 90, exit_button.y + 14))
        screen.blit(font.render("Nation", True, (255, 255, 255)), (nation_screen_button.x + 10, nation_screen_button.y + 14))
        screen.blit(font.render("Buildings", True, (255, 255, 255)), (buildings_screen_button.x + 10, buildings_screen_button.y + 14))
        screen.blit(font.render("Investments", True, (255, 255, 255)), (investments_screen_button.x + 10, investments_screen_button.y + 14))
        screen.blit(font.render("Tech", True, (255, 255, 255)), (tech_screen_button.x + 10, tech_screen_button.y + 14))
        screen.blit(font.render("Warfare", True, (255, 255, 255)), (warfare_screen_button.x + 10, warfare_screen_button.y + 14))
        screen.blit(font.render("Leaderboard", True, (255, 255, 255)), (leaderboard_screen_button.x + 10, leaderboard_screen_button.y + 14))
        
        # NATION SEARCH ------------------
        
        search_box = pygame.Rect(panel_x + 20, 950, PANEL_WIDTH - 40, 40)
        pygame.draw.rect(screen, (60, 60, 70), search_box)
        pygame.draw.rect(screen, (255, 255, 255), search_box, 2)
        screen.blit(font.render("Search Nation:", True, (220, 220, 220)),(search_box.x, search_box.y - 25))
        screen.blit(font.render(user_search, True, (255, 255, 255)),(search_box.x + 10, search_box.y + 8))
        screen.blit(font.render(search_message, True, (185, 255, 185)),(search_box.x + 10, search_box.y + 8))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
