import pygame
import pygame.freetype
import textwrap
import random
import os
import json

# Zorg dat afbeeldingen, muziek en highscores altijd gevonden worden,
# ongeacht vanuit welke map het spel gestart wordt.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# HIGHSCORE VARIABLES
highscore_file = "./highscores.json"
player_name = ""
score_saved = False
# GAME STATE VARIABLES
dollar = 500
total_poles = 1
max_poles = 10
spot_price = 250
debt = 2500
score = 1000
days = 0
final_score = 0

has_sea_permit = False
has_boat = False
game_active = False

fish_inventory = []
type_fish_fresh = ["Bass", "Catfish", "Salmon"]
type_fish_sea = ["Tuna", "Lobster", "Seahorse"]
fish_prices = {
    "Bass": 1,
    "Salmon": 2,
    "Catfish": 4,
    "Tuna": 2,
    "Lobster": 4,
    "Seahorse": 8,
}

multiplier_common = 1.0
multiplier_uncommon = 1.5
multiplier_rare = 2.5
multiplier_legendary = 4.0

pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Bob's Degenerate Fishing Adventure")
programIcon = pygame.image.load("./img/logo.png")
pygame.display.set_icon(programIcon)
BLUE = (106, 159, 181)
WHITE = (255, 255, 255)
DARK_BLUE = (50, 100, 130)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

input_font = pygame.freetype.SysFont("Courier", 24)


# soundvariables
sound1 = pygame.mixer.Sound('muziek/mud.ogg')
sound2 = pygame.mixer.Sound('muziek/wood.ogg')
step_delay = 350
last_step_time = 0

# muziek bg
pygame.mixer.music.load('muziek/bobmuziek.mp3')

pygame.mixer.music.play(-1, 0.0)

# PLAYER/MAP VARIABLES
player_x = 1290
player_y = 930
player_speed = 8

player_width_small = 72
player_height_small = 72
player_width_large = 96  # Larger size for interiors
player_height_large = 96  # Larger size for interiors
player_width = player_width_small
player_height = player_height_small

# CHARACTER ANIMATION VARIABLES
player_direction = "back"  # Current direction: "back", "front", "left", "right"
player_moving = False  # Is the player currently moving?
animation_frame = 0  # Current animation frame counter
animation_speed = 8  # Frames to wait before switching sprite (lower = faster)
animation_frame_counter = 0  # Counter for animation speed
current_sprite_state = "idle"  # Current sprite state: "idle" or "step"

overlay_return_pos = (player_x, player_y)
fishing_return_pos = (player_x, player_y)

current_transition = None  # Can be "fade_out", "fade_in" or None
fade_alpha = 0
fade_speed = 10

out_points = {
    "fishing_local": (626, 518),
    "fishing_sea": (1632, 513),
    "casino_map_entry": (795, 930),
    "casino_map_exit": (921, 915),
    "casino_don_return": (585, 675),
    "casino_lucky7_return": (1305, 675),
    "shop_map_entry": (1272, 453),
    "shop_map_exit": (921, 915),
    "shop_desk_return": (960, 780),
    "debtor_map_entry": (768, 473),
    "debtor_map_exit": (921, 915),
    "debtor_desk_return": (960, 780),
}
in_screens = {
    "fishing": "fishing_local_results",
    "casino_map_entry": "casino_map",
    "casino_map_exit": "game",
    "don_desk": "casino_don_game",
    "lucky7_desk": "casino_lucky7_game",
    "shop_map_entry": "shop_map",
    "shop_map_exit": "game",
    "shop_desk": "shop",
    "debtor_map_entry": "debtor_map",
    "debtor_map_exit": "game",
    "debtor": "debtor",
}
fade_target_screen = None
fade_return_pos = None

NO_FADE_SCREENS = {
    "shop",
    "debtor",
    "casino_don_game",
    "casino_lucky7_game",
    "fishing_local_results",
}

# STORY AND STATUS STRINGS
story_text = (
    "**Bob's Degenerate Fishing Adventure**\n"
    "\n"
    "**THE STORY**\n"
    "Two years ago, Bob lost everything to a gambling addiction, including his savings and family.\n"
    "He is now burdened with a massive debt of **$2,500**.\n\n"
    "Determined to rebuild his life, Bob returns to his old passion: fishing.\n"
    "His goal is to sell his catch to the local dealer to slowly pay off his debt.\n\n"
    "However, a new, glittering **Casino** has opened downtown.\n"
    "Will Bob pay off his debt, or succumb to the temptations of gambling?\n\n"
    "**HOW TO PLAY**\n"
    "* **Movement:** Use **WASD** or the **Arrow Keys** to move around the map.\n"
    "* **Enter Locations:** Walk onto a door area for instant transitions.\n"
    "* **Fishing:** Press **E** at the designated fishing spots to fish.\n"
    "* **Menu/Back:** Press **ESC** to open the pause menu or exit from shops/casinos.\n"
)


fishing_result_text = ""
end_text = ""
status_message = ""
don_bet_input_text = ""
lucky7_bet_input_text = ""
current_screen = "splash"
pause_from_screen = None  # Tracks which screen we paused from

# SPLASH SCREEN VARIABLES
splash_alpha = 0
splash_state = "starting"  # Can be "starting", "fade_in", "hold", "fade_out"
splash_starting_timer = 0
splash_starting_duration = 15
splash_hold_timer = 0
splash_hold_duration = 120
splash_fade_speed = 5

# MENU FADE VARIABLES
menu_alpha = 0
menu_fade_active = False
menu_fade_speed = 5


# HELPER FUNCTIONS
def create_surface_with_text(text, font_size, text_rgb, bg_rgb=None):
    font = pygame.freetype.SysFont("Courier", font_size, bold=True)
    surface, _ = font.render(text=text, fgcolor=text_rgb, bgcolor=bg_rgb)
    return surface.convert_alpha()


def calculate_text_dimensions(text, font_size, max_width):
    """Calculates the width and height of a text block."""
    font = pygame.freetype.SysFont("Courier", int(font_size), bold=True)
    est_char_width = font_size * 0.55
    max_chars = max(20, int(max_width / est_char_width))

    lines = []

    clean_text = text.replace("**", "")

    for paragraph in clean_text.split("\n"):
        wrapped = textwrap.wrap(paragraph, width=max_chars)
        if not wrapped:
            lines.append("")
        else:
            lines.extend(wrapped)

    max_line_width = 0
    for line in lines:
        surf, _ = font.render(line, fgcolor=(255, 255, 255))
        text_rect = surf.get_rect()
        max_line_width = max(max_line_width, text_rect.width)

    line_height = int(font_size * 1.2)
    total_height = len(lines) * line_height

    return max_line_width, total_height


def render_text_block(surface, text, font_size, color, x, y, max_width, align="left"):
    base_font_name = "courier"

    est_char_width = font_size * 0.55
    max_chars = max(20, int(max_width / est_char_width))

    lines_to_render = []

    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        is_heading_or_bold = paragraph.startswith("**")

        clean_paragraph = paragraph.replace("**", "")

        wrapped_lines = textwrap.wrap(clean_paragraph, width=max_chars)

        if not wrapped_lines:
            lines_to_render.append(("", is_heading_or_bold))
        else:
            lines_to_render.append((wrapped_lines[0], is_heading_or_bold))
            for line in wrapped_lines[1:]:
                lines_to_render.append((line, False))

    line_height = int(font_size * 1.2)
    current_y = y

    for line, is_bold in lines_to_render:
        font_style = pygame.freetype.SysFont(
            base_font_name, int(font_size), bold=is_bold
        )

        if line.strip().startswith("*"):
            font_style = pygame.freetype.SysFont(
                base_font_name, int(font_size), bold=False
            )

        surf, _ = font_style.render(line, fgcolor=color)
        text_rect = surf.get_rect()

        if align == "center":
            line_x = x + (max_width - text_rect.width) // 2
        elif align == "right":
            line_x = x + (max_width - text_rect.width)
        else:
            line_x = x

        surface.blit(surf, (line_x, current_y))
        current_y += line_height


def draw_button(surface, rect, text, text_color, color):
    pygame.draw.rect(surface, color, rect)

    max_font_size = int(rect.height * 0.6)
    font = pygame.freetype.SysFont("Courier", max_font_size, bold=True)

    text_surf, _ = font.render(text, fgcolor=text_color)
    text_rect = text_surf.get_rect(center=rect.center)

    while text_rect.width > rect.width * 0.9 and max_font_size > 10:
        max_font_size -= 1
        font = pygame.freetype.SysFont("Courier", max_font_size, bold=True)
        text_surf, _ = font.render(text, fgcolor=text_color)
        text_rect = text_surf.get_rect(center=rect.center)

    surface.blit(text_surf, text_rect)


def button_clicked(rect, event):
    return (
        event.type == pygame.MOUSEBUTTONDOWN
        and rect.collidepoint(event.pos)
        and event.button == 1
    )


def get_button_rect(screen_width, screen_height, y_factor=0.4, x_factor=0.4):
    x = int(screen_width * x_factor)
    y = int(screen_height * y_factor)
    w = int(screen_width * 0.2)
    h = int(screen_height * 0.1)
    return pygame.Rect(x, y, w, h)


