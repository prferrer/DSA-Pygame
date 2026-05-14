import pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
import sys
import random
import math
import os

from menu import run_menu
from config import *
import map_data as md
from players import Player
from guns import GUN_TYPES, GunSystem, ArmorPickup, shoot, scale_gun_images, load_gun_sounds, play_explosion_sound
from mechanics import update_bullets, try_melee

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# ── Screen initialisation ─────────────────────────────────────────────────────
info   = pygame.display.Info()
WIDTH  = info.current_w
HEIGHT = info.current_h

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("PacPew - 2D Arena Shooter")
clock  = pygame.time.Clock()

# ── Menu ──────────────────────────────────────────────────────────────────────
menu_result = run_menu(screen)
if menu_result is None:
    pygame.quit()
    sys.exit()

p1_name, p1_color, p1_hat, p1_glasses, p1_pet, p2_name, p2_color, p2_hat, p2_glasses, p2_pet, selected_map_name = menu_result 

md.init_map(selected_map_name)

scale_gun_images(md.map_data.TILE_SIZE)
load_gun_sounds()

HUD_FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 72)
MED_FONT = pygame.font.SysFont(None, 40)

# ── Players ───────────────────────────────────────────────────────────────────
p1_spawn = md.get_valid_spawn(True)
p2_spawn = md.get_valid_spawn(False)
player1  = Player(p1_spawn[0], p1_spawn[1], p1_color)
player2  = Player(p2_spawn[0], p2_spawn[1], p2_color)

# Initialize armor HP tracking for new armor system
# Each armor unit has 33.33 HP
player1.armor_hp = 0
player2.armor_hp = 0

# ── Dual guns ─────────────────────────────────────────────────────────────────
gun1 = GunSystem()
gun2 = GunSystem()
gun1.spawn(md.map_data)
gun2.spawn(md.map_data, occupied_positions=[gun1.pos] if gun1.pos else [])

GUN_RESPAWN_TIME     = 1000
last_gun1_spawn_time = pygame.time.get_ticks()
last_gun2_spawn_time = pygame.time.get_ticks()

bullets = []

# ── Armor pickup ──────────────────────────────────────────────────────────────
armor_pickup          = ArmorPickup()
last_armor_spawn_time = pygame.time.get_ticks()
armor_pickup.spawn(md.map_data, pygame.time.get_ticks())

# ── Melee animations ──────────────────────────────────────────────────────────
# List of dicts: {cx, cy, start, duration, frame}
active_animations = []

# ── Explosion animations ───────────────────────────────────────────────────────
# List of dicts: {x, y, start, duration, frame, radius}
explosion_animations = []

# ── Game state ────────────────────────────────────────────────────────────────
start_time       = pygame.time.get_ticks()
last_shrink_time = start_time
game_state       = "playing"
winner_text      = ""

# ─────────────────────────────────────────────────────────────────────────────
# ASSET LOADING
# ─────────────────────────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))

def _load_img(path, fallback_color=(255, 0, 0), size=(24, 24)):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        s = pygame.Surface(size, pygame.SRCALPHA)
        s.fill(fallback_color)
        return s

HEART_IMG    = pygame.transform.scale(_load_img("assets/health/hearts.png"),   (24, 24))
AR_HEART_IMG = pygame.transform.scale(_load_img("assets/health/ArHeart.png"),  (24, 24))

# ── GLASSES ────────────────────────────────────────────────────
GLASSES_IMAGES = {}
def load_glasses_images():
    hat_dir = os.path.join(_HERE, "assets", "glasses")
    for glasses_name in ["None", "Round", "Sunglasses", "Red", "Black", "Pink"]:
        path = os.path.join(hat_dir, f"{glasses_name}.png")
        GLASSES_IMAGES[glasses_name] = (
            pygame.image.load(path).convert_alpha() if os.path.isfile(path) else None
        )
load_glasses_images()

# ── PET ────────────────────────────────────────────────────────
PET_IMAGES = {}

def load_pet_images():
    pet_dir = os.path.join(_HERE, "assets", "pets")

    for pet_name in ["Dragon", "Panda", "Rabbit"]:
        path = os.path.join(pet_dir, f"{pet_name}.png")

        if os.path.isfile(path):
            PET_IMAGES[pet_name] = pygame.image.load(path).convert_alpha()
        else:
            PET_IMAGES[pet_name] = None

load_pet_images()

try:
    SPEED_IMG = pygame.image.load("assets/powerups/speedboost.png").convert_alpha()
except Exception:
    SPEED_IMG = None

try:
    SLOW_IMG = pygame.image.load("assets/powerups/slowdown.png").convert_alpha()
except Exception:
    SLOW_IMG = None

# Pickup token on the map uses armor.png; HUD heart replacement uses ArHeart.png
try:
    ARMOR_ICON = pygame.image.load("assets/health/armor.png").convert_alpha()
except Exception:
    ARMOR_ICON = None
    
