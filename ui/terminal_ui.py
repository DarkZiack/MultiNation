import pygame
import os
import json

from data.nation import nation
from data.save_load import load_nation, save_nation
from engine.num_format import abbreviate_number
from engine.world import regions

# -------------------- CONFIG --------------------
WIDTH, HEIGHT = 1200, 800
FPS = 60

population_growth_per_minute = 5000
file_path = "nations_save.json"

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
                    nation_obj = nation(input_text.strip(), 1_000_000, 100, 5_000_000_000, 5_000_000_000, 5_000_000_000, selected_region)
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
exit_button = pygame.Rect(400, 480, 300, 50)

# -------------------- MAIN LOOP --------------------
running = True
timer = 0
timer_minute = 0


while running:
    timer += 1
    if timer == 62:
        timer_minute += 1
        timer = 0
    nation_obj.update_economy(nation_obj.income + 1000)
    nation_obj.population_density = nation_obj.calculate_density()
    # ---- Population growth ----
    if timer_minute >= 60:
        nation_obj.population += population_growth_per_minute
        timer_minute = 0

    save_nation(nation_obj, file_path)

    # ---- Events ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_nation(nation_obj, file_path)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if upgrade_button.collidepoint(event.pos):
                nation_obj.population += 100_000

            if exit_button.collidepoint(event.pos):
                save_nation(nation_obj, file_path)
                running = False

    # ---- Draw ----
    screen.fill((25, 25, 30))

    title = big_font.render(nation_obj.name, True, (255, 255, 255))
    screen.blit(title, (50, 30))
    text = font.render(str(60 - timer_minute), True, (220, 220, 220))
    screen.blit(text, (WIDTH-50, 20))
    region_text = font.render(nation_obj.world_region, True, (220, 220, 220))
    region_rect = region_text.get_rect(midtop=(WIDTH // 2, 20))
    screen.blit(region_text, region_rect)
    stats = [
        f"Nation: {nation_obj.name}",
        f"Population: {abbreviate_number(nation_obj.population)}",
        f"Area: {abbreviate_number(nation_obj.area)} sq km",
        f"Income: ${abbreviate_number(nation_obj.income)}",
        f"Population Density: {abbreviate_number(nation_obj.population_density)} people/sq km",
        f"GDP: ${abbreviate_number(nation_obj.gdp)}",
        f"GDP per Capita: ${abbreviate_number(nation_obj.gdp_per_capita)}",
    ]

    y = 100
    for stat in stats:
        text = font.render(stat, True, (220, 220, 220))
        screen.blit(text, (50, y))
        y += 40

    # ---- Buttons ----
    pygame.draw.rect(screen, (60, 140, 220), upgrade_button)
    pygame.draw.rect(screen, (200, 80, 80), exit_button)

    screen.blit(font.render("Population Upgrade (+100k)", True, (255, 255, 255)),
                (upgrade_button.x + 20, upgrade_button.y + 12))
    screen.blit(font.render("Save & Exit", True, (255, 255, 255)),
                (exit_button.x + 90, exit_button.y + 12))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
