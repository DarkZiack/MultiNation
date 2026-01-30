import pygame
import os
import json
import math

from data.nation import nation
from data.save_load import load_nation, save_nation
from engine.num_format import abbreviate_number
from engine.world import regions

# -------------------- CONFIG --------------------
WIDTH, HEIGHT = 1920, 1080
FPS = 60

population_growth_per_minute = 5000
file_path = "data/nations_save.json"

# -------------------- PANEL CONFIG --------------------
PANEL_WIDTH = 350
PANEL_CLOSED_X = WIDTH
PANEL_OPEN_X = WIDTH - PANEL_WIDTH
PANEL_ANIMATION_SPEED = 20
PANEL_TABS = ["Buildings", "Investments"]

# -------------------- INIT --------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nation Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big_font = pygame.font.SysFont(None, 40)

# -------------------- LOAD SAVE DATA --------------------
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        saved_nations = json.load(f)
else:
    saved_nations = {}

# -------------------- NATION SETUP (PYGAME MENU) --------------------
input_text = ""
phase = "name"  # name -> region -> done
message = ""
nation_obj = None

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
                                        5, # Commerce Buidlings
                                        100, # Transport
                                        5, # Transport Buildings
                                        100,  # Stability
                                        5, # Stability Buildings
                                        100,  # Healthcare
                                        5, # Healthcare Buildings
                                        100,  # Education
                                        5, # Education Buildings
                                        100,  # Safety
                                        5, # Safety Buildings
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

    # ---- Draw input interface ----
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

# -------------------- UI ELEMENTS --------------------
upgrade_button = pygame.Rect(50, 480, 300, 50)
exit_button = pygame.Rect(WIDTH - 350, HEIGHT - 100, 300, 50)
commerce_button = pygame.Rect(50, 540, 300, 50)
transport_button = pygame.Rect(400, 540, 300, 50)
land_button = pygame.Rect(50, 600, 300, 50)
infrastructure_button = pygame.Rect(400, 600, 300, 50)
stability_button = pygame.Rect(50, 660, 300, 50)
healthcare_button = pygame.Rect(400, 660, 300, 50)
education_button = pygame.Rect(50, 720, 300, 50)
safety_button = pygame.Rect(400, 720, 300, 50)

# -------------------- PANEL STATE --------------------
panel_is_open = False
panel_x = PANEL_CLOSED_X
# panel_screen: 'main' shows navigation, 'buildings' and 'investments' show respective buy screens
panel_screen = "main"

# -------------------- MAIN LOOP --------------------
running = True
timer = 0
timer_minute = 0

# -------------------- Economic Stats --------------------

commerce_income = 0
tax_income = 0
trasport_income = 10000000
education_income = 10000000