def calculate_fish_value(fish):
    rarity = fish["Rarity"]
    if rarity == "Common":
        mul = multiplier_common
    elif rarity == "Uncommon":
        mul = multiplier_uncommon
    elif rarity == "Rare":
        mul = multiplier_rare
    else:
        mul = multiplier_legendary

    base = fish_prices[fish["Type"]]
    return round(base * mul * (fish["Weight"] * 1.1), 2)


def print_inventory():
    global fish_inventory

    total_value = calculate_total_value(fish_inventory)

    inv_print = "=== Inventory (Max 20 Shown) ===\n"
    inv_print += "Nr. | Type | Rarity | Weight (kg) | Value\n"
    inv_print += "-" * 40 + "\n"

    for i, fish in enumerate(fish_inventory[:20], start=1):
        value = calculate_fish_value(fish)
        inv_print += f"{i:<3} | {fish['Type']:<7} | {fish['Rarity']:<8} | {fish['Weight']:<4} | ${value:,.2f}\n"

    if len(fish_inventory) > 20:
        inv_print += "...\n"

    inv_print += "-" * 40 + "\n"
    inv_print += f"Total fish: {len(fish_inventory)}\n"
    inv_print += f"Total value: ${total_value:,.2f}\n"

    return inv_print


def calculate_total_value(inv):
    return round(sum(calculate_fish_value(f) for f in inv), 2)


def calculate_score():
    global dollar, score, days
    calculated_score = score - days * 10
    calculated_score += dollar
    return max(0, int(calculated_score))


def check_rank(score):
    if score <= 0:
        return "a Bankrupt Fisherman"
    elif 0 < score <= 10000:
        return "a Rookie Fisherman"
    elif 10000 < score <= 50000:
        return "a Seasoned Fisherman"
    elif 50000 < score <= 100000:
        return "a Successful Captain"
    else:
        return "a Legend of the Seas"


