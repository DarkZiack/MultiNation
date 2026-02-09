import pygame
import os
import json
import math

from data.nation import nation
from data.save_load import load_nation, save_nation
from engine.num_format import abbreviate_number
from engine.world import regions

#   CONFIG --------------------
WIDTH, HEIGHT = 1920, 1080
FPS = 60

population_growth_per_minute = 5000
file_path = "data/nations_save.json"

# PANEL CONFIG -------------------- 
PANEL_WIDTH = 350
PANEL_CLOSED_X = WIDTH
PANEL_OPEN_X = WIDTH - PANEL_WIDTH
PANEL_ANIMATION_SPEED = 20
PANEL_TABS = ["Buildings", "Investments"]

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
                    nation_obj = nation(input_text.strip(), 
                                        100000,  # Population
                                        1000, # Infrastructure
                                        1000,  # Land
                                        100,  # Income
                                        10000000, # Balance
                                        100,  # Commerce
                                        0, # Commerce Buidlings
                                        100, # Transport
                                        0, # Transport Buildings
                                        100,  # Stability
                                        0, # Stability Buildings
                                        100,  # Healthcare
                                        0, # Healthcare Buildings
                                        100,  # Education
                                        0, # Education Buildings
                                        100,  # Safety
                                        0, # Safety Buildings
                                        100,  # GDP
                                        100,  # GDPPC
                                        10,  # Tax
                                        selected_region)  # World Region
                    """
                (self, name, population, infrastructure, area, income, balance, commerce, commerce_buildings, 
                transport, transport_buildings, stability, stability_buildings, healthcare, healthcare_buildings
                , education, education_buildings, safety, safety_buildings ,gdp, gdp_per_capita, tax, world_region=None):
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

commerce_button = pygame.Rect(350, 250, 300, 50)
transport_button = pygame.Rect(350, 600, 300, 50)
stability_button = pygame.Rect(970, 950, 300, 50)
healthcare_button = pygame.Rect(350, 950, 300, 50)
education_button = pygame.Rect(970, 250, 300, 50) 
safety_button = pygame.Rect(970, 600, 300, 50) 

commercial_image = pygame.image.load("data/assets/commercial.jpg")
transport_image = pygame.image.load("data/assets/transport.jpg")
education_image = pygame.image.load("data/assets/education.jpg")
healthcare_image = pygame.image.load("data/assets/healthcare.jpg")
safety_image = pygame.image.load("data/assets/safety.jpg")
stability_image = pygame.image.load("data/assets/stability.jpg")

IMAGE_SIZE_BUILDINGS = (225, 225)

commercial_image = pygame.transform.smoothscale(pygame.image.load("data/assets/commercial.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
transport_image = pygame.transform.smoothscale(pygame.image.load("data/assets/transport.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
education_image = pygame.transform.smoothscale(pygame.image.load("data/assets/education.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
healthcare_image = pygame.transform.smoothscale(pygame.image.load("data/assets/healthcare.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
safety_image = pygame.transform.smoothscale(pygame.image.load("data/assets/safety.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)
stability_image = pygame.transform.smoothscale(pygame.image.load("data/assets/stability.jpg").convert_alpha(),IMAGE_SIZE_BUILDINGS)


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
    save_nation(nation_obj, file_path)

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
            used_building_slots = (
                nation_obj.commerce_buildings + nation_obj.transport_buildings
                + nation_obj.stability_buildings + nation_obj.healthcare_buildings
                + nation_obj.education_buildings + nation_obj.safety_buildings
            )
            if panel_screen == "buildings":
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
                
            # Dev
            if panel_screen == "investments":
                if land_button.collidepoint(event.pos) and nation_obj.balance >= ((float(quantityland_input) if quantityland_input else 0) * (nation_obj.area / 100) ** 2) / 2:
                    nation_obj.balance -= ((float(quantityland_input) if quantityland_input else 0) * (nation_obj.area / 100) ** 2) / 2
                    nation_obj.area += (float(quantityland_input) if quantityland_input else 0)
                    quantityland_input = ""
                if infrastructure_button.collidepoint(event.pos) and nation_obj.balance >= (infrastructure_cost_reduction* (float(quantityinfra_input) if quantityinfra_input else 0)* (nation_obj.infrastructure / 100) ** 2):
                    nation_obj.balance -= (infrastructure_cost_reduction*(float(quantityinfra_input) if quantityinfra_input else 0)* (nation_obj.infrastructure / 100) ** 2)
                    nation_obj.infrastructure += (float(quantityinfra_input) if quantityinfra_input else 0)
                    quantityinfra_input = ""
            infrastructure_cost_reduction = max((nation_obj.infrastructure / (nation_obj.area*0.9)) ** 2, 0)

            # Panel events: dynamic toggle attached to panel edge
            toggle_rect = pygame.Rect(int(panel_x) - 40, 0, 40, 50)
            if toggle_rect.collidepoint(event.pos):
                panel_is_open = not panel_is_open

            if panel_x < WIDTH:  # Panel is visible (or sliding)
            # Panel navigation screens
                nation_screen_button = pygame.Rect(panel_x + 20, 70, PANEL_WIDTH -40, 50)
                buildings_screen_button = pygame.Rect(panel_x + 20, 140, PANEL_WIDTH - 40, 50)
                investments_screen_button = pygame.Rect(panel_x + 20, 210, PANEL_WIDTH - 40, 50)
                if nation_screen_button.collidepoint(event.pos):
                    panel_screen = "nation"
                elif buildings_screen_button.collidepoint(event.pos):
                    panel_screen = "buildings"
                elif investments_screen_button.collidepoint(event.pos):
                    panel_screen = "investments"

            elif panel_screen == "buildings":
                commerce_panel_button = pygame.Rect(panel_x + 20, 200, PANEL_WIDTH - 40, 50)
                transport_panel_button = pygame.Rect(panel_x + 20, 270, PANEL_WIDTH - 40, 50)
                stability_panel_button = pygame.Rect(panel_x + 20, 340, PANEL_WIDTH - 40, 50)
                healthcare_panel_button = pygame.Rect(panel_x + 20, 410, PANEL_WIDTH - 40, 50)
                education_panel_button = pygame.Rect(panel_x + 20, 480, PANEL_WIDTH - 40, 50)
                safety_panel_button = pygame.Rect(panel_x + 20, 550, PANEL_WIDTH - 40, 50)
                back_button = pygame.Rect(panel_x + 20, 620, PANEL_WIDTH - 40, 40)
                used_building_slots = (
                    nation_obj.commerce_buildings + nation_obj.transport_buildings
                    + nation_obj.stability_buildings + nation_obj.healthcare_buildings
                    + nation_obj.education_buildings + nation_obj.safety_buildings
                )
        
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

        # TEXTINPUT for actual typing
        elif event.type == pygame.TEXTINPUT:
            char = event.text
            if char.isdigit():
                if active_input == "land":
                    quantityland_input += char
                else:
                    quantityinfra_input += char
    # Update economic stats ----
    # Commerce Index ----
    
        # Economic growth
    commerce_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    commerce_development = max(commerce_development, 1)
    
    nation_obj.commerce = round(100 * math.sqrt((nation_obj.commerce_buildings * 3.33 * nation_obj.transport)
                        / commerce_development)+(nation_obj.commerce_buildings * 10000) / commerce_development + 100,2)

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
    roads = nation_obj.transport_buildings
    bonus_roads = 0
    transportation_eff = 1                 # efficiency modifier
    bonus_road_output = 0
    national_highway_system = 0
    nation_obj.transport = round(
        (100 * math.sqrt(((roads + bonus_roads) * transportation_eff * 200)/ transportation_development)
         + (((roads + bonus_roads) * transportation_eff * 10000)/ transportation_development))* 
        (1+ bonus_road_output / 100+ national_highway_system / 4) + 100,2)
    
    # Education Index ----
    education_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    nation_obj.education = round(100 * math.sqrt((nation_obj.education_buildings * 3.33 * nation_obj.safety)
                        / education_development)+(nation_obj.education_buildings * 10000) / education_development + 100,2)
    
    # Safety Index ----
    
    safety_development = 2 * (nation_obj.population/100)
    
    nation_obj.safety = round(100 * math.sqrt((nation_obj.safety_buildings * 3.33)
                        / safety_development)+(nation_obj.safety_buildings * 10000) / safety_development + 100,2)
    
    # Healthcare Index
    
    healthcare_development = 2 * (nation_obj.population/100)
    
    nation_obj.healthcare = round(100 * math.sqrt((nation_obj.healthcare_buildings * 3.33)
                        / healthcare_development)+(nation_obj.healthcare_buildings * 10000) / healthcare_development + 100,2)
    
    # Stability Index
    
    stability_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    
    nation_obj.stability = round(
        ((nation_obj.commerce + nation_obj.transport + nation_obj.education + nation_obj.healthcare + nation_obj.safety / 5) / stability_development)
         + ((100 * math.sqrt(((nation_obj.stability_buildings) * 1000)/ stability_development))) + 100,2)
    
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
    
    # Population Stats ----
    population_growth_per_minute = round((nation_obj.population * 0.015) * (nation_obj.healthcare / 100), 1)
    nation_obj.population_density = nation_obj.calculate_density()
    if timer_minute >= 60:
        nation_obj.population += population_growth_per_minute 
        nation_obj.balance += (nation_obj.income/1440)
        timer_minute = 0
    
    # Draw ----
    
    screen.fill((25, 25, 30))

    title = big_font.render(nation_obj.name, True, (255, 255, 255))
    screen.blit(title, (50, 30))
    title = big_font.render(f"Money: {abbreviate_number(nation_obj.balance)}", True, (255, 255, 255))
    screen.blit(title, (230, 30))
    # Timer moved to bottom-left
    timer_text = font.render(str(60 - timer_minute), True, (220, 220, 220))
    screen.blit(timer_text, (30, HEIGHT - 40))
    region_text = font.render(nation_obj.world_region, True, (220, 220, 220))
    region_rect = region_text.get_rect(midtop=(WIDTH // 2, 30))
    screen.blit(region_text, region_rect)


    # Panel Drawing ----
    # Draw toggle button attached to panel edge (always visible)
    toggle_rect = pygame.Rect(int(panel_x) - 40, 0, 40, 50)
    pygame.draw.rect(screen, (100, 100, 120), toggle_rect)
    arrow = "<" if panel_is_open else ">"
    screen.blit(font.render(arrow, True, (255, 255, 255)), (toggle_rect.x + 10, toggle_rect.y + 10))

    if panel_x < WIDTH:  # Only draw panel background and contents when open/visible
        # Panel background
        pygame.draw.rect(screen, (40, 40, 50), pygame.Rect(panel_x, 0, PANEL_WIDTH, HEIGHT))

        # Panel header
        header = big_font.render("Menu", True, (255, 255, 255))
        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(panel_x, 0, PANEL_WIDTH, 50))
        screen.blit(header, (panel_x + 60, 10))

        # Panel screens
        
        nation_screen_button = pygame.Rect(panel_x + 20, 70, PANEL_WIDTH - 40, 50)
        buildings_screen_button = pygame.Rect(panel_x + 20, 140, PANEL_WIDTH - 40, 50)
        investments_screen_button = pygame.Rect(panel_x + 20, 210, PANEL_WIDTH - 40, 50)
        pygame.draw.rect(screen, (80, 120, 200), nation_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), buildings_screen_button)
        pygame.draw.rect(screen, (80, 120, 200), investments_screen_button)
        screen.blit(font.render("Nation", True, (255, 255, 255)), (nation_screen_button.x + 10, nation_screen_button.y + 12))
        screen.blit(font.render("Buildings", True, (255, 255, 255)), (buildings_screen_button.x + 10, buildings_screen_button.y + 12))
        screen.blit(font.render("Investments", True, (255, 255, 255)), (investments_screen_button.x + 10, investments_screen_button.y + 12))
            
    if panel_screen == "nation":
        # Buttons ----
        pygame.draw.rect(screen, (200, 80, 80), exit_button)
        screen.blit(font.render("Save & Exit", True, (255, 255, 255)),(exit_button.x + 90, exit_button.y + 12))
        
        # Stats ----
        used_building_slots = (
        nation_obj.commerce_buildings + nation_obj.transport_buildings
        + nation_obj.stability_buildings + nation_obj.healthcare_buildings
        + nation_obj.education_buildings + nation_obj.safety_buildings)
        stats_left = [
            f"Nation: {nation_obj.name}",
            f"Income: ${abbreviate_number(nation_obj.income)}",
            f"Population: {abbreviate_number(nation_obj.population)}",
            f"Population Growth/min: {abbreviate_number(population_growth_per_minute)}",
            f"Infrastructure: {nation_obj.infrastructure}",
            f"Area: {abbreviate_number(nation_obj.area)} sq km",
            f"GDP: ${abbreviate_number(nation_obj.gdp)}",
            f"GDP per Capita: ${abbreviate_number(nation_obj.gdp_per_capita)}",
            f"Population Density: {abbreviate_number(nation_obj.population_density)} people/sq km",
        ]  
        stats_right = [
            f"Building Slots: {used_building_slots}/{nation_obj.building_slots}",
            f"Stability: {nation_obj.stability}%",
            f"Commerce: {nation_obj.commerce}%",
            f"Transport: {nation_obj.transport}%",
            f"Healthcare: {nation_obj.healthcare}%",
            f"Education: {nation_obj.education}%",
            f"Safety: {nation_obj.safety}%",
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
        ]

        pygame.draw.rect(screen, (200, 80, 80), exit_button)
        screen.blit(font.render(f"Save & Exit", True, (255, 255, 255)),(exit_button.x + 90, exit_button.y + 12))

        for button_rect, color, label in building_buttons:
            pygame.draw.rect(screen, color, button_rect)
            screen.blit(font.render(label, True, (255, 255, 255)),(button_rect.x + 20, button_rect.y + 12))

        stats_right = [
            (f"Building Slots: {used_building_slots}/{nation_obj.building_slots}", (500, 30)),
            # First line
            (f"Owned: {nation_obj.commerce_buildings}", (350, 110)),
            (f"Commerce: {nation_obj.commerce}%", (350, 150)),
            (f"+ {round(100 * math.sqrt(((nation_obj.commerce_buildings+1) * 3.33 * nation_obj.transport)/ commerce_development)+((nation_obj.commerce_buildings+1) * 10000) / commerce_development + 100 - nation_obj.commerce,2)}%", (350, 190)),
            (f"Owned: {nation_obj.transport_buildings}", (350, 460)),
            (f"Transport: {nation_obj.transport}%", (350, 500)),
            (f"+ {round((100 * math.sqrt(((roads+1 + bonus_roads) * transportation_eff * 200)/ transportation_development)+ (((roads+1 + bonus_roads) * transportation_eff * 10000)/ transportation_development))* (1+ bonus_road_output / 100+ national_highway_system / 4) + 100 - nation_obj.transport,2)}%", (350, 540)),
            (f"Owned: {nation_obj.healthcare_buildings}", (350, 810)),
            (f"Healthcare {nation_obj.healthcare}%", (350, 850)),
            (f"+ {round(100 * math.sqrt(((nation_obj.healthcare_buildings+1) * 3.33) / healthcare_development)+((nation_obj.healthcare_buildings+1) * 10000) / healthcare_development + 100 - nation_obj.healthcare,2)}%", (350, 890)),
            # Second line
            (f"Owned: {nation_obj.education_buildings}", (970, 110)),
            (f"Education: {nation_obj.education}%", (970, 150)),
            (f"+ {round(100 * math.sqrt(((nation_obj.education_buildings+1) * 3.33 * nation_obj.safety)/ education_development)+((nation_obj.education_buildings+1) * 10000) / education_development + 100 - nation_obj.education,2)}%", (970, 190)),
            (f"Owned: {nation_obj.safety_buildings}", (970, 460)),
            (f"Safety: {nation_obj.safety}%", (970, 500)),
            (f"+ {round(100 * math.sqrt(((nation_obj.safety_buildings+1) * 3.33) / safety_development)+((nation_obj.safety_buildings+1) * 10000) / safety_development + 100 - nation_obj.safety,2)}%", (970, 540)),
            (f"Owned: {nation_obj.stability_buildings}", (970, 810)),
            (f"Stability: {nation_obj.stability}%", (970, 850)),
            (f"+ {round(((nation_obj.commerce + nation_obj.transport + nation_obj.education + nation_obj.healthcare + nation_obj.safety / 5) / stability_development)+ ((100 * math.sqrt(((nation_obj.stability_buildings+1) * 1000)/ stability_development))) + 100 - nation_obj.stability,2)}%", (970, 890)),
        ]
        for stat_text, pos in stats_right:
            text = font.render(stat_text, True, (220, 220, 220))
            screen.blit(text, pos)

        images = [
            (commercial_image, (100, 100)),
            (transport_image, (100, 450)),
            (safety_image, (720, 450)),
            (education_image, (720, 100)),
            (healthcare_image, (100, 800)),
            (stability_image, (720, 800)),
        ]
        for img, pos in images:
            screen.blit(img, pos)
        
        
        

    elif panel_screen == "investments":
        pygame.draw.rect(screen, (200, 80, 80), exit_button)
        pygame.draw.rect(screen, (60, 140, 220), land_button)
        pygame.draw.rect(screen, (60, 140, 220), infrastructure_button)
        screen.blit(font.render("Save & Exit", True, (255, 255, 255)),(exit_button.x + 90, exit_button.y + 12))
        screen.blit(font.render(f"Purchase {abbreviate_number(float(quantityland_input) if quantityland_input else 0)} Land for ${abbreviate_number(((float(quantityland_input) if quantityland_input else 0)  * (nation_obj.area / 100) ** 2) / 2)}", True, (255, 255, 255)),(land_button.x + 20, land_button.y + 15))
        screen.blit(font.render(f"Purchase {abbreviate_number(float(quantityinfra_input) if quantityinfra_input else 0)} Infrastructure for ${abbreviate_number(infrastructure_cost_reduction* (float(quantityinfra_input) if quantityinfra_input else 0) * (nation_obj.infrastructure / 100) ** 2)}", True, (255, 255, 255)),(infrastructure_button.x + 20, infrastructure_button.y + 15))

        stats_right = [
            (f"Building Slots: {used_building_slots}/{nation_obj.building_slots}", (500, 30)),
            (f"Owned: {nation_obj.area}", (110,460)),
            (f"Owned: {nation_obj.infrastructure}", (720, 460)),
            (f"Cost Reduction: {abbreviate_number(max((1 - infrastructure_cost_reduction) * 100, 0))}%", (720, 500)),
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
        
        
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