def _load_sound(path):
    if os.path.isfile(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None

SFX_SPEED = _load_sound("assets/SE/speed.mp3")
SFX_SLOW  = _load_sound("assets/SE/slow.mp3")
SFX_ARMOR = _load_sound("assets/SE/armor.mp3")
SFX_TP = _load_sound("assets/SE/teleport.mp3")
SFX_MELEE = _load_sound("assets/SE/melee.mp3")
SFX_PICKUP = _load_sound("assets/SE/pickup.mp3")

# Melee hit-spark frames Hit1.png … Hit5.png
MELEE_FRAMES = []
for _i in range(1, 6):
    _path = os.path.join(_HERE, "assets", "melee", f"Hit{_i}.png")
    try:
        MELEE_FRAMES.append(pygame.image.load(_path).convert_alpha())
    except Exception:
        _fb = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(_fb, (255, 200, 0, 200), (24, 24), 24 - _i * 3)
        MELEE_FRAMES.append(_fb)

# Explosion frames boom1.png … boom5.png
BOOM_FRAMES = []
for _i in range(1, 6):
    _path = os.path.join(_HERE, f"assets/boom/boom{_i}.png")
    try:
        BOOM_FRAMES.append(pygame.image.load(_path).convert_alpha())
    except Exception:
        # Fallback: simple orange expanding circle
        _fb = pygame.Surface((128, 128), pygame.SRCALPHA)
        _r  = 10 + _i * 18
        pygame.draw.circle(_fb, (255, 140 - _i * 20, 0, max(30, 220 - _i * 40)), (64, 64), _r)
        BOOM_FRAMES.append(_fb)

# Map backgrounds
MAP_BACKGROUNDS = {
    "Greenwood Village": os.path.join(_HERE, "assets", "maps", "Greenwood Village.png"),
    "Meadow Crossing":   os.path.join(_HERE, "assets", "maps", "Meadow Crossing.png"),
    "The Underkeep":     os.path.join(_HERE, "assets", "maps", "The Underkeep.png"),
}
MAP_FALLBACK_COLORS = {
    "Greenwood Village": (34,  139,  34),
    "Meadow Crossing":   (144, 238, 144),
    "The Underkeep":     (40,   40,  60),
}

def _load_background(map_name):
    path = MAP_BACKGROUNDS.get(map_name)
    if path and os.path.isfile(path):
        try:
            return pygame.image.load(path).convert(), None
        except Exception:
            pass
    return None, MAP_FALLBACK_COLORS.get(map_name, (30, 30, 30))

BACKGROUND_IMG, BACKGROUND_COLOR = _load_background(selected_map_name)
scaled_bg       = None
current_bg_size = (0, 0)

# Hat images
HAT_IMAGES = {}
def load_hat_images():
    hat_dir = os.path.join(_HERE, "assets", "hats")
    for hat_name in ["None", "Crown", "Top", "Cowboy", "Duck", "Party", "Pirate"]:
        path = os.path.join(hat_dir, f"{hat_name}.png")
        HAT_IMAGES[hat_name] = (
            pygame.image.load(path).convert_alpha() if os.path.isfile(path) else None
        )
load_hat_images()

# ── Speed / slow powerup state ────────────────────────────────────────────────
green_powerup      = None
blue_powerup       = None
green_spawn_time   = pygame.time.get_ticks() + random.randint(5000, 15000)
blue_spawn_time    = pygame.time.get_ticks() + random.randint(5000, 15000)
green_despawn_time = None
blue_despawn_time  = None
speed_boost_p1     = None
speed_boost_p2     = None
slow_p1            = None
slow_p2            = None

TELEPORT_COOLDOWN = 3000  # ms before same player can teleport again
player1_last_teleport = 0
player2_last_teleport = 0

SPEED_BOOST_DURATION = 2000
SLOW_DURATION        = 2000

def get_valid_powerup_spawn():
    while True:
        x = random.randint(0, md.MAP_COLS - 1)
        y = random.randint(0, md.MAP_ROWS - 1)
        if md.map_grid[y][x] == 0:
            return [x, y]

# ── Layout recalculation ──────────────────────────────────────────────────────
def recalculate_layout():
    ts = min(WIDTH // md.MAP_COLS, HEIGHT // md.MAP_ROWS)
    md.map_data.TILE_SIZE = ts
    md.map_data.offset_x  = (WIDTH  - md.MAP_COLS * ts) // 2
    md.map_data.offset_y  = (HEIGHT - md.MAP_ROWS * ts) // 2
    scale_gun_images(ts)

recalculate_layout()

# ─────────────────────────────────────────────────────────────────────────────
# DRAWING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def draw_health_bar(surface, player, x, y, bar_width=200, bar_height=20):
    """
    Draws health bar with armor HP display.
    Each armor unit has 33.33 HP, max 3 armor (100 total armor HP).
    Shows: HP bar (green) + Armor HP bar (blue with depletion) + Text showing armor HP
    """

    # Constants for health
    MAX_HP = 100
    MAX_ARMOR_HP = 100  # 3 armor units * 33.33 HP each
    health_ratio = max(0, player.hp / MAX_HP)
    
    # 1. Draw Background (Empty Bar)
    bg_rect = pygame.Rect(x, y, bar_width, bar_height)
    pygame.draw.rect(surface, (60, 60, 60), bg_rect) # Dark Gray
    
    # 2. Draw HP (Green)
    hp_rect = pygame.Rect(x, y, int(bar_width * health_ratio), bar_height)
    pygame.draw.rect(surface, (50, 200, 50), hp_rect) # Green
    
    # 3. Draw Armor HP (Blue with depletion visible)
    if player.armor_hp > 0:
        # Calculate armor HP ratio
        armor_hp_ratio = max(0, min(1, player.armor_hp / MAX_ARMOR_HP))
        
        # Draw armor HP as a blue overlay that depletes
        armor_width = int(bar_width * armor_hp_ratio)
        armor_rect = pygame.Rect(x, y, armor_width, bar_height)
        
        # Use a semi-transparent blue for armor
        armor_surface = pygame.Surface((armor_width, bar_height), pygame.SRCALPHA)
        armor_surface.fill((50, 150, 255, 180))  # Blue with alpha
        surface.blit(armor_surface, (x, y))
        
        # Draw segment dividers to show the 3 armor units
        segment_width = bar_width // 3
        for i in range(1, 3):
            divider_x = x + (i * segment_width)
            pygame.draw.line(surface, (200, 200, 255), 
                           (divider_x, y), (divider_x, y + bar_height), 2)
            
    # 4. Draw Border
    pygame.draw.rect(surface, (255, 255, 255), bg_rect, 2) # White Border
    
    # 5. Text showing HP and Armor HP
    if player.armor_hp > 0:
        hp_text = HUD_FONT.render(f"{int(player.hp)} HP | {int(player.armor_hp)} AR", True, (255, 255, 255))
    else:
        hp_text = HUD_FONT.render(f"{int(player.hp)} HP", True, (255, 255, 255))
    surface.blit(hp_text, (x + bar_width + 10, y - 5))


def draw_held_gun(surface, gun, player, map_data_module):
    if gun.owner != player:
        return
    img    = GUN_TYPES[gun.type]["equipped_image"]
    dx, dy = player.dir
    if   (dx, dy) == (1,  0): rotated = img
    elif (dx, dy) == (-1, 0): rotated = pygame.transform.flip(img, True, False)
    elif (dx, dy) == (0, -1): rotated = pygame.transform.rotate(img, 90)
    elif (dx, dy) == (0,  1): rotated = pygame.transform.rotate(img, 270)
    else:                      rotated = img
    cx = map_data_module.offset_x + player.pos[0] * map_data_module.TILE_SIZE
    cy = map_data_module.offset_y + player.pos[1] * map_data_module.TILE_SIZE
    ox = dx * map_data_module.TILE_SIZE // 2
    oy = dy * map_data_module.TILE_SIZE // 2
    surface.blit(rotated, (
        cx + ox + (map_data_module.TILE_SIZE - rotated.get_width())  // 2,
        cy + oy + (map_data_module.TILE_SIZE - rotated.get_height()) // 2,
    ))


def draw_weapon_ui(surface, g1, g2, player, x, y):
    label = None
    if g1.owner == player:
        label = f"{g1.type.upper()} | Ammo: {g1.ammo}"
    elif g2.owner == player:
        label = f"{g2.type.upper()} | Ammo: {g2.ammo}"
    else:
        label = "No Weapon  [Melee ready]"
    surface.blit(HUD_FONT.render(label, True, (255, 255, 255)), (x, y))


def draw_win_screen(surface, winner_text):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    win_surf = BIG_FONT.render(f"{winner_text} Wins!", True, (255, 215, 0))
    sub_surf = MED_FONT.render("Press R to play again  |  ESC to quit", True, (200, 200, 200))
    surface.blit(win_surf, win_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    surface.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


def draw_powerups(surface):
    ts = md.map_data.TILE_SIZE
    if green_powerup:
        x = md.map_data.offset_x + green_powerup[0] * ts
        y = md.map_data.offset_y + green_powerup[1] * ts
        if SPEED_IMG:
            surface.blit(pygame.transform.scale(SPEED_IMG, (ts, ts)), (x, y))
        else:
            pygame.draw.circle(surface, (0, 255, 0), (x + ts // 2, y + ts // 2), ts // 2)
    if blue_powerup:
        x = md.map_data.offset_x + blue_powerup[0] * ts
        y = md.map_data.offset_y + blue_powerup[1] * ts
        if SLOW_IMG:
            surface.blit(pygame.transform.scale(SLOW_IMG, (ts, ts)), (x, y))
        else:
            pygame.draw.circle(surface, (0, 0, 255), (x + ts // 2, y + ts // 2), ts // 2)


def draw_armor_pickup(surface):
    if not armor_pickup.pos:
        return
    ts = md.map_data.TILE_SIZE
    x  = md.map_data.offset_x + armor_pickup.pos[0] * ts
    y  = md.map_data.offset_y + armor_pickup.pos[1] * ts
    if ARMOR_ICON:
        surface.blit(pygame.transform.scale(ARMOR_ICON, (ts, ts)), (x, y))
    else:
        pygame.draw.circle(surface, (180, 180, 255), (x + ts // 2, y + ts // 2), ts // 2)


def draw_melee_animations(surface, current_time):
    """
    Draw each frame offset from the attacker's current facing direction.
    This keeps the animation glued to the player as they move.
    """
    for anim in active_animations[:]:
        elapsed  = current_time - anim["start"]
        progress = elapsed / anim["duration"]
        if progress >= 1.0:
            active_animations.remove(anim)
            continue

        attacker  = anim["attacker"]
        ts        = md.map_data.TILE_SIZE
        frame_idx = min(int(progress * len(MELEE_FRAMES)), len(MELEE_FRAMES) - 1)
        frame     = MELEE_FRAMES[frame_idx]
        scaled    = pygame.transform.scale(frame, (ts, ts))

        # Always recompute from the attacker's live position + facing direction
        draw_x = (md.map_data.offset_x
                  + (attacker.pos[0] + attacker.dir[0]) * ts)
        draw_y = (md.map_data.offset_y
                  + (attacker.pos[1] + attacker.dir[1]) * ts)
        surface.blit(scaled, (draw_x, draw_y))


def draw_bullets(surface, bullets):
    for b in bullets:
        if b.get("is_explosive", False):
            # Draw rocket as a glowing orange circle
            pygame.draw.circle(surface, (255, 140, 0), (int(b["x"]), int(b["y"])), 6)
            pygame.draw.circle(surface, (255, 220, 100), (int(b["x"]), int(b["y"])), 3)
        else:
            pygame.draw.rect(surface, (255, 255, 0), (int(b["x"]), int(b["y"]), 8, 8))


def draw_explosion_animations(surface, current_time):
    """
    Draw boom sprite frames centred on the explosion impact point.
    Frames advance linearly over the animation duration.
    """
    for anim in explosion_animations[:]:
        elapsed  = current_time - anim["start"]
        progress = elapsed / anim["duration"]
        if progress >= 1.0:
            explosion_animations.remove(anim)
            continue

        frame_idx = min(int(progress * len(BOOM_FRAMES)), len(BOOM_FRAMES) - 1)
        frame     = BOOM_FRAMES[frame_idx]

        # Scale the frame to match the explosion radius
        size   = max(32, int(anim["radius"] * 2.2))
        scaled = pygame.transform.scale(frame, (size, size))

        # Fade out in the final third
        if progress > 0.65:
            alpha = int(255 * (1.0 - (progress - 0.65) / 0.35))
            scaled.set_alpha(alpha)

        cx = int(anim["x"])
        cy = int(anim["y"])
        surface.blit(scaled, (cx - size // 2, cy - size // 2))


def draw_player_hat(surface, player, hat_name):
    if hat_name == "None":
        return
    hat_img = HAT_IMAGES.get(hat_name)
    if hat_img is None:
        return
    ts    = md.map_data.TILE_SIZE
    hat_w = int(ts * 1.2)
    ratio = hat_w / hat_img.get_width()
    hat_h = int(hat_img.get_height() * ratio)
    scaled = pygame.transform.smoothscale(hat_img, (hat_w, hat_h))
    px = md.map_data.offset_x + player.pos[0] * ts
    py = md.map_data.offset_y + player.pos[1] * ts
    surface.blit(scaled, (px + (ts - hat_w) // 2, py - int(hat_h * 0.80)))
    
def draw_player_glasses(surface, player, glasses_name):
    if glasses_name == "None":
        return
    img = GLASSES_IMAGES.get(glasses_name)
    if img is None:
        return
    ts = md.map_data.TILE_SIZE
    px = md.map_data.offset_x + player.pos[0] * ts
    py = md.map_data.offset_y + player.pos[1] * ts
    g_w = int(ts * 1.1)
    ratio = g_w / img.get_width()
    g_h = int(img.get_height() * ratio)
    scaled = pygame.transform.smoothscale(img, (g_w, g_h))
    if glasses_name == "Red":
        surface.blit(scaled, (px + (ts - g_w)//2, py + ts//3 - 4))
    elif glasses_name == "Round":
        surface.blit(scaled, (px + (ts - g_w)//2, py + ts//3 - 2))
    else:
        surface.blit(scaled, (px + (ts - g_w)//2, py + ts//3))
        
def draw_pet(surface, player, pet_name):
    if pet_name == "None":
        return

    pet_img = PET_IMAGES.get(pet_name)

    if pet_img is None:
        return

    ts = md.map_data.TILE_SIZE

    # Pet smaller than player
    pet_size = int(ts * 0.65)

    pet_scaled = pygame.transform.smoothscale(
        pet_img,
        (pet_size, pet_size)
    )

    # Player position
    px = md.map_data.offset_x + player.pos[0] * ts
    py = md.map_data.offset_y + player.pos[1] * ts

    dx, dy = player.dir

    # Distance from player
    offset = int(ts * 0.9)

    # Pet switches side depending on movement direction
    if dx == 1:  # right
        pet_x = px - offset
        pet_y = py + ts // 5

    elif dx == -1:  # left
        pet_x = px + offset
        pet_y = py + ts // 5

    elif dy == -1:  # up
        pet_x = px - offset
        pet_y = py + ts // 3

    elif dy == 1:  # down
        pet_x = px + offset
        pet_y = py + ts // 3

    else:
        pet_x = px - offset
        pet_y = py

    surface.blit(pet_scaled, (pet_x, pet_y))


# ─────────────────────────────────────────────────────────────────────────────
# RESET HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _occupied_positions():
    occ = []
    if gun1.pos:         occ.append(list(gun1.pos))
    if gun2.pos:         occ.append(list(gun2.pos))
    if armor_pickup.pos: occ.append(list(armor_pickup.pos))
    return occ


def _drop_gun(gun, current_time):
    if gun.type:
        gun.drop(current_time)
    gun.pos  = None
    gun.ammo = 0


def reset_round():
    global bullets, green_powerup, blue_powerup, active_animations, explosion_animations
    global last_gun1_spawn_time, last_gun2_spawn_time, last_armor_spawn_time

    bullets.clear()
    active_animations.clear()
    explosion_animations.clear()

    now = pygame.time.get_ticks()

    player1.pos           = md.get_valid_spawn(True)
    player2.pos           = md.get_valid_spawn(False)
    player1.dir           = [1,  0]
    player2.dir           = [-1, 0]
    player1.stunned_until = 0
    player2.stunned_until = 0

    _drop_gun(gun1, now)
    _drop_gun(gun2, now)
    gun1.spawn(md.map_data, now)
    gun2.spawn(md.map_data, now, occupied_positions=[gun1.pos] if gun1.pos else [])
    last_gun1_spawn_time = now
    last_gun2_spawn_time = now

    armor_pickup.clear()
    armor_pickup.spawn(md.map_data, now)
    last_armor_spawn_time = now

    green_powerup = None
    blue_powerup  = None


def reset_game():
    global game_state, winner_text, start_time, last_shrink_time
    md.reset_grid()
    player1.hp = 100  # Updated from 3
    player2.hp = 100  # Updated from 3
    player1.armor = 0
    player2.armor = 0
    reset_round()
    start_time       = pygame.time.get_ticks()
    last_shrink_time = start_time
    game_state  = "playing"
    winner_text = ""


# ═════════════════════════════════════════════════════════════════════════════
# GAME LOOP
# ═════════════════════════════════════════════════════════════════════════════
while True:
    dt           = clock.tick(60) / 1000.0
    current_time = pygame.time.get_ticks()
    TILE_SIZE    = md.map_data.TILE_SIZE

    # ── Events ───────────────────────────────────────────────────────────────
    # Melee is edge-triggered (one press = one swing), tracked here each frame.
    p1_action_pressed = False   # True when K_f was pressed THIS frame
    p2_action_pressed = False   # True when K_RCTRL was pressed THIS frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if game_state == "win" and event.key == pygame.K_r:
                reset_game()
            # Capture single-press for melee
            if event.key == pygame.K_f:
                p1_action_pressed = True
            if event.key == pygame.K_RCTRL:
                p2_action_pressed = True
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            recalculate_layout()

    # ── Speed/slow powerup spawn/despawn ─────────────────────────────────────
    if game_state == "playing":
        if not green_powerup and current_time >= green_spawn_time:
            green_powerup      = get_valid_powerup_spawn()
            green_despawn_time = current_time + POWERUP_DESPAWN
        if not blue_powerup and current_time >= blue_spawn_time:
            blue_powerup      = get_valid_powerup_spawn()
            blue_despawn_time = current_time + POWERUP_DESPAWN
        if green_powerup and current_time >= green_despawn_time:
            green_powerup    = None
            green_spawn_time = current_time + POWERUP_RESPAWN
        if blue_powerup and current_time >= blue_despawn_time:
            blue_powerup    = None
            blue_spawn_time = current_time + POWERUP_RESPAWN

    # ── Playing state logic ───────────────────────────────────────────────────
    time_left = 0
    if game_state == "playing":
        keys = pygame.key.get_pressed()

        time_elapsed = current_time - start_time
        time_left    = max(0, GAME_DURATION - time_elapsed)

        # Map shrink
        if time_left <= 60000:
            if last_shrink_time == start_time:
                last_shrink_time = current_time
            if current_time - last_shrink_time >= SHRINK_INTERVAL:
                last_shrink_time = current_time
                md.shrink_map([player1, player2])
                for g in (gun1, gun2):
                    if g.pos and md.map_grid[g.pos[1]][g.pos[0]] == 1:
                        _drop_gun(g, current_time)
                if (armor_pickup.pos
                        and md.map_grid[armor_pickup.pos[1]][armor_pickup.pos[0]] == 1):
                    armor_pickup.clear()
                    last_armor_spawn_time = current_time
                if green_powerup and md.map_grid[green_powerup[1]][green_powerup[0]] == 1:
                    green_powerup    = None
                    green_spawn_time = current_time + POWERUP_RESPAWN
                if blue_powerup and md.map_grid[blue_powerup[1]][blue_powerup[0]] == 1:
                    blue_powerup    = None
                    blue_spawn_time = current_time + POWERUP_RESPAWN

        # Movement delays
        p1_delay = NORMAL_MOVE_DELAY
        p2_delay = NORMAL_MOVE_DELAY
        if speed_boost_p1 and current_time < speed_boost_p1: p1_delay = FAST_MOVE_DELAY
        if slow_p1        and current_time < slow_p1:        p1_delay = SLOW_MOVE_DELAY
        if speed_boost_p2 and current_time < speed_boost_p2: p2_delay = FAST_MOVE_DELAY
        if slow_p2        and current_time < slow_p2:        p2_delay = SLOW_MOVE_DELAY

        # Stun check
        p1_stunned = current_time < player1.stunned_until
        p2_stunned = current_time < player2.stunned_until

        # Player 1 movement (blocked if stunned)
        if not p1_stunned:
            if keys[pygame.K_w]: player1.move(0, -1, md.map_data, current_time, p1_delay)
            if keys[pygame.K_s]: player1.move(0,  1, md.map_data, current_time, p1_delay)
            if keys[pygame.K_a]: player1.move(-1, 0, md.map_data, current_time, p1_delay)
            if keys[pygame.K_d]: player1.move(1,  0, md.map_data, current_time, p1_delay)

        # Player 2 movement (blocked if stunned)
        if not p2_stunned:
            if keys[pygame.K_UP]:    player2.move(0, -1, md.map_data, current_time, p2_delay)
            if keys[pygame.K_DOWN]:  player2.move(0,  1, md.map_data, current_time, p2_delay)
            if keys[pygame.K_LEFT]:  player2.move(-1, 0, md.map_data, current_time, p2_delay)
            if keys[pygame.K_RIGHT]: player2.move(1,  0, md.map_data, current_time, p2_delay)

        # ── Shoot (held key) OR melee (single press) — context-sensitive ────────
        p1_has_gun = (gun1.owner == player1 or gun2.owner == player1)
        p2_has_gun = (gun1.owner == player2 or gun2.owner == player2)

        # Shooting uses held key so it respects the gun's own cooldown naturally
        if keys[pygame.K_f] and p1_has_gun:
            shoot(gun1, player1, bullets, current_time, md.map_data)
            shoot(gun2, player1, bullets, current_time, md.map_data)

        if keys[pygame.K_RCTRL] and p2_has_gun:
            shoot(gun1, player2, bullets, current_time, md.map_data)
            shoot(gun2, player2, bullets, current_time, md.map_data)

        # Melee uses single-press so one tap = one swing, can't hold to spam.
        # The swing animation ALWAYS plays on press (so the action is visible).
        # Stun only applies if the opponent is on the adjacent tile.
        if p1_action_pressed and not p1_has_gun:
            if current_time - player1.last_melee >= MELEE_COOLDOWN:
                player1.last_melee = current_time

                if SFX_MELEE:
                    SFX_MELEE.play()

                active_animations.append({
                    "attacker": player1,
                    "start":    current_time,
                    "duration": MELEE_ANIM_DURATION,
                })
                swing_tx = player1.pos[0] + player1.dir[0]
                swing_ty = player1.pos[1] + player1.dir[1]
                if [swing_tx, swing_ty] == player2.pos:
                    player2.stunned_until = current_time + MELEE_STUN_DURATION
                    if SFX_MELEE:
                        SFX_MELEE.play()

        if p2_action_pressed and not p2_has_gun:
            if current_time - player2.last_melee >= MELEE_COOLDOWN:
                player2.last_melee = current_time
                
                if SFX_MELEE:
                    SFX_MELEE.play()
                
                active_animations.append({
                    "attacker": player2,
                    "start":    current_time,
                    "duration": MELEE_ANIM_DURATION,
                })
                swing_tx = player2.pos[0] + player2.dir[0]
                swing_ty = player2.pos[1] + player2.dir[1]
                if [swing_tx, swing_ty] == player1.pos:
                    player1.stunned_until = current_time + MELEE_STUN_DURATION
                    if SFX_MELEE:
                        SFX_MELEE.play()

        # Gun pickup — a player who already owns a gun cannot pick up a second one
        for g in (gun1, gun2):
            if g.pos:
                p1_owns_gun = (gun1.owner == player1 or gun2.owner == player1)
                p2_owns_gun = (gun1.owner == player2 or gun2.owner == player2)
                if player1.pos == g.pos and not p1_owns_gun:
                    g.pickup(player1, current_time)
                    if SFX_PICKUP:
                        SFX_PICKUP.play()

                elif player2.pos == g.pos and not p2_owns_gun:
                    g.pickup(player2, current_time)
                    if SFX_PICKUP:
                        SFX_PICKUP.play()

        # Gun expiry / ammo depletion / map despawn
        for g, spawn_key in ((gun1, "last_gun1_spawn_time"),
                              (gun2, "last_gun2_spawn_time")):
            # Equipped gun: expired duration or out of ammo
            expired = g.owner and g.pickup_time and (current_time - g.pickup_time >= g.duration)
            empty   = g.owner and g.ammo <= 0
            # Floor gun: sitting on the map past its duration
            map_expired = (g.pos and g.type
                           and (current_time - g.map_spawn_time >= GUN_TYPES[g.type]["duration"]))
            if expired or empty:
                g.drop(current_time)
                if spawn_key == "last_gun1_spawn_time":
                    last_gun1_spawn_time = current_time
                else:
                    last_gun2_spawn_time = current_time
            elif map_expired:
                g.pos            = None   # remove from map without crediting an owner
                g.map_spawn_time = 0
                if spawn_key == "last_gun1_spawn_time":
                    last_gun1_spawn_time = current_time
                else:
                    last_gun2_spawn_time = current_time

        # Gun respawn (each independently)
        for g, last_t in ((gun1, last_gun1_spawn_time),
                           (gun2, last_gun2_spawn_time)):
            if not g.pos and not g.owner:
                if current_time - last_t >= GUN_RESPAWN_TIME:
                    occ = _occupied_positions()
                    if not g.spawn(md.map_data, current_time, occupied_positions=occ):
                        # record updated timer
                        if g is gun1:
                            last_gun1_spawn_time = current_time
                        else:
                            last_gun2_spawn_time = current_time

        # Armor respawn
        if not armor_pickup.pos:
            if current_time - last_armor_spawn_time >= ARMOR_RESPAWN_TIME:
                armor_pickup.spawn(md.map_data, current_time,
                                   occupied_positions=_occupied_positions())
                last_armor_spawn_time = current_time

        # Armor despawn
        if armor_pickup.pos and current_time >= armor_pickup.despawn_time:
            armor_pickup.clear()
            last_armor_spawn_time = current_time

        # Armor collection
        if armor_pickup.pos:
            for player in (player1, player2):
                if player.pos == armor_pickup.pos:
                    # Only collect if player doesn't have full armor (max 100 armor HP = 3 units)
                    if player.armor_hp < 100:
                        player.armor_hp = min(100, player.armor_hp + 33.33)
                        player.armor = min(3, max(0, math.ceil(player.armor_hp / 33.33)))
                        if SFX_ARMOR: SFX_ARMOR.play()
                        armor_pickup.clear()
                        last_armor_spawn_time = current_time
                    break

        # Bullet update — returns (hit_player, armor_absorbed)
        hit_player, armor_absorbed = update_bullets(
            bullets, [player1, player2], md.map_data, dt, explosion_animations
        )

        if hit_player:
            bullets.clear()
            # Drop gun on hit
            for g in (gun1, gun2):
                if g.owner == hit_player:
                    g.drop(current_time)
                    last_gun1_spawn_time = current_time
                    last_gun2_spawn_time = current_time

            if not armor_absorbed:
                # Full hit: respawn at spawn tile
                if hit_player == player1:
                    player1.pos = md.get_valid_spawn(True)
                    player1.dir = [1,  0]
                else:
                    player2.pos = md.get_valid_spawn(False)
                    player2.dir = [-1, 0]
            # If armor absorbed: player stays in place, armor already decremented

        # Win conditions
        if not player1.is_alive:
            game_state, winner_text = "win", p2_name
        elif not player2.is_alive:
            game_state, winner_text = "win", p1_name
        elif time_left == 0:
            game_state = "win"
            if   player1.hp > player2.hp: winner_text = p1_name
            elif player2.hp > player1.hp: winner_text = p2_name
            else:                          winner_text = "Nobody"

        # Teleport holes (Meadow Crossing)
        holes = md.get_teleport_holes()
        if holes:
            for player, last_tp_attr in ((player1, 'player1_last_teleport'), (player2, 'player2_last_teleport')):
                last_tp = globals()[last_tp_attr]
                if current_time - last_tp >= TELEPORT_COOLDOWN:
                    for hx, hy in holes:
                        if player.pos == [hx, hy]:
                            # Pick a random OTHER hole
                            other_holes = [h for h in holes if h != [hx, hy]]
                            dest = random.choice(other_holes)
                            player.pos = list(dest)
                            globals()[last_tp_attr] = current_time
                            if SFX_TP: SFX_TP.play()
                            break

        # Speed/slow powerup collection
        if green_powerup and player1.pos == green_powerup:
            speed_boost_p1 = current_time + SPEED_BOOST_DURATION
            if SFX_SPEED: SFX_SPEED.play()
            green_powerup  = None; green_spawn_time = current_time + POWERUP_RESPAWN
        if blue_powerup and player1.pos == blue_powerup:
            slow_p2        = current_time + SLOW_DURATION
            if SFX_SLOW: SFX_SLOW.play()
            blue_powerup   = None; blue_spawn_time  = current_time + POWERUP_RESPAWN
        if green_powerup and player2.pos == green_powerup:
            speed_boost_p2 = current_time + SPEED_BOOST_DURATION
            if SFX_SPEED: SFX_SPEED.play()
            green_powerup  = None; green_spawn_time = current_time + POWERUP_RESPAWN
        if blue_powerup and player2.pos == blue_powerup:
            slow_p1        = current_time + SLOW_DURATION
            if SFX_SLOW: SFX_SLOW.play()
            blue_powerup   = None; blue_spawn_time  = current_time + POWERUP_RESPAWN

    # ─────────────────────────────────────────────────────────────────────────
    # RENDERING
    # ─────────────────────────────────────────────────────────────────────────
    map_w = md.MAP_COLS * TILE_SIZE
    map_h = md.MAP_ROWS * TILE_SIZE

    if BACKGROUND_IMG:
        if current_bg_size != (map_w, map_h):
            scaled_bg       = pygame.transform.scale(BACKGROUND_IMG, (map_w, map_h))
            current_bg_size = (map_w, map_h)
        screen.fill((30, 30, 30))
        screen.blit(scaled_bg, (md.map_data.offset_x, md.map_data.offset_y))
    else:
        screen.fill((30, 30, 30))
        if BACKGROUND_COLOR:
            pygame.draw.rect(screen, BACKGROUND_COLOR,
                             (md.map_data.offset_x, md.map_data.offset_y, map_w, map_h))

    md.map_data.draw_map(screen)
    draw_powerups(screen)
    draw_armor_pickup(screen)

    # Both gun pickups on the map
    for g in (gun1, gun2):
        if g.pos:
            img    = GUN_TYPES[g.type]["map_image"]
            draw_x = (md.map_data.offset_x + g.pos[0] * TILE_SIZE
                      + (TILE_SIZE - img.get_width())  // 2)
            draw_y = (md.map_data.offset_y + g.pos[1] * TILE_SIZE
                      + (TILE_SIZE - img.get_height()) // 2)
            screen.blit(img, (draw_x, draw_y))

    # Players
    # Players
    for player in (player1, player2):
        px = md.map_data.offset_x + player.pos[0] * TILE_SIZE
        py = md.map_data.offset_y + player.pos[1] * TILE_SIZE
        pygame.draw.rect(screen, player.color, (px, py, TILE_SIZE, TILE_SIZE))
        # Flashing white border when stunned
        if current_time < player.stunned_until and (current_time // 120) % 2 == 0:
            pygame.draw.rect(screen, (255, 255, 255), (px, py, TILE_SIZE, TILE_SIZE), 3)

        # Eyes — two white circles with black pupils, centered on the tile
        eye_r      = max(2, TILE_SIZE // 8)       # white circle radius
        pupil_r    = max(1, eye_r // 2)            # black pupil radius
        eye_y      = py + TILE_SIZE // 2 - eye_r // 2
        left_eye_x  = px + TILE_SIZE // 3
        right_eye_x = px + (TILE_SIZE * 2) // 3
        for ex in (left_eye_x, right_eye_x):
            pygame.draw.circle(screen, (255, 255, 255), (ex, eye_y), eye_r)
            pygame.draw.circle(screen, (0,   0,   0),   (ex, eye_y), pupil_r)

    draw_player_hat(screen, player1, p1_hat)
    draw_player_hat(screen, player2, p2_hat)
    draw_player_glasses(screen, player1, p1_glasses)
    draw_player_glasses(screen, player2, p2_glasses)
    draw_pet(screen, player1, p1_pet)
    draw_pet(screen, player2, p2_pet)

    # Held guns (draw for both slots)
    for g in (gun1, gun2):
        draw_held_gun(screen, g, player1, md.map_data)
        draw_held_gun(screen, g, player2, md.map_data)

    draw_bullets(screen, bullets)
    draw_explosion_animations(screen, current_time)
    draw_melee_animations(screen, current_time)

    # HUD — Player 1 top-left
    screen.blit(HUD_FONT.render(p1_name, True, (255, 255, 255)), (10, 10))
    draw_weapon_ui(screen, gun1, gun2, player1, 10, 42)
    draw_health_bar(screen, player1, 10, 80) # Adjusted Y

    # HUD — Player 2 bottom-left
    screen.blit(HUD_FONT.render(p2_name, True, (255, 255, 255)), (10, HEIGHT - 115))
    draw_weapon_ui(screen, gun1, gun2, player2, 10, HEIGHT - 80)
    draw_health_bar(screen, player2, 10, HEIGHT - 40) # Adjusted Y

    if game_state == "playing":
        timer_text = HUD_FONT.render(f"Time: {time_left // 1000}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))
        map_text = HUD_FONT.render(f"Map: {selected_map_name}", True, (255, 255, 255))
        screen.blit(map_text,  (WIDTH // 2 - map_text.get_width()  // 2, 45))

    if game_state == "win":
        draw_win_screen(screen, winner_text)

    pygame.display.update()