def load_high_scores():
    if not os.path.exists(highscore_file):
        return []

    try:
        with open(highscore_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_high_score(name, score):

    scores = load_high_scores()

    new_save = {"name": name, "score": score}
    scores.append(new_save)

    scores.sort(key=lambda x: x["score"], reverse=True)

    with open(highscore_file, "w") as f:
        json.dump(scores, f, indent=4)


def get_highscore_string():

    scores = load_high_scores()
    output = "HIGH SCORES:\n\n"
    if not scores:
        return output + "No scores yet!"

    for i, entry in enumerate(scores[:10], start=1):
        output += f"{i}. {entry['name'][:10]:<9} : {entry['score']:>8}\n"
    return output


def get_current_collision_map():
    """Returns the correct collision map based on the current screen."""
    if current_screen == "game" or current_screen == "fishing_local_results":
        return collision_map_game
    elif current_screen == "debtor_map":
        return collision_map_debtor
    elif current_screen == "shop_map":
        return collision_map_shop
    elif current_screen == "casino_map":
        return collision_map_casino
    return None


def check_collision(x, y, collision_map):
    """
    Checks if the player collides with a collision pixel.
    """
    global player_width, player_height

    if collision_map is None:
        return False

    if (
        x < 0
        or y < 0
        or x + player_width >= screen.get_width()
        or y + player_height >= screen.get_height()
    ):
        return True

    # Check collision map pixels
    points_to_check = [
        (x, y),  # Top-left
        (x + player_width - 1, y),  # Top-right
        (x, y + player_height - 1),  # Bottom-left
        (x + player_width - 1, y + player_height - 1),  # Bottom-right
    ]

    for point_x, point_y in points_to_check:
        if 0 <= point_x < screen.get_width() and 0 <= point_y < screen.get_height():
            try:
                pixel_color = collision_map.get_at((int(point_x), int(point_y)))

                # Black pixels are collision
                if (
                    pixel_color[0] < 128
                    and pixel_color[1] < 128
                    and pixel_color[2] < 128
                ):
                    return True

            except IndexError:
                return True

    return False


def check_door_collision(x, y):
    """Checks if the player is near an interactive 'door'."""
    global player_width, player_height

    player_rect = pygame.Rect(x, y, player_width, player_height)

    if current_screen == "game":
        doors = {
            "fishing_local": pygame.Rect(183, 437, 375, 375),
            "fishing_sea_prompt": pygame.Rect(1632, 506, 45, 45),
            "casino_map_entry": pygame.Rect(783, 870, 45, 45),
            "shop_map_entry": pygame.Rect(1290, 383, 45, 45),
            "debtor_map_entry": pygame.Rect(792, 390, 45, 45),
        }
    elif current_screen == "debtor_map":
        doors = {
            "debtor_map_exit": pygame.Rect(930, 1020, 60, 30),
            "debtor_desk": pygame.Rect(885, 675, 150, 75),
        }
    elif current_screen == "shop_map":
        doors = {
            "shop_map_exit": pygame.Rect(930, 1020, 60, 30),
            "shop_desk": pygame.Rect(885, 675, 150, 75),
        }
    elif current_screen == "casino_map":
        doors = {
            "casino_map_exit": pygame.Rect(930, 1020, 60, 30),
            "don_desk": pygame.Rect(329, 825, 150, 300),
            "lucky7_desk": pygame.Rect(1514, 518, 150, 150),
        }
    else:
        return None

    for location, door_rect in doors.items():
        if player_rect.colliderect(door_rect):
            return location
    return None


def check_door_collision_and_fade(x, y):
    """
    Checks if the player hits a door and immediately starts the transition
    """
    global current_transition, fade_target_screen, fade_return_pos

    if current_transition is None:
        door = check_door_collision(x, y)

        if door == "casino_map_entry":  # Large map -> Casino Map
            start_transition(
                in_screens["casino_map_entry"], out_points["casino_map_exit"]
            )
            return True
        elif door == "casino_map_exit":  # Casino Map -> Large map
            start_transition(
                in_screens["casino_map_exit"], out_points["casino_map_entry"]
            )
            return True

        # Shop Door
        elif door == "shop_map_entry":  # Large map -> Shop Map
            start_transition(in_screens["shop_map_entry"], out_points["shop_map_exit"])
            return True
        elif door == "shop_map_exit":  # Shop Map -> Large map
            start_transition(in_screens["shop_map_exit"], out_points["shop_map_entry"])
            return True

        # Debtor Door
        elif door == "debtor_map_entry":
            # Large map -> Debtor Map
            start_transition(
                in_screens["debtor_map_entry"], out_points["debtor_map_exit"]
            )
            return True
        elif door == "debtor_map_exit":
            # Debtor Map -> Large map
            start_transition(
                in_screens["debtor_map_exit"], out_points["debtor_map_entry"]
            )
            return True

    return False


def generate_fishing_results():
    global total_poles, days, fish_inventory

    days += 1

    if current_screen == "sea_fishing_cutscene":
        fish_type_list = type_fish_sea
        header = "You successfully fished at SEA!"
    else:
        fish_type_list = type_fish_fresh
        header = "You successfully fished locally!"

    current_catch = []
    tries = total_poles

    while tries > 0:
        tries -= 1

        if random.randint(0, 1) == 1:
            rarity_num = random.randint(0, 100)
            if rarity_num <= 40:
                rarity = "Common"
            elif rarity_num <= 70:
                rarity = "Uncommon"
            elif rarity_num <= 95:
                rarity = "Rare"
            else:
                rarity = "Legendary"

            weight_num = random.randint(0, 100)
            if weight_num <= 40:
                weight = random.randint(1, 5)
            elif weight_num <= 70:
                weight = random.randint(5, 10)
            elif weight_num <= 95:
                weight = random.randint(10, 20)
            else:
                weight = random.randint(20, 30)

            fish = {
                "Type": random.choice(fish_type_list),
                "Rarity": rarity,
                "Weight": weight,
            }

            fish_inventory.append(fish)
            current_catch.append(fish)

    if not current_catch:
        return f"{header}\n\nYou caught NOTHING today."

    output = [header, "", "Today's Catch:"]

    for i, fish in enumerate(current_catch, start=1):
        val = calculate_fish_value(fish)
        output.append(
            f"{i}. {fish['Type']} | {fish['Rarity']} | {fish['Weight']}kg | ${val:,.2f}"
        )

    output.append("")

    return "\n".join(output)


# INITIALIZATION AND IMAGE LOADING

screen_width, screen_height = screen.get_size()
font_size = int(screen_height * 0.05)
default_font_size = int(screen_height * 0.035)
inv_font_size = int(screen_height * 0.025)
story_font_size = 30

# Button Rects
start_button_rect = get_button_rect(
    screen_width, screen_height, y_factor=0.40, x_factor=0.21
)
quit_button_rect = get_button_rect(
    screen_width, screen_height, y_factor=0.55, x_factor=0.21
)
continue_button_rect = get_button_rect(
    screen_width,
    screen_height,
    y_factor=0.85,
    x_factor=0.4,
)

end_button_rect = get_button_rect(screen_width, screen_height, y_factor=0.65)
play_again_rect = get_button_rect(screen_width, screen_height, y_factor=0.74)
quit_rect = get_button_rect(screen_width, screen_height, y_factor=0.87)

# Pause Menu Buttons
pause_button_width = int(screen_width * 0.28)
pause_button_height = int(screen_height * 0.1)
pause_button_x = int(screen_width * 0.36)
pause_resume_rect = pygame.Rect(
    pause_button_x, int(screen_height * 0.35), pause_button_width, pause_button_height
)
pause_mainmenu_rect = pygame.Rect(
    pause_button_x, int(screen_height * 0.50), pause_button_width, pause_button_height
)
pause_quit_rect = pygame.Rect(
    pause_button_x, int(screen_height * 0.65), pause_button_width, pause_button_height
)

x_margin = int(screen_width * 0.05)
y_margin = int(screen_height * 0.05)
max_text_width = int(screen_width * 0.9)

# Image loading
try:
    base_dir = (
        os.path.dirname(os.path.abspath(__file__))
        if "__file__" in locals()
        else os.getcwd()
    )
    img_dir = os.path.join(base_dir, "img")

    splashscreen_image = pygame.image.load(
        os.path.join(img_dir, "splashscreen-logo.png")
    ).convert()
    background_image = pygame.image.load(os.path.join(img_dir, "bobfish.png")).convert()
    sea_fishing_image = pygame.image.load(
        os.path.join(img_dir, "sea_fishing_img.png")
    ).convert()
    end_image = pygame.image.load(os.path.join(img_dir, "endimg.jpeg")).convert()

    game_map_with_boat = pygame.image.load(
        os.path.join(img_dir, "gamemap_with_boat.png")
    ).convert_alpha()
    game_map_without_boat = pygame.image.load(
        os.path.join(img_dir, "gamemap_without_boat.png")
    ).convert_alpha()
    collision_map_game = pygame.image.load(
        os.path.join(img_dir, "collission_map.png")
    ).convert_alpha()

    # Load all character sprites
    character_dir = os.path.join(img_dir, "character")

    # Back sprites (moving up)
    back_idle_raw = pygame.image.load(os.path.join(character_dir, "back-idle.png"))
    back_step_raw = pygame.image.load(os.path.join(character_dir, "back-step.png"))

    # Front sprites (moving down)
    front_idle_raw = pygame.image.load(os.path.join(character_dir, "front-idle.png"))
    front_step_raw = pygame.image.load(os.path.join(character_dir, "front-step.png"))

    # Left sprites (moving left)
    left_idle_raw = pygame.image.load(os.path.join(character_dir, "left-idle.png"))
    left_step_raw = pygame.image.load(os.path.join(character_dir, "left-step.png"))

    # Right sprites (moving right)
    right_idle_raw = pygame.image.load(os.path.join(character_dir, "right-idle.png"))
    right_step_raw = pygame.image.load(os.path.join(character_dir, "right-step.png"))

    # Scale assets to screen size
    scale_size = (screen_width, screen_height)
    splashscreen_image = pygame.transform.scale(splashscreen_image, scale_size)
    background_image = pygame.transform.scale(background_image, scale_size)
    sea_fishing_image = pygame.transform.scale(sea_fishing_image, scale_size)
    end_image = pygame.transform.scale(end_image, scale_size)
    game_map_with_boat = pygame.transform.scale(game_map_with_boat, scale_size)
    game_map_without_boat = pygame.transform.scale(game_map_without_boat, scale_size)
    collision_map_game = pygame.transform.scale(collision_map_game, scale_size)

    # Scale character sprites for small size (outside)
    back_idle_small = pygame.transform.scale(
        back_idle_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    back_step_small = pygame.transform.scale(
        back_step_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    front_idle_small = pygame.transform.scale(
        front_idle_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    front_step_small = pygame.transform.scale(
        front_step_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    left_idle_small = pygame.transform.scale(
        left_idle_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    left_step_small = pygame.transform.scale(
        left_step_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    right_idle_small = pygame.transform.scale(
        right_idle_raw, (player_width_small, player_height_small)
    ).convert_alpha()
    right_step_small = pygame.transform.scale(
        right_step_raw, (player_width_small, player_height_small)
    ).convert_alpha()

    # Scale character sprites for large size (interiors)
    back_idle_large = pygame.transform.scale(
        back_idle_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    back_step_large = pygame.transform.scale(
        back_step_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    front_idle_large = pygame.transform.scale(
        front_idle_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    front_step_large = pygame.transform.scale(
        front_step_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    left_idle_large = pygame.transform.scale(
        left_idle_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    left_step_large = pygame.transform.scale(
        left_step_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    right_idle_large = pygame.transform.scale(
        right_idle_raw, (player_width_large, player_height_large)
    ).convert_alpha()
    right_step_large = pygame.transform.scale(
        right_step_raw, (player_width_large, player_height_large)
    ).convert_alpha()

    # Dictionary to easily access sprites
    character_sprites_small = {
        "back_idle": back_idle_small,
        "back_step": back_step_small,
        "front_idle": front_idle_small,
        "front_step": front_step_small,
        "left_idle": left_idle_small,
        "left_step": left_step_small,
        "right_idle": right_idle_small,
        "right_step": right_step_small,
    }

    character_sprites_large = {
        "back_idle": back_idle_large,
        "back_step": back_step_large,
        "front_idle": front_idle_large,
        "front_step": front_step_large,
        "left_idle": left_idle_large,
        "left_step": left_step_large,
        "right_idle": right_idle_large,
        "right_step": right_step_large,
    }

    # Interior Maps
    debtor_map_image = pygame.image.load(
        os.path.join(img_dir, "debt_interior.png")
    ).convert_alpha()
    collision_map_debtor = pygame.image.load(
        os.path.join(img_dir, "debt_collission.png")
    ).convert_alpha()
    shop_map_image = pygame.image.load(
        os.path.join(img_dir, "shop_interior.png")
    ).convert_alpha()
    collision_map_shop = pygame.image.load(
        os.path.join(img_dir, "shop_collission.png")
    ).convert_alpha()
    casino_map_image = pygame.image.load(
        os.path.join(img_dir, "casino_interior.png")
    ).convert_alpha()
    collision_map_casino = pygame.image.load(
        os.path.join(img_dir, "casino_collission.png")
    ).convert_alpha()

    debtor_map_image = pygame.transform.scale(debtor_map_image, scale_size)
    collision_map_debtor = pygame.transform.scale(collision_map_debtor, scale_size)
    shop_map_image = pygame.transform.scale(shop_map_image, scale_size)
    collision_map_shop = pygame.transform.scale(collision_map_shop, scale_size)
    casino_map_image = pygame.transform.scale(casino_map_image, scale_size)
    collision_map_casino = pygame.transform.scale(collision_map_casino, scale_size)

    game_map = game_map_without_boat

    # Button images
    start_button_image = pygame.image.load(os.path.join(img_dir, "start_button.png"))
    quit_button_image = pygame.image.load(os.path.join(img_dir, "quit_button.png"))
    resume_button_image = pygame.image.load(os.path.join(img_dir, "resume_button.png"))
    mainmenu_button_image = pygame.image.load(
        os.path.join(img_dir, "mainmenu_button.png")
    )
    quitgame_button_image = pygame.image.load(
        os.path.join(img_dir, "quitgame_button.png")
    )

    start_button_image = pygame.transform.scale(
        start_button_image, (start_button_rect.width, start_button_rect.height)
    )
    quit_button_image = pygame.transform.scale(
        quit_button_image, (quit_button_rect.width, quit_button_rect.height)
    )
    resume_button_image = pygame.transform.scale(
        resume_button_image, (pause_resume_rect.width, pause_resume_rect.height)
    )
    mainmenu_button_image = pygame.transform.scale(
        mainmenu_button_image, (pause_mainmenu_rect.width, pause_mainmenu_rect.height)
    )
    quitgame_button_image = pygame.transform.scale(
        quitgame_button_image, (pause_quit_rect.width, pause_quit_rect.height)
    )


except pygame.error as e:
    print(
        f"Error loading images. Ensure the 'img' folder exists and contains the files: {e}"
    )
    # Fallback initialization
    fallback_surface = pygame.Surface((screen_width, screen_height))
    fallback_surface.fill(DARK_BLUE)
    fallback_char_small = pygame.Surface((player_width_small, player_height_small))
    fallback_char_small.fill(BLUE)
    fallback_char_large = pygame.Surface((player_width_large, player_height_large))
    fallback_char_large.fill(BLUE)
    fallback_collision = pygame.Surface((screen_width, screen_height))
    fallback_collision.fill(WHITE)

    splashscreen_image = fallback_surface
    background_image = fallback_surface
    sea_fishing_image = fallback_surface
    end_image = fallback_surface
    start_button_image = fallback_surface
    quit_button_image = fallback_surface
    resume_button_image = fallback_surface
    mainmenu_button_image = fallback_surface
    quitgame_button_image = fallback_surface

    game_map_with_boat = fallback_surface
    game_map_without_boat = fallback_surface
    game_map = fallback_surface
    collision_map_game = fallback_collision
    debtor_map_image = fallback_surface
    collision_map_debtor = fallback_collision
    shop_map_image = fallback_surface
    collision_map_shop = fallback_collision
    casino_map_image = fallback_surface
    collision_map_casino = fallback_collision

    character_img_small = fallback_char_small
    character_img_large = fallback_char_large
    character_img = fallback_char_small


running = True
clock = pygame.time.Clock()


# FADE TRANSITION FUNCTION
def start_transition(target, return_pos=None):
    """
    Starts the fade transition and manages player size/image during screen change.
    """
    global current_transition, fade_alpha, fade_target_screen, fade_return_pos, current_screen
    global player_x, player_y, overlay_return_pos, player_width, player_height

    perform_full_fade = (
        target not in NO_FADE_SCREENS and current_screen not in NO_FADE_SCREENS
    )

    if current_screen in ["fishing_local_results"] and target == "game":
        perform_full_fade = False

    if target in ["fishing_local_results"]:
        perform_full_fade = False

    if perform_full_fade:
        current_transition = "fade_out"
        fade_alpha = 0
        fade_target_screen = target
        fade_return_pos = return_pos
    else:

        if target in NO_FADE_SCREENS and current_screen in [
            "casino_map",
            "shop_map",
            "debtor_map",
            "game",
        ]:
            overlay_return_pos = (player_x, player_y)

        current_transition = None
        current_screen = target

        if current_screen in [
            "debtor_map",
            "shop_map",
            "casino_map",
            "shop",
            "debtor",
            "casino_don_game",
            "casino_lucky7_game",
        ]:
            player_width = player_width_large
            player_height = player_height_large
        else:
            player_width = player_width_small
            player_height = player_height_small

        if current_screen in ["game", "debtor_map", "shop_map", "casino_map"]:
            if current_screen in ["casino_map", "shop_map", "debtor_map"]:
                if current_screen == "game" and return_pos is not None:
                    player_x, player_y = return_pos
                elif current_screen != "game" and return_pos is not None:
                    player_x, player_y = return_pos
            elif current_screen == "game" and return_pos is not None:
                player_x, player_y = return_pos

        if current_screen in ["fishing_local_results", "sea_fishing_cutscene"]:
            global fishing_result_text
            fishing_result_text = generate_fishing_results()
        elif current_screen == "debtor_map":
            global status_message
            status_message = "I've been expecting you, Bob. Please, take a seat."
        elif current_screen == "shop_map":
            status_message = "Welcome to the shop, fisherman! What can I get for you?"
        elif current_screen == "casino_map":
            status_message = "Feeling lucky, Bob? Pick a table."
        else:
            status_message = ""


# MAIN GAME LOOP
fishing_return_pos = (player_x, player_y)

while running:

    def get_shop_button_rect_styled(y_factor, height_factor=0.1):
        menu_area_width = int(screen_width * 0.50)
        x_margin = int(screen_width * 0.05)

        menu_area_inner_x = screen_width - menu_area_width - x_margin + 5

        button_area_width = int((menu_area_width - 10) * 0.8)
        button_area_x = menu_area_inner_x + (menu_area_width - 10) * 0.1
        w = button_area_width
        h = int(screen_height * height_factor)
        x = button_area_x
        y = int(screen_height * y_factor)
        return pygame.Rect(x, y, w, h)

    shop_sellfish_rect = get_shop_button_rect_styled(0.25)
    shop_buypoles_rect = get_shop_button_rect_styled(0.40)
    shop_buyboat_rect = get_shop_button_rect_styled(0.55)
    shop_buyperm_rect = get_shop_button_rect_styled(0.70)

    stats_text = (
        f"Total days: {days}\n"
        f"Total money: ${round(dollar, 2):,.2f}\n"
        f"Total poles: {total_poles}\n"
        f"Total fish: {len(fish_inventory)}"
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # MENU LOGIC
        elif current_screen == "menu":
            if button_clicked(start_button_rect, event):
                start_transition("name_input")
            if button_clicked(quit_button_rect, event):
                running = False
        elif current_screen == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(player_name) > 0:
                        start_transition("description")
                elif event.key == pygame.K_ESCAPE:
                    start_transition("menu")
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10 and event.unicode.isprintable():
                        player_name += event.unicode

        elif current_screen == "description":
            if button_clicked(continue_button_rect, event):
                start_transition("game", (player_x, player_y))

        elif current_screen == "game" and current_transition is None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_from_screen = "game"
                    current_screen = "pause_menu"
                elif event.key == pygame.K_e:
                    door = check_door_collision(player_x, player_y)

                    if door == "fishing_sea_prompt":
                        if has_boat and has_sea_permit:
                            fishing_return_pos = (player_x, player_y)
                            start_transition("sea_fishing_cutscene", fishing_return_pos)
                        else:
                            status_message = (
                                "You need a boat and a sea permit to venture out here!"
                            )

                    elif door == "fishing_local":
                        fishing_return_pos = (player_x, player_y)
                        start_transition("fishing_local_results", fishing_return_pos)

                    elif door == "debtor_desk":
                        # Not used here (only on debtor_map)
                        pass
                    elif door == "shop_desk":
                        # Not used here (only on shop_map)
                        pass

        # DEBTOR MAP LOGIC
        elif current_screen == "debtor_map" and current_transition is None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_from_screen = "debtor_map"
                    current_screen = "pause_menu"
                elif event.key == pygame.K_e:
                    door = check_door_collision(player_x, player_y)
                    if door == "debtor_desk":
                        start_transition(
                            in_screens["debtor"], out_points["debtor_desk_return"]
                        )
                        status_message = ""

        # SHOP MAP LOGIC
        elif current_screen == "shop_map" and current_transition is None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_from_screen = "shop_map"
                    current_screen = "pause_menu"
                elif event.key == pygame.K_e:
                    door = check_door_collision(player_x, player_y)
                    if door == "shop_desk":
                        start_transition(
                            in_screens["shop_desk"], out_points["shop_desk_return"]
                        )
                        status_message = "Welcome! What can I help you with?"

        # CASINO MAP LOGIC
        elif current_screen == "casino_map" and current_transition is None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_from_screen = "casino_map"
                    current_screen = "pause_menu"
                elif event.key == pygame.K_e:
                    door = check_door_collision(player_x, player_y)
                    if door == "don_desk":
                        start_transition(
                            in_screens["don_desk"], out_points["casino_don_return"]
                        )
                        don_bet_input_text = ""
                        status_message = ""
                    elif door == "lucky7_desk":
                        start_transition(
                            in_screens["lucky7_desk"],
                            out_points["casino_lucky7_return"],
                        )
                        lucky7_bet_input_text = ""
                        status_message = ""

        # FISHING LOGIC (LOCAL)
        elif current_screen == "fishing_local_results":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_transition("game", fishing_return_pos)
                status_message = ""

        # FISHING LOGIC (SEA)
        elif current_screen == "sea_fishing_cutscene":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_transition("game", fishing_return_pos)
                status_message = ""

        # SHOP INTERACTION LOGIC
        elif current_screen == "shop":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_transition("shop_map", None)
                status_message = "See you later, Bob."

            if button_clicked(shop_buyboat_rect, event):
                if has_boat:
                    status_message = "You already own a boat."
                elif dollar >= 500:
                    dollar -= 500
                    has_boat = True
                    status_message = "You bought a boat!"
                else:
                    status_message = "Not enough money."

            elif button_clicked(shop_buyperm_rect, event):
                if has_sea_permit:
                    status_message = "You already own a permit."
                elif dollar >= 100:
                    dollar -= 100
                    has_sea_permit = True
                    status_message = "You bought a sea permit!"
                else:
                    status_message = "Not enough money."

            elif button_clicked(shop_buypoles_rect, event):
                if dollar >= spot_price and total_poles < max_poles:
                    dollar -= spot_price
                    total_poles += 1
                    spot_price += 250
                    status_message = f"You bought a pole. Now {total_poles} poles."
                elif total_poles >= max_poles:
                    status_message = "You cannot buy more poles."
                else:
                    status_message = "Not enough money."

            elif button_clicked(shop_sellfish_rect, event):
                if len(fish_inventory) == 0:
                    status_message = "You have no fish to sell."
                else:
                    total_val = calculate_total_value(fish_inventory)
                    dollar += total_val
                    fish_inventory.clear()
                    status_message = f"You sold all fish for ${total_val:,.2f}."

        # CASINO GAME LOGIC
        elif current_screen == "casino_don_game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_transition("casino_map", None)
                    status_message = ""
                    don_bet_input_text = ""
                elif event.key == pygame.K_RETURN:
                    if don_bet_input_text.isdigit():
                        bet = int(don_bet_input_text)
                        if bet == 0:
                            status_message = "You cannot bet 0."
                        elif bet > dollar:
                            status_message = "Not enough money."
                        else:
                            flip_num = random.randint(0, 1)
                            if flip_num == 1:
                                dollar += bet
                                days += 1
                                status_message = (
                                    f"You won +${bet}. "
                                    f"Your current balance is ${round(dollar, 2):,.2f}. Press ESC to return."
                                )
                            elif flip_num == 0:
                                dollar -= bet
                                days += 1
                                status_message = (
                                    f"You lost -${bet}. "
                                    f"Your current balance is ${round(dollar, 2):,.2f}. Press ESC to return."
                                )
                            don_bet_input_text = ""
                    else:
                        status_message = "Invalid bet amount."
                elif event.key == pygame.K_BACKSPACE:
                    don_bet_input_text = don_bet_input_text[:-1]
                elif event.unicode.isdigit():
                    don_bet_input_text += event.unicode

        elif current_screen == "casino_lucky7_game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    start_transition("casino_map", None)
                    lucky7_bet_input_text = ""
                    status_message = ""
                elif event.key == pygame.K_RETURN:
                    if lucky7_bet_input_text.isdigit():
                        bet = int(lucky7_bet_input_text)
                        if bet == 0:
                            status_message = "You cannot bet 0."
                        elif bet > dollar:
                            status_message = "Not enough money."
                        else:
                            flip_num = random.randint(1, 7)
                            if flip_num == 1:
                                win_amount = bet * 6
                                dollar += win_amount
                                days += 1
                                status_message = (
                                    f"LUCKY 7! You have won +${win_amount:,.2f}. "
                                    f"Your current balance is ${round(dollar, 2):,.2f}. "
                                    f"Press ESC to return."
                                )
                            else:
                                dollar -= bet
                                days += 1
                                status_message = (
                                    f"Unlucky! You have lost -${bet}. "
                                    f"Your current balance is ${round(dollar, 2):,.2f}. "
                                    f"Press ESC to return."
                                )
                            lucky7_bet_input_text = ""
                    else:
                        status_message = "Invalid bet amount."
                elif event.key == pygame.K_BACKSPACE:
                    lucky7_bet_input_text = lucky7_bet_input_text[:-1]
                elif event.unicode.isdigit():
                    lucky7_bet_input_text += event.unicode

        # DEBTOR INTERACTION SCREEN
        elif current_screen == "debtor":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_transition("debtor_map", None)
                status_message = "Get back to work, Bob."

            if button_clicked(end_button_rect, event):
                if dollar >= debt:
                    start_transition("end")
                    dollar -= debt
                    final_score = calculate_score()
                    final_rank = check_rank(final_score)

                    end_text = (
                        f"After working so hard, Bob has finally done it. "
                        f"He's once again a free man — free of debt and free of any burden.\n\n"
                        f"What will Bob do next now that he's free? To be continued.\n\n"
                        f"===== End =====\n\n"
                        f"Thanks for playing Bob's Degenerate Fishing Adventure!\n"
                        f"Your end score is {final_score}.\n"
                        f"It took you {days} days to pay off your debt.\n"
                        f"After paying your debt, you had a total of ${round(dollar, 2):,.2f}.\n"
                        f"You are {final_rank}."
                    )
                else:
                    status_message = (
                        f"I cannot accept a partial payment, Bob. "
                        f"You still owe me ${debt - dollar:,.2f}. "
                        f"Get back to work!"
                    )

        # PAUSE MENU LOGIC
        elif current_screen == "pause_menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_screen = pause_from_screen
                pause_from_screen = None
            elif button_clicked(pause_resume_rect, event):
                # Resume game
                current_screen = pause_from_screen
                pause_from_screen = None
            elif button_clicked(pause_mainmenu_rect, event):
                # Reset game state
                current_screen = "menu"
                pause_from_screen = None
                dollar = 500
                total_poles = 1
                spot_price = 250
                debt = 2500
                score = 1000
                days = 0
                has_sea_permit = False
                has_boat = False
                fish_inventory = []
                status_message = ""
                player_x = 1290
                player_y = 930
                player_name = ""
                score_saved = False
            elif button_clicked(pause_quit_rect, event):
                # Quit the game
                running = False

        elif current_screen == "end":
            if not score_saved and current_transition is None:
                final_score = calculate_score()

                save_high_score(player_name, final_score)

                score_saved = True
            if button_clicked(play_again_rect, event):
                # Reset game
                score_saved = False
                dollar = 500
                total_poles = 1
                spot_price = 250
                debt = 2500
                score = 1000
                days = 0
                has_sea_permit = False
                has_boat = False
                fish_inventory = []
                status_message = ""
                player_x = 1290
                player_y = 930
                player_name = ""
                final_score = 0
                start_transition("name_input")

            elif button_clicked(quit_rect, event):
                running = False

    # MOVEMENT HANDLING
    if (
        current_screen in ["game", "debtor_map", "shop_map", "casino_map"]
        and current_transition is None
    ):
        keys = pygame.key.get_pressed()
        new_x = player_x
        new_y = player_y
        player_moving = False
        new_direction = player_direction

        current_collision_map = get_current_collision_map()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= player_speed
            player_moving = True
            new_direction = "back"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += player_speed
            player_moving = True
            new_direction = "front"
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= player_speed
            player_moving = True
            new_direction = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += player_speed
            player_moving = True
            new_direction = "right"

        if not check_collision(player_x, new_y, current_collision_map):
            player_y = new_y

        if not check_collision(new_x, player_y, current_collision_map):
            player_x = new_x

        if player_moving:
            player_direction = new_direction

            animation_frame_counter += 1
            if animation_frame_counter >= animation_speed:
                animation_frame_counter = 0
                if current_sprite_state == "idle":
                    current_sprite_state = "step"
                else:
                    current_sprite_state = "idle"
        else:
            current_sprite_state = "idle"
            animation_frame_counter = 0

        # geluid step logica
        now = pygame.time.get_ticks()
        if player_moving and current_screen == "game":
            if now - last_step_time >= step_delay:
                sound1.play()
                last_step_time = now

        if player_moving and not current_screen == "game":
            if now - last_step_time >= step_delay:
                sound2.play()
                last_step_time = now

        check_door_collision_and_fade(player_x, player_y)

    sprite_key = f"{player_direction}_{current_sprite_state}"
    if player_width == player_width_large:
        current_character_img = character_sprites_large[sprite_key]
    else:
        current_character_img = character_sprites_small[sprite_key]

    # MENU FADE-IN LOGIC
    if current_screen == "menu" and menu_fade_active:
        menu_alpha += menu_fade_speed
        if menu_alpha >= 255:
            menu_alpha = 255
            menu_fade_active = False

    # SPLASH SCREEN LOGIC
    if current_screen == "splash":
        if splash_state == "starting":
            splash_starting_timer += 1
            if splash_starting_timer >= splash_starting_duration:
                splash_state = "fade_in"
        elif splash_state == "fade_in":
            splash_alpha += splash_fade_speed
            if splash_alpha >= 255:
                splash_alpha = 255
                splash_state = "hold"
        elif splash_state == "hold":
            splash_hold_timer += 1
            if splash_hold_timer >= splash_hold_duration:
                splash_state = "fade_out"
        elif splash_state == "fade_out":
            splash_alpha -= splash_fade_speed
            if splash_alpha <= 0:
                splash_alpha = 0
                current_screen = "menu"
                menu_alpha = 0
                menu_fade_active = True
                splash_state = "starting"
                splash_starting_timer = 0
                splash_hold_timer = 0

    # RENDERING SECTION
    if current_screen == "splash":
        screen.fill(BLACK)

        splash_surface = splashscreen_image.copy()
        splash_surface.set_alpha(int(splash_alpha))
        screen.blit(splash_surface, (0, 0))

    elif current_screen == "menu":
        screen.blit(background_image, (0, 0))
        screen.blit(start_button_image, start_button_rect.topleft)
        screen.blit(quit_button_image, quit_button_rect.topleft)

        if menu_fade_active:
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill(BLACK)
            fade_surface.set_alpha(255 - int(menu_alpha))
            screen.blit(fade_surface, (0, 0))
    elif current_screen == "name_input":
        screen.blit(background_image, (0, 0))
        box_width = int(screen_width * 0.3)
        box_height = int(screen_height * 0.25)
        box_x = int(screen_width * 0.16)
        box_y = int(screen_height * 0.40)

        pygame.draw.rect(
            screen, BLACK, (box_x, box_y, box_width, box_height), border_radius=10
        )
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            (box_x + 5, box_y + 5, box_width - 10, box_height - 10),
            border_radius=10,
        )

        render_text_block(
            screen,
            "Enter your name:",
            font_size,
            WHITE,
            box_x,
            box_y + 30,
            box_width,
            "center",
        )

        display_name = player_name + (
            "_" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
        )

        render_text_block(
            screen,
            display_name,
            int(font_size * 1.5),
            WHITE,
            box_x,
            box_y + 100,
            box_width,
            "center",
        )

        render_text_block(
            screen,
            "Press ENTER to continue",
            int(default_font_size * 0.8),
            WHITE,
            box_x,
            box_y + 200,
            box_width,
            "center",
        )

    elif current_screen == "description":
        screen.blit(background_image, (0, 0))

        desc_box_width = int(screen_width * 0.8)
        desc_box_height = int(screen_height * 0.8)
        desc_box_x = screen_width // 2 - desc_box_width // 2
        desc_box_y = screen_height // 2 - desc_box_height // 2

        pygame.draw.rect(
            screen,
            BLACK,
            (desc_box_x - 5, desc_box_y - 5, desc_box_width + 10, desc_box_height + 10),
            border_radius=15,
        )

        text_bg = pygame.Surface((desc_box_width, desc_box_height))
        text_bg.set_alpha(220)
        text_bg.fill(DARK_BLUE)
        screen.blit(text_bg, (desc_box_x, desc_box_y))

        max_text_width_box = desc_box_width - 40

        total_story_text = story_text

        render_text_block(
            screen,
            total_story_text,
            story_font_size,
            WHITE,
            desc_box_x + 20,
            desc_box_y + 20,
            max_text_width_box,
            "left",
        )

        continue_button_rect = pygame.Rect(
            screen_width // 2 - continue_button_rect.width // 2,
            desc_box_y + desc_box_height - continue_button_rect.height - 20,
            continue_button_rect.width,
            continue_button_rect.height,
        )

        draw_button(screen, continue_button_rect, "Start Game", WHITE, BLACK)

    elif current_screen == "game":
        if has_boat:
            game_map = game_map_with_boat
        else:
            game_map = game_map_without_boat

        screen.blit(game_map, (0, 0))
        screen.blit(current_character_img, (player_x, player_y))

        stats_text_no_debug = stats_text
        text_width, text_height = calculate_text_dimensions(
            stats_text_no_debug, default_font_size, 500
        )
        stats_bg = pygame.Surface((text_width + 20, text_height + 20))
        stats_bg.set_alpha(180)
        stats_bg.fill(BLACK)
        screen.blit(stats_bg, (x_margin - 10, y_margin - 10))
        render_text_block(
            screen,
            stats_text_no_debug,
            default_font_size,
            WHITE,
            x_margin,
            y_margin,
            text_width,
            "left",
        )

        if status_message:
            status_text_width, status_text_height = calculate_text_dimensions(
                status_message, default_font_size, 500
            )
            status_bg = pygame.Surface(
                (status_text_width + 20, status_text_height + 20)
            )
            status_bg.set_alpha(180)
            status_bg.fill(BLACK)
            screen.blit(status_bg, (x_margin - 10, y_margin + 200))
            render_text_block(
                screen,
                status_message,
                default_font_size,
                WHITE,
                x_margin,
                y_margin + 230,
                status_text_width,
                "left",
            )

        door = check_door_collision(player_x, player_y)
        if door and current_transition is None:
            if door == "fishing_local":
                prompt_text = "Press E to fish locally"
            elif door == "fishing_sea_prompt":
                if has_boat and has_sea_permit:
                    prompt_text = "Press E to fish at SEA!"
                else:
                    prompt_text = "Requires Boat & Sea Permit!"
            elif door == "debtor_map_entry":
                prompt_text = "Entering Debt Collector's Office..."
            elif door == "shop_map_entry":
                prompt_text = "Entering Shop..."
            elif door == "casino_map_entry":
                prompt_text = "Entering Casino..."
            else:
                prompt_text = f"Entering {door.upper()}..."

            prompt_width = int(screen_width * 0.25)
            prompt_height = int(screen_height * 0.08)
            prompt_bg = pygame.Surface((prompt_width, prompt_height))
            prompt_bg.set_alpha(200)
            prompt_bg.fill(BLACK)
            prompt_x = screen_width // 2 - prompt_width // 2
            prompt_y = screen_height - prompt_height - int(screen_height * 0.05)
            screen.blit(prompt_bg, (prompt_x, prompt_y))

            render_text_block(
                screen,
                prompt_text,
                default_font_size,
                WHITE,
                prompt_x + int(prompt_width * 0.05),
                prompt_y + int(prompt_height * 0.15),
                int(prompt_width * 0.9),
                "center",
            )

            if door not in ["fishing_sea_prompt"] and status_message != "":
                status_message = ""

    # DEBTOR MAP RENDERING
    elif current_screen == "debtor_map":
        screen.blit(debtor_map_image, (0, 0))
        screen.blit(current_character_img, (player_x, player_y))

        door = check_door_collision(player_x, player_y)
        if door == "debtor_desk" and current_transition is None:
            prompt_text = "Press E to talk to Debt Collector"

            prompt_width = int(screen_width * 0.25)
            prompt_height = int(screen_height * 0.08)
            prompt_bg = pygame.Surface((prompt_width, prompt_height))
            prompt_bg.set_alpha(200)
            prompt_bg.fill(BLACK)
            prompt_x = screen_width // 2 - prompt_width // 2
            prompt_y = screen_height - prompt_height - int(screen_height * 0.05)
            screen.blit(prompt_bg, (prompt_x, prompt_y))

            render_text_block(
                screen,
                prompt_text,
                default_font_size,
                WHITE,
                prompt_x + int(prompt_width * 0.05),
                prompt_y + int(prompt_height * 0.15),
                int(prompt_width * 0.9),
                "center",
            )

        stats_text_no_debug = stats_text
        text_width, text_height = calculate_text_dimensions(
            stats_text_no_debug, default_font_size, 500
        )
        stats_bg = pygame.Surface((text_width + 20, text_height + 20))
        stats_bg.set_alpha(180)
        stats_bg.fill(BLACK)
        screen.blit(stats_bg, (x_margin - 10, y_margin - 10))
        render_text_block(
            screen,
            stats_text_no_debug,
            default_font_size,
            WHITE,
            x_margin,
            y_margin,
            text_width,
            "left",
        )
        if status_message:
            status_text_width, status_text_height = calculate_text_dimensions(
                status_message, default_font_size, 500
            )
            status_bg = pygame.Surface(
                (status_text_width + 20, status_text_height + 20)
            )
            status_bg.set_alpha(180)
            status_bg.fill(BLACK)
            screen.blit(status_bg, (x_margin - 10, y_margin + 200))
            render_text_block(
                screen,
                status_message,
                default_font_size,
                WHITE,
                x_margin,
                y_margin + 210,
                status_text_width,
                "left",
            )

    # SHOP MAP RENDERING
    elif current_screen == "shop_map":
        screen.blit(shop_map_image, (0, 0))
        screen.blit(current_character_img, (player_x, player_y))

        door = check_door_collision(player_x, player_y)
        if door == "shop_desk" and current_transition is None:
            prompt_text = "Press E to talk to Shopkeeper"

            prompt_width = int(screen_width * 0.25)
            prompt_height = int(screen_height * 0.08)
            prompt_bg = pygame.Surface((prompt_width, prompt_height))
            prompt_bg.set_alpha(200)
            prompt_bg.fill(BLACK)
            prompt_x = screen_width // 2 - prompt_width // 2
            prompt_y = screen_height - prompt_height - int(screen_height * 0.05)
            screen.blit(prompt_bg, (prompt_x, prompt_y))

            render_text_block(
                screen,
                prompt_text,
                default_font_size,
                WHITE,
                prompt_x + int(prompt_width * 0.05),
                prompt_y + int(prompt_height * 0.15),
                int(prompt_width * 0.9),
                "center",
            )

        stats_text_no_debug = stats_text
        text_width, text_height = calculate_text_dimensions(
            stats_text_no_debug, default_font_size, 500
        )
        stats_bg = pygame.Surface((text_width + 20, text_height + 20))
        stats_bg.set_alpha(180)
        stats_bg.fill(BLACK)
        screen.blit(stats_bg, (x_margin - 10, y_margin - 10))
        render_text_block(
            screen,
            stats_text_no_debug,
            default_font_size,
            WHITE,
            x_margin,
            y_margin,
            text_width,
            "left",
        )
        if status_message:
            status_text_width, status_text_height = calculate_text_dimensions(
                status_message, default_font_size, 500
            )
            status_bg = pygame.Surface(
                (status_text_width + 20, status_text_height + 20)
            )
            status_bg.set_alpha(180)
            status_bg.fill(BLACK)
            screen.blit(status_bg, (x_margin - 10, y_margin + 200))
            render_text_block(
                screen,
                status_message,
                default_font_size,
                WHITE,
                x_margin,
                y_margin + 210,
                status_text_width,
                "left",
            )

    # CASINO MAP RENDERING
    elif current_screen == "casino_map":
        screen.blit(casino_map_image, (0, 0))
        screen.blit(current_character_img, (player_x, player_y))

        door = check_door_collision(player_x, player_y)
        if door in ["don_desk", "lucky7_desk"] and current_transition is None:
            if door == "don_desk":
                prompt_text = "Press E to play Double or Nothing"
            elif door == "lucky7_desk":
                prompt_text = "Press E to play Lucky 7"

            prompt_width = int(screen_width * 0.25)
            prompt_height = int(screen_height * 0.08)
            prompt_bg = pygame.Surface((prompt_width, prompt_height))
            prompt_bg.set_alpha(200)
            prompt_bg.fill(BLACK)
            prompt_x = screen_width // 2 - prompt_width // 2
            prompt_y = screen_height - prompt_height - int(screen_height * 0.05)
            screen.blit(prompt_bg, (prompt_x, prompt_y))

            render_text_block(
                screen,
                prompt_text,
                default_font_size,
                WHITE,
                prompt_x + int(prompt_width * 0.05),
                prompt_y + int(prompt_height * 0.15),
                int(prompt_width * 0.9),
                "center",
            )

        stats_text_no_debug = stats_text
        text_width, text_height = calculate_text_dimensions(
            stats_text_no_debug, default_font_size, 500
        )
        stats_bg = pygame.Surface((text_width + 20, text_height + 20))
        stats_bg.set_alpha(180)
        stats_bg.fill(BLACK)
        screen.blit(stats_bg, (x_margin - 10, y_margin - 10))
        render_text_block(
            screen,
            stats_text_no_debug,
            default_font_size,
            WHITE,
            x_margin,
            y_margin,
            text_width,
            "left",
        )
        if status_message:
            status_text_width, status_text_height = calculate_text_dimensions(
                status_message, default_font_size, 500
            )
            status_bg = pygame.Surface(
                (status_text_width + 20, status_text_height + 20)
            )
            status_bg.set_alpha(180)
            status_bg.fill(BLACK)
            screen.blit(status_bg, (x_margin - 10, y_margin + 200))
            render_text_block(
                screen,
                status_message,
                default_font_size,
                WHITE,
                x_margin,
                y_margin + 210,
                status_text_width,
                "left",
            )

    # LOCAL FISHING RESULTS
    elif current_screen == "fishing_local_results":
        if has_boat:
            game_map = game_map_with_boat
        else:
            game_map = game_map_without_boat
        screen.blit(game_map, (0, 0))

        screen.blit(current_character_img, fishing_return_pos)

        full_text_local = fishing_result_text + "\nPress ESC to return to map."

        overlay_content_width = int(screen_width * 0.45) - 40

        text_w, text_h = calculate_text_dimensions(
            full_text_local, default_font_size, overlay_content_width
        )

        padding = 40

        min_overlay_height = int(screen_height * 0.3)

        overlay_width = int(screen_width * 0.45)
        overlay_height = max(min_overlay_height, text_h + padding)

        overlay_x = screen_width // 2 - overlay_width // 2
        overlay_y = screen_height // 2 - overlay_height // 2

        max_height_limit = int(screen_height * 0.9)
        if overlay_height > max_height_limit:
            overlay_height = max_height_limit
            overlay_y = (screen_height - overlay_height) // 2

        catch_bg = pygame.Surface((overlay_width, overlay_height))
        catch_bg.set_alpha(220)
        catch_bg.fill(DARK_BLUE)
        pygame.draw.rect(
            screen,
            BLACK,
            (overlay_x - 5, overlay_y - 5, overlay_width + 10, overlay_height + 10),
            border_radius=10,
        )
        screen.blit(catch_bg, (overlay_x, overlay_y))

        render_text_block(
            screen,
            full_text_local,
            default_font_size,
            WHITE,
            overlay_x + 20,
            overlay_y + 20,
            overlay_content_width,
            "left",
        )

    # SEA FISHING RESULTS
    elif current_screen == "sea_fishing_cutscene":
        screen.blit(sea_fishing_image, (0, 0))

        SIDE_PANEL_WIDTH = int(screen_width * 0.35)
        PANEL_HEIGHT = int(screen_height * 0.85)

        panel_x = x_margin
        panel_y = y_margin

        left_panel_rect = pygame.Rect(panel_x, panel_y, SIDE_PANEL_WIDTH, PANEL_HEIGHT)

        catch_bg = pygame.Surface((left_panel_rect.width, left_panel_rect.height))
        catch_bg.set_alpha(200)
        catch_bg.fill(DARK_BLUE)
        screen.blit(catch_bg, left_panel_rect.topleft)
        pygame.draw.rect(screen, BLACK, left_panel_rect, 5, border_radius=10)

        full_text = fishing_result_text + "\n\nPress ESC to return to the map."

        max_content_width = left_panel_rect.width - 30

        render_text_block(
            screen,
            full_text,
            inv_font_size,
            WHITE,
            left_panel_rect.x + 15,
            left_panel_rect.y + 15,
            max_content_width,
            "left",
        )

    elif current_screen == "casino_don_game":
        screen.blit(casino_map_image, (0, 0))
        input_area_width = int(screen_width * 0.35)
        input_area_height = int(screen_height * 0.55)
        input_area = pygame.Rect(
            screen_width // 2 - input_area_width // 2,
            screen_height // 2 - input_area_height // 2,
            input_area_width,
            input_area_height,
        )
        pygame.draw.rect(screen, BLACK, input_area, border_radius=10)
        input_area_inner = pygame.Rect(
            input_area.x + 5,
            input_area.y + 5,
            input_area_width - 10,
            input_area_height - 10,
        )
        pygame.draw.rect(screen, DARK_BLUE, input_area_inner, border_radius=10)

        content_width = int(input_area_width * 0.8)
        content_x = input_area.x + int(input_area_width * 0.1)

        render_text_block(
            screen,
            "Double or Nothing",
            font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.05),
            content_width,
            "center",
        )
        render_text_block(
            screen,
            "Enter your bet:",
            default_font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.20),
            content_width,
            "center",
        )

        button_width = int(input_area_width * 0.5)
        button_height = int(input_area_height * 0.12)
        draw_button(
            screen,
            pygame.Rect(
                screen_width // 2 - button_width // 2,
                input_area.y + int(input_area_height * 0.35),
                button_width,
                button_height,
            ),
            don_bet_input_text if don_bet_input_text else "...",
            WHITE,
            BLUE,
        )
        render_text_block(
            screen,
            f"Balance: ${round(dollar, 2):,.2f}",
            default_font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.60),
            content_width,
            "center",
        )
        render_text_block(
            screen,
            status_message,
            default_font_size,
            GREEN,
            content_x,
            input_area.y + int(input_area_height * 0.75),
            content_width,
            "center",
        )

    elif current_screen == "casino_lucky7_game":
        screen.blit(casino_map_image, (0, 0))
        input_area_width = int(screen_width * 0.35)
        input_area_height = int(screen_height * 0.55)
        input_area = pygame.Rect(
            screen_width // 2 - input_area_width // 2,
            screen_height // 2 - input_area_height // 2,
            input_area_width,
            input_area_height,
        )
        pygame.draw.rect(screen, BLACK, input_area, border_radius=10)
        input_area_inner = pygame.Rect(
            input_area.x + 5,
            input_area.y + 5,
            input_area_width - 10,
            input_area_height - 10,
        )
        pygame.draw.rect(screen, DARK_BLUE, input_area_inner, border_radius=10)

        content_width = int(input_area_width * 0.8)
        content_x = input_area.x + int(input_area_width * 0.1)

        render_text_block(
            screen,
            "Lucky 7",
            font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.05),
            content_width,
            "center",
        )
        render_text_block(
            screen,
            "Enter your bet:",
            default_font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.20),
            content_width,
            "center",
        )

        button_width = int(input_area_width * 0.5)
        button_height = int(input_area_height * 0.12)
        draw_button(
            screen,
            pygame.Rect(
                screen_width // 2 - button_width // 2,
                input_area.y + int(input_area_height * 0.30),
                button_width,
                button_height,
            ),
            lucky7_bet_input_text if lucky7_bet_input_text else "...",
            WHITE,
            BLUE,
        )
        render_text_block(
            screen,
            f"Balance: ${round(dollar, 2):,.2f}",
            default_font_size,
            WHITE,
            content_x,
            input_area.y + int(input_area_height * 0.50),
            content_width,
            "center",
        )
        render_text_block(
            screen,
            status_message,
            default_font_size,
            GREEN,
            content_x,
            input_area.y + int(input_area_height * 0.65),
            content_width,
            "center",
        )

    elif current_screen == "shop":
        screen.blit(shop_map_image, (0, 0))
        menu_area_width = int(screen_width * 0.50)
        menu_area_height = int(screen_height * 0.9)
        menu_area = pygame.Rect(
            screen_width - menu_area_width - x_margin,
            screen_height * 0.05,
            menu_area_width,
            menu_area_height,
        )
        pygame.draw.rect(screen, BLACK, menu_area, border_radius=10)
        menu_area_inner = pygame.Rect(
            menu_area.x + 5,
            menu_area.y + 5,
            menu_area.width - 10,
            menu_area.height - 10,
        )
        pygame.draw.rect(screen, DARK_BLUE, menu_area_inner, border_radius=10)

        render_text_block(
            screen,
            "The Fisherman's Market",
            font_size,
            WHITE,
            menu_area.x,
            menu_area.y + 20,
            menu_area.width,
            "center",
        )

        render_text_block(
            screen,
            status_message,
            default_font_size,
            GREEN,
            menu_area.x + 20,
            menu_area.y + 100,
            menu_area.width - 40,
            "center",
        )

        stats_panel_width = int(screen_width * 0.4)
        stats_panel_height = int(screen_height * 0.85)
        stats_panel = pygame.Rect(
            x_margin, y_margin, stats_panel_width, stats_panel_height
        )

        pygame.draw.rect(screen, BLACK, stats_panel, border_radius=10)
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            (
                stats_panel.x + 5,
                stats_panel.y + 5,
                stats_panel.width - 10,
                stats_panel.height - 10,
            ),
            border_radius=10,
        )

        inventory_text = print_inventory()

        render_text_block(
            screen,
            inventory_text,
            inv_font_size,
            WHITE,
            stats_panel.x + 20,
            stats_panel.y + 20,
            stats_panel.width - 40,
            "left",
        )

        button_area_x = menu_area_inner.x + (menu_area_inner.width * 0.1)
        button_area_width = int(menu_area_inner.width * 0.8)

        draw_button(
            screen,
            shop_sellfish_rect,
            f"Sell All Fish (${calculate_total_value(fish_inventory):,.2f})",
            WHITE,
            BLACK,
        )
        draw_button(
            screen,
            shop_buypoles_rect,
            f"Buy Fishing Pole (${spot_price:,.2f})" if total_poles < max_poles else "Buy Fishing Pole (MAX)",
            WHITE,
            BLACK,
        )
        draw_button(
            screen,
            shop_buyboat_rect,
            f"Buy Boat ({'$500.00' if not has_boat else 'Owned'})",
            WHITE,
            BLACK,
        )
        draw_button(
            screen,
            shop_buyperm_rect,
            f"Buy Sea Permit ({'$100.00' if not has_sea_permit else 'Owned'})",
            WHITE,
            BLACK,
        )

        render_text_block(
            screen,
            "Press ESC to exit shop",
            int(default_font_size * 0.8),
            WHITE,
            menu_area.x,
            menu_area.y + menu_area.height - 50,
            menu_area.width,
            "center",
        )

    elif current_screen == "debtor":
        screen.blit(debtor_map_image, (0, 0))

        debt_area_width = int(screen_width * 0.35)
        debt_area_height = int(screen_height * 0.65)
        debt_area = pygame.Rect(
            screen_width // 2 - debt_area_width // 2,
            screen_height // 2 - debt_area_height // 2,
            debt_area_width,
            debt_area_height,
        )
        pygame.draw.rect(screen, BLACK, debt_area, border_radius=10)
        debt_area_inner = pygame.Rect(
            debt_area.x + 5,
            debt_area.y + 5,
            debt_area_width - 10,
            debt_area_height - 10,
        )
        pygame.draw.rect(screen, DARK_BLUE, debt_area_inner, border_radius=10)

        debt_status = f"Your current debt is: ${debt:,.2f}\nYour current money is: ${round(dollar, 2):,.2f}"

        dialog_max_width = int(debt_area_width * 0.9)
        dialog_x_start = debt_area.x + int(debt_area_width * 0.05)

        render_text_block(
            screen,
            "Debt Collector's Office",
            45,
            WHITE,
            dialog_x_start,
            debt_area.y + int(debt_area_height * 0.05),
            dialog_max_width,
            "center",
        )

        render_text_block(
            screen,
            debt_status,
            default_font_size,
            WHITE,
            dialog_x_start,
            debt_area.y + int(debt_area_height * 0.25),
            dialog_max_width,
            "center",
        )

        render_text_block(
            screen,
            status_message,
            default_font_size,
            GREEN,
            dialog_x_start,
            debt_area.y + int(debt_area_height * 0.45),
            dialog_max_width,
            "center",
        )

        draw_button(screen, end_button_rect, f"Pay debt (${debt:,.2f})", WHITE, BLACK)

    elif current_screen == "pause_menu":
        if pause_from_screen == "game":
            if has_boat:
                game_map = game_map_with_boat
            else:
                game_map = game_map_without_boat
            screen.blit(game_map, (0, 0))
            screen.blit(current_character_img, (player_x, player_y))
        elif pause_from_screen == "debtor_map":
            screen.blit(debtor_map_image, (0, 0))
            screen.blit(current_character_img, (player_x, player_y))
        elif pause_from_screen == "shop_map":
            screen.blit(shop_map_image, (0, 0))
            screen.blit(current_character_img, (player_x, player_y))
        elif pause_from_screen == "casino_map":
            screen.blit(casino_map_image, (0, 0))
            screen.blit(current_character_img, (player_x, player_y))

        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        menu_width = int(screen_width * 0.4)
        menu_height = int(screen_height * 0.7)
        menu_x = screen_width // 2 - menu_width // 2
        menu_y = screen_height // 2 - menu_height // 2

        pygame.draw.rect(
            screen, BLACK, (menu_x, menu_y, menu_width, menu_height), border_radius=10
        )
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            (menu_x + 5, menu_y + 5, menu_width - 10, menu_height - 10),
            border_radius=10,
        )

        render_text_block(
            screen,
            "PAUSED",
            int(font_size * 1.5),
            WHITE,
            menu_x,
            menu_y + 40,
            menu_width,
            "center",
        )

        screen.blit(resume_button_image, pause_resume_rect.topleft)
        screen.blit(mainmenu_button_image, pause_mainmenu_rect.topleft)
        screen.blit(quitgame_button_image, pause_quit_rect.topleft)

    elif current_screen == "end":
        screen.blit(end_image, (0, 0))

        main_panel_width = int(screen_width * 0.55)
        main_panel_height = int(screen_height * 0.8)
        main_panel_x = int(screen_width * 0.05)
        main_panel_y = int(screen_height * 0.1)
        main_panel = pygame.Rect(
            main_panel_x, main_panel_y, main_panel_width, main_panel_height
        )

        pygame.draw.rect(screen, BLACK, main_panel, border_radius=10)
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            (
                main_panel.x + 5,
                main_panel.y + 5,
                main_panel.width - 10,
                main_panel.height - 10,
            ),
            border_radius=10,
        )

        final_rank = check_rank(final_score)

        end_text_title = f"**DEBT PAID - {player_name.upper()}**\n\n"

        end_text_body = (
            f"After {days} relentless days of fishing and gambling, "
            f"Bob has finally paid his debt of $2,500. "
            f"He is now a free man.\n\n"
            f"Your Final Score:\n"
            f"**{final_score:,}**\n\n"
            f"Your Final Rank:\n"
            f"**{final_rank.upper()}**\n\n"
            f"Net Worth after payment: **${round(dollar, 2):,.2f}**"
        )

        render_text_block(
            screen,
            end_text_title,
            int(font_size * 1.2),
            WHITE,
            main_panel.x + 20,
            main_panel.y + 20,
            main_panel.width - 40,
            "center",
        )

        render_text_block(
            screen,
            end_text_body,
            default_font_size,
            WHITE,
            main_panel.x + 40,
            main_panel.y + 120,
            main_panel.width - 80,
            "left",
        )

        hs_panel_width = int(screen_width * 0.3)
        hs_panel_height = int(screen_height * 0.5)
        hs_panel_x = int(screen_width * 0.65)
        hs_panel_y = int(screen_height * 0.1)
        hs_panel = pygame.Rect(hs_panel_x, hs_panel_y, hs_panel_width, hs_panel_height)

        pygame.draw.rect(screen, BLACK, hs_panel, border_radius=10)
        pygame.draw.rect(
            screen,
            DARK_BLUE,
            (
                hs_panel.x + 5,
                hs_panel.y + 5,
                hs_panel.width - 10,
                hs_panel.height - 10,
            ),
            border_radius=10,
        )

        hs_text = get_highscore_string()

        render_text_block(
            screen,
            hs_text,
            default_font_size,
            WHITE,
            hs_panel.x + 20,
            hs_panel.y + 20,
            hs_panel.width - 40,
            "left",
        )

        button_area_y = hs_panel.y + hs_panel.height + 30

        play_again_rect.x = (
            hs_panel_x + hs_panel.width // 2 - play_again_rect.width // 2
        )
        play_again_rect.y = button_area_y

        quit_rect.x = hs_panel_x + hs_panel.width // 2 - quit_rect.width // 2
        quit_rect.y = button_area_y + play_again_rect.height + 20

        draw_button(screen, play_again_rect, "Play Again", WHITE, BLACK)
        draw_button(screen, quit_rect, "Quit", WHITE, BLACK)

    if current_transition == "fade_out":
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255

            current_screen = fade_target_screen

            if current_screen in [
                "debtor_map",
                "shop_map",
                "casino_map",
                "shop",
                "debtor",
                "casino_don_game",
                "casino_lucky7_game",
            ]:
                player_width = player_width_large
                player_height = player_height_large
            else:
                player_width = player_width_small
                player_height = player_height_small

            if (
                current_screen in ["game", "debtor_map", "shop_map", "casino_map"]
                and fade_return_pos is not None
            ):
                player_x, player_y = fade_return_pos

            current_transition = "fade_in"

            if current_screen in ["fishing_local_results", "sea_fishing_cutscene"]:
                fishing_result_text = generate_fishing_results()
            elif current_screen == "debtor_map":
                status_message = "I've been expecting you, Bob. \nPlease, take a seat."
            elif current_screen == "shop_map":
                status_message = (
                    "Welcome to the shop, fisherman! \nWhat can I get for you?"
                )
            elif current_screen == "casino_map":
                status_message = "Feeling lucky, Bob? \nPick a table."
            else:
                status_message = ""

    elif current_transition == "fade_in":
        fade_alpha -= fade_speed
        if fade_alpha <= 0:
            fade_alpha = 0
            current_transition = None

    if current_transition is not None:
        fade_surface = pygame.Surface((screen_width, screen_height))
        fade_surface.fill(BLACK)
        fade_surface.set_alpha(min(255, max(0, int(fade_alpha))))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