while running:
    timer += 1
    if timer == 62:
        timer_minute += 1
        timer = 0
    # ---- Economic growth ----
    commerce_development = 2 * (nation_obj.infrastructure + (nation_obj.area / 10))
    commerce_development = max(commerce_development, 1)

    # ---- Commerce Index ----
    nation_obj.commerce = round(100 * math.sqrt((nation_obj.commerce_buildings * 3.33 * nation_obj.transport)
                        / commerce_development)+(nation_obj.commerce_buildings * 10000) / commerce_development,2)
    
    # ---- Transportation Development ----
    integrated_public_transport = 0        # future tech / policy
    bonus_transport_dev_reduction = 0       # modifiers
    development = nation_obj.infrastructure # using infrastructure as dev proxy

    transportation_development = (
        nation_obj.infrastructure *
        (1 + integrated_public_transport / 20)
        + bonus_transport_dev_reduction
        + (development + nation_obj.area) / 10)
    transportation_development = max(transportation_development, 1)

    # ---- Transportation Index (Roads) ----
    roads = nation_obj.transport_buildings
    bonus_roads = 0
    transportation_eff = 1                 # efficiency modifier
    bonus_road_output = 0
    national_highway_system = 0
    nation_obj.transport = round(
        (100 * math.sqrt(((roads + bonus_roads) * transportation_eff * 200)/ transportation_development)
         + (((roads + bonus_roads) * transportation_eff * 10000)/ transportation_development))* (1+ bonus_road_output / 100+ national_highway_system / 4),2)
    # ---- Income Calculation ----
    commerce_income = (nation_obj.population * (nation_obj.commerce * 0.1))
    tax_income = (100 * (nation_obj.tax * ( nation_obj.population * 0.06)) * (nation_obj.commerce / 100))
    nation_obj.income = (commerce_income + tax_income + trasport_income + education_income)
    nation_obj.gdp = (nation_obj.income * 365)
    nation_obj.gdp_per_capita = (nation_obj.gdp/nation_obj.population)
    
    # ---- Population Stats ----
    population_growth_per_minute = round((nation_obj.population * 0.001) * min((nation_obj.healthcare / 100), 1))
    nation_obj.population_density = nation_obj.calculate_density()
    if timer_minute >= 60:
        nation_obj.population += population_growth_per_minute 
        nation_obj.balance += (nation_obj.income/1440)
        timer_minute = 0

    save_nation(nation_obj, file_path)

    # ---- Panel Animation ----
    target_x = PANEL_OPEN_X if panel_is_open else PANEL_CLOSED_X
    if panel_x != target_x:
        if panel_x < target_x:
            panel_x = min(panel_x + PANEL_ANIMATION_SPEED, target_x)
        else:
            panel_x = max(panel_x - PANEL_ANIMATION_SPEED, target_x)

    # ---- Events ----
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_nation(nation_obj, file_path)
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if nation_obj.balance >= 100000:
                if upgrade_button.collidepoint(event.pos):
                    nation_obj.population += 10000
                    nation_obj.balance -= 100000
            if exit_button.collidepoint(event.pos):
                save_nation(nation_obj, file_path)
                running = False
            
            # Buildings
            used_building_slots = (
                nation_obj.commerce_buildings + nation_obj.transport_buildings
                + nation_obj.stability_buildings + nation_obj.healthcare_buildings
                + nation_obj.education_buildings + nation_obj.safety_buildings
            )
            if used_building_slots < nation_obj.building_slots:
                if nation_obj.balance >= 1000000:
                    if commerce_button.collidepoint(event.pos):
                        nation_obj.commerce_buildings += 1
                        nation_obj.balance -= 1000000
                    elif transport_button.collidepoint(event.pos):
                        nation_obj.transport_buildings += 1
                        nation_obj.balance -= 1000000
                    elif stability_button.collidepoint(event.pos):
                        nation_obj.stability_buildings += 1
                        nation_obj.balance -= 1000000
                    elif healthcare_button.collidepoint(event.pos):
                        nation_obj.healthcare_buildings += 1
                        nation_obj.balance -= 1000000
                    elif education_button.collidepoint(event.pos):
                        nation_obj.education_buildings += 1
                        nation_obj.balance -= 1000000
                    elif safety_button.collidepoint(event.pos):
                        nation_obj.safety_buildings += 1
                        nation_obj.balance -= 1000000
            
            # Dev
            
            if nation_obj.balance >= 100000:
                if land_button.collidepoint(event.pos):
                    nation_obj.area += 1000
                    nation_obj.balance -= 100000
                if infrastructure_button.collidepoint(event.pos):
                    nation_obj.infrastructure += 100
                    nation_obj.balance -= 100000

            # Panel events: dynamic toggle attached to panel edge
            toggle_rect = pygame.Rect(int(panel_x) - 40, 0, 40, 50)
            if toggle_rect.collidepoint(event.pos):
                panel_is_open = not panel_is_open

            if panel_x < WIDTH:  # Panel is visible (or sliding)
                # Panel navigation screens
                if panel_screen == "main":
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
                    if back_button.collidepoint(event.pos):
                        panel_screen = "main"
                    elif used_building_slots < nation_obj.building_slots and nation_obj.balance >= 1000000:
                        if commerce_panel_button.collidepoint(event.pos):
                            nation_obj.commerce_buildings += 1
                            nation_obj.balance -= 1000000
                        elif transport_panel_button.collidepoint(event.pos):
                            nation_obj.transport_buildings += 1
                            nation_obj.balance -= 1000000
                        elif stability_panel_button.collidepoint(event.pos):
                            nation_obj.stability_buildings += 1
                            nation_obj.balance -= 1000000
                        elif healthcare_panel_button.collidepoint(event.pos):
                            nation_obj.healthcare_buildings += 1
                            nation_obj.balance -= 1000000
                        elif education_panel_button.collidepoint(event.pos):
                            nation_obj.education_buildings += 1
                            nation_obj.balance -= 1000000
                        elif safety_panel_button.collidepoint(event.pos):
                            nation_obj.safety_buildings += 1
                            nation_obj.balance -= 1000000

                elif panel_screen == "investments":
                    pop_panel_button = pygame.Rect(panel_x + 20, 200, PANEL_WIDTH - 40, 50)
                    land_panel_button = pygame.Rect(panel_x + 20, 270, PANEL_WIDTH - 40, 50)
                    infra_panel_button = pygame.Rect(panel_x + 20, 340, PANEL_WIDTH - 40, 50)
                    back_button = pygame.Rect(panel_x + 20, 420, PANEL_WIDTH - 40, 40)
                    if back_button.collidepoint(event.pos):
                        panel_screen = "main"
                    elif nation_obj.balance >= 100000:
                        if pop_panel_button.collidepoint(event.pos):
                            nation_obj.population += 10000
                            nation_obj.balance -= 100000
                        elif land_panel_button.collidepoint(event.pos):
                            nation_obj.area += 1000
                            nation_obj.balance -= 100000
                        elif infra_panel_button.collidepoint(event.pos):
                            nation_obj.infrastructure += 100
                            nation_obj.balance -= 100000

    # ---- Draw ----
    
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
    used_building_slots = (
        nation_obj.commerce_buildings + nation_obj.transport_buildings
        + nation_obj.stability_buildings + nation_obj.healthcare_buildings
        + nation_obj.education_buildings + nation_obj.safety_buildings
    )
    stats_left = [
        f"Nation: {nation_obj.name}",
        f"Income: ${abbreviate_number(nation_obj.income)}",
        f"Population: {abbreviate_number(nation_obj.population)}",
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

    # ---- Buttons ----
    pygame.draw.rect(screen, (60, 140, 220), upgrade_button)
    pygame.draw.rect(screen, (200, 80, 80), exit_button)
    pygame.draw.rect(screen, (60, 140, 220), commerce_button)
    pygame.draw.rect(screen, (60, 140, 220), transport_button)
    pygame.draw.rect(screen, (60, 140, 220), land_button)
    pygame.draw.rect(screen, (60, 140, 220), infrastructure_button)
    pygame.draw.rect(screen, (60, 140, 220), stability_button)
    pygame.draw.rect(screen, (60, 140, 220), healthcare_button)
    pygame.draw.rect(screen, (60, 140, 220), education_button)
    pygame.draw.rect(screen, (60, 140, 220), safety_button)

    screen.blit(font.render("Population Upgrade (+100k)", True, (255, 255, 255)),
                (upgrade_button.x + 20, upgrade_button.y + 12))
    screen.blit(font.render("Save & Exit", True, (255, 255, 255)),
                (exit_button.x + 90, exit_button.y + 12))
    screen.blit(font.render("Commerce Buildings +1", True, (255, 255, 255)),
                (commerce_button.x + 20, commerce_button.y + 12))
    screen.blit(font.render("Transport Buildings +1", True, (255, 255, 255)),
                (transport_button.x + 20, transport_button.y + 12))
    screen.blit(font.render("Land +1000 sq km", True, (255, 255, 255)),
                (land_button.x + 20, land_button.y + 12))
    screen.blit(font.render("Infrastructure +1000", True, (255, 255, 255)),
                (infrastructure_button.x + 20, infrastructure_button.y + 12))
    screen.blit(font.render("Stability Buildings +1", True, (255, 255, 255)),
                (stability_button.x + 20, stability_button.y + 12))
    screen.blit(font.render("Healthcare Buildings +1", True, (255, 255, 255)),
                (healthcare_button.x + 20, healthcare_button.y + 12))
    screen.blit(font.render("Education Buildings +1", True, (255, 255, 255)),
                (education_button.x + 20, education_button.y + 12))
    screen.blit(font.render("Safety Buildings +1", True, (255, 255, 255)),
                (safety_button.x + 20, safety_button.y + 12))

    # ---- Panel Drawing ----
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
            print("hi")
        
        
        elif panel_screen == "buildings":
            commerce_panel_button = pygame.Rect(panel_x + 20, 200, PANEL_WIDTH - 40, 50)
            transport_panel_button = pygame.Rect(panel_x + 20, 270, PANEL_WIDTH - 40, 50)
            stability_panel_button = pygame.Rect(panel_x + 20, 340, PANEL_WIDTH - 40, 50)
            healthcare_panel_button = pygame.Rect(panel_x + 20, 410, PANEL_WIDTH - 40, 50)
            education_panel_button = pygame.Rect(panel_x + 20, 480, PANEL_WIDTH - 40, 50)
            safety_panel_button = pygame.Rect(panel_x + 20, 550, PANEL_WIDTH - 40, 50)
            back_button = pygame.Rect(panel_x + 20, 620, PANEL_WIDTH - 40, 40)
            pygame.draw.rect(screen, (60, 140, 220), commerce_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), transport_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), stability_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), healthcare_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), education_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), safety_panel_button)
            pygame.draw.rect(screen, (200, 80, 80), back_button)
            screen.blit(font.render("Commerce Buildings +1", True, (255, 255, 255)), (commerce_panel_button.x + 10, commerce_panel_button.y + 12))
            screen.blit(font.render("Transport Buildings +1", True, (255, 255, 255)), (transport_panel_button.x + 10, transport_panel_button.y + 12))
            screen.blit(font.render("Stability Buildings +1", True, (255, 255, 255)), (stability_panel_button.x + 10, stability_panel_button.y + 12))
            screen.blit(font.render("Healthcare Buildings +1", True, (255, 255, 255)), (healthcare_panel_button.x + 10, healthcare_panel_button.y + 12))
            screen.blit(font.render("Education Buildings +1", True, (255, 255, 255)), (education_panel_button.x + 10, education_panel_button.y + 12))
            screen.blit(font.render("Safety Buildings +1", True, (255, 255, 255)), (safety_panel_button.x + 10, safety_panel_button.y + 12))
            screen.blit(font.render("Buildings", True, (255, 255, 255)), (buildings_screen_button.x + 10, buildings_screen_button.y + 12))
            screen.blit(font.render("Investments", True, (255, 255, 255)), (investments_screen_button.x + 10, investments_screen_button.y + 12))
            screen.blit(font.render("Nation", True, (255, 255, 255)), (panel_x + 10, 100))

        elif panel_screen == "investments":
            pop_panel_button = pygame.Rect(panel_x + 20, 200, PANEL_WIDTH - 40, 50)
            land_panel_button = pygame.Rect(panel_x + 20, 270, PANEL_WIDTH - 40, 50)
            infra_panel_button = pygame.Rect(panel_x + 20, 340, PANEL_WIDTH - 40, 50)
            back_button = pygame.Rect(panel_x + 20, 420, PANEL_WIDTH - 40, 40)
            pygame.draw.rect(screen, (60, 140, 220), pop_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), land_panel_button)
            pygame.draw.rect(screen, (60, 140, 220), infra_panel_button)
            pygame.draw.rect(screen, (200, 80, 80), back_button)
            screen.blit(font.render("Population Upgrade (+100k)", True, (255, 255, 255)), (pop_panel_button.x + 10, pop_panel_button.y + 12))
            screen.blit(font.render("Land +1000 sq km", True, (255, 255, 255)), (land_panel_button.x + 10, land_panel_button.y + 12))
            screen.blit(font.render("Infrastructure +100", True, (255, 255, 255)), (infra_panel_button.x + 10, infra_panel_button.y + 12))
            screen.blit(font.render("Buildings", True, (255, 255, 255)), (buildings_screen_button.x + 10, buildings_screen_button.y + 12))
            screen.blit(font.render("Investments", True, (255, 255, 255)), (investments_screen_button.x + 10, investments_screen_button.y + 12))
            screen.blit(font.render("Nation", True, (255, 255, 255)), (panel_x + 10, 100))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
