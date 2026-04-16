import pygame
import sys
import random
import os

from menu import run_menu
from config import *
import map_data as md
from players import Player
from guns import GUN_TYPES, GunSystem, shoot, scale_gun_images
from mechanics import update_bullets

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

global green_powerup, blue_powerup
global green_spawn_time, blue_spawn_time
global green_despawn_time, blue_despawn_time
global speed_boost_p1, speed_boost_p2
global slow_p1, slow_p2

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("PacPew - 2D Arena Shooter")
clock = pygame.time.Clock()

menu_data = run_menu(screen)

scale_gun_images(md.map_data.TILE_SIZE)

HUD_FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 72)
MED_FONT = pygame.font.SysFont(None, 40)

p1_spawn = md.get_valid_spawn(True)
p2_spawn = md.get_valid_spawn(False)

player1 = Player(p1_spawn[0], p1_spawn[1], menu_data["p1_color"])
player2 = Player(p2_spawn[0], p2_spawn[1], menu_data["p2_color"])

selected_map_name = menu_data["map_name"]

gun = GunSystem()
gun.spawn(md.map_data)
bullets = []

GUN_RESPAWN_TIME = 5000
last_gun_spawn_time = pygame.time.get_ticks()
start_time = pygame.time.get_ticks()
last_shrink_time = start_time

game_state = "playing"
winner_text = ""

try:
    HEART_IMG = pygame.image.load("assets/health/hearts.png").convert_alpha()
    HEART_IMG = pygame.transform.scale(HEART_IMG, (24, 24))
except:
    HEART_IMG = pygame.Surface((24, 24), pygame.SRCALPHA)
    HEART_IMG.fill((255, 0, 0))

try:
    SPEED_IMG = pygame.image.load("assets/powerups/speedboost.png").convert_alpha()
except:
    SPEED_IMG = None

try:
    SLOW_IMG = pygame.image.load("assets/powerups/slowdown.png").convert_alpha() 
except:
    SLOW_IMG = None

try:
    BACKGROUND_IMG = pygame.image.load("Map3.png").convert()
except:
    BACKGROUND_IMG = None

scaled_bg = None
current_bg_size = (0, 0)
    
def draw_health_bar(screen, player, x, y):
    for i in range(int(player.hp)):
        screen.blit(HEART_IMG, (x + i*28, y))
    hp_text = HUD_FONT.render(f"{player.hp:.1f}", True, (255, 255, 255))
    screen.blit(hp_text, (x + max(0,int(player.hp))*28 + 5, y))

def draw_held_gun(screen, gun, player, map_data_module):
    if gun.owner != player:
        return
    img = GUN_TYPES[gun.type]["equipped_image"]
    dx, dy = player.dir
    
    if  (dx, dy) == (1, 0): rotated = img
    elif (dx, dy) == (-1, 0): rotated = pygame.transform.flip(img, True, False)
    elif (dx, dy) == (0, -1): rotated = pygame.transform.rotate(img, 90)
    elif (dx, dy) == (0, 1): rotated = pygame.transform.rotate(img, 270)
    else: rotated = img
  
    center_x = map_data_module.offset_x + player.pos[0] * map_data_module.TILE_SIZE
    center_y = map_data_module.offset_y + player.pos[1] * map_data_module.TILE_SIZE
    
    offset_x = dx * map_data_module.TILE_SIZE // 2
    offset_y = dy * map_data_module.TILE_SIZE // 2
    
    draw_x = center_x + offset_x + (map_data_module.TILE_SIZE - rotated.get_width()) // 2
    draw_y = center_y + offset_y + (map_data_module.TILE_SIZE - rotated.get_height()) // 2
    screen.blit(rotated, (draw_x, draw_y))

def draw_weapon_ui(screen, gun, player, x, y):
    if gun.owner == player:
        text = f"{gun.type.upper()} | Ammo: {gun.ammo}"
    else:
        text = "No Weapon"
    ui = HUD_FONT.render(text, True, (255,255,255))
    screen.blit(ui, (x, y))

def draw_win_screen(screen, winner_text):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    screen.blit(overlay, (0,0))
    win_surf = BIG_FONT.render(f"{winner_text} Wins!", True, (255, 215, 0))
    sub_surf = MED_FONT.render("Press R to play again  |  ESC to quit", True, (200,200,200))
    screen.blit(win_surf, win_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
    screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))

def reset_round():
    global bullets, green_powerup, blue_powerup
    bullets.clear()
    
    player1.pos = md.get_valid_spawn(True)
    player2.pos = md.get_valid_spawn(False)
    player1.dir = [1, 0]
    player2.dir = [-1, 0]
    
    gun.owner = None
    gun.pos = None
    gun.ammo = 0
    gun.spawn(md.map_data)
    
    green_powerup = None
    blue_powerup = None

def reset_game():
    global game_state, winner_text, last_gun_spawn_time, start_time, last_shrink_time
    md.reset_grid()
    player1.hp = 3
    player2.hp = 3
    reset_round()
    last_gun_spawn_time = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()
    last_shrink_time = start_time
    game_state = "playing"
    winner_text = ""

green_powerup = None
blue_powerup = None
green_spawn_time = pygame.time.get_ticks() + random.randint(5000, 15000)
blue_spawn_time = pygame.time.get_ticks() + random.randint(5000, 15000)
green_despawn_time = None
blue_despawn_time = None
speed_boost_p1 = None
speed_boost_p2 = None
slow_p1 = None
slow_p2 = None
POWERUP_DESPAWN = 15000
POWERUP_RESPAWN = 10000
SPEED_BOOST_DURATION = 2000
SLOW_DURATION = 2000

def get_valid_powerup_spawn():
    while True:
        x = random.randint(0, md.MAP_COLS-1)
        y = random.randint(0, md.MAP_ROWS-1)
        if md.map_grid[y][x] == 0:
            return [x, y]

def draw_powerups(screen):
    if green_powerup:
        x = md.map_data.offset_x + green_powerup[0]*md.map_data.TILE_SIZE
        y = md.map_data.offset_y + green_powerup[1]*md.map_data.TILE_SIZE
        if SPEED_IMG:
            scaled = pygame.transform.scale(SPEED_IMG, (md.map_data.TILE_SIZE, md.map_data.TILE_SIZE))
            screen.blit(scaled, (x, y))
        else:
            pygame.draw.circle(screen, (0,255,0), (x + md.map_data.TILE_SIZE//2, y + md.map_data.TILE_SIZE//2), md.map_data.TILE_SIZE//2)
            
    if blue_powerup:
        x = md.map_data.offset_x + blue_powerup[0]*md.map_data.TILE_SIZE
        y = md.map_data.offset_y + blue_powerup[1]*md.map_data.TILE_SIZE
        if SLOW_IMG:
            scaled = pygame.transform.scale(SLOW_IMG, (md.map_data.TILE_SIZE, md.map_data.TILE_SIZE))
            screen.blit(scaled, (x, y))
        else:
            pygame.draw.circle(screen, (0,0,255), (x + md.map_data.TILE_SIZE//2, y + md.map_data.TILE_SIZE//2), md.map_data.TILE_SIZE//2)
if not os.path.exists("assets/coconut/coconut.jfif"): sys.exit("Critical Error: Missing essential texture 'coconut.jfif'.")

def draw_bullets(screen, bullets):
    for b in bullets:
        # Drawing slightly larger 8x8 bullets so they are clearly visible
        pygame.draw.rect(screen, (255, 255, 0), (int(b["x"]), int(b["y"]), 8, 8))

# =========================
# GAME LOOP
# =========================
while True:
    # Explicitly enforce float division so 'dt' isn't zeroed out
    dt = clock.tick(60) / 1000.0 
    current_time = pygame.time.get_ticks()

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

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
            TILE_SIZE = min(WIDTH // md.MAP_COLS, HEIGHT // md.MAP_ROWS)
            md.map_data.TILE_SIZE = TILE_SIZE
            md.map_data.offset_x = (WIDTH - (md.MAP_COLS * TILE_SIZE)) // 2
            md.map_data.offset_y = (HEIGHT - (md.MAP_ROWS * TILE_SIZE)) // 2
            scale_gun_images(md.map_data.TILE_SIZE)
    
    TILE_SIZE = min(WIDTH // md.MAP_COLS, HEIGHT // md.MAP_ROWS)
    md.map_data.TILE_SIZE = TILE_SIZE
    md.map_data.offset_x = (WIDTH - (md.MAP_COLS * TILE_SIZE)) // 2
    md.map_data.offset_y = (HEIGHT - (md.MAP_ROWS * TILE_SIZE)) // 2

    if game_state == "playing":
        if not green_powerup and current_time >= green_spawn_time:
            green_powerup = get_valid_powerup_spawn()
            green_despawn_time = current_time + POWERUP_DESPAWN
        if not blue_powerup and current_time >= blue_spawn_time:
            blue_powerup = get_valid_powerup_spawn()
            blue_despawn_time = current_time + POWERUP_DESPAWN
            
        if green_powerup and current_time >= green_despawn_time:
            green_powerup = None
            green_spawn_time = current_time + POWERUP_RESPAWN
        if blue_powerup and current_time >= blue_despawn_time:
            blue_powerup = None
            blue_spawn_time = current_time + POWERUP_RESPAWN

    time_left = 0
    if game_state == "playing":
        keys = pygame.key.get_pressed()

        time_elapsed = current_time - start_time
        time_left = max(0, GAME_DURATION - time_elapsed)
        
        if time_left <= 60000:
            if last_shrink_time == start_time:
                last_shrink_time = current_time 
            
            if current_time - last_shrink_time >= SHRINK_INTERVAL:
                last_shrink_time = current_time
                md.shrink_map([player1, player2])
        
                if gun.pos and md.map_grid[gun.pos[1]][gun.pos[0]] == 1:
                    gun.pos = None
                    gun.owner = None
                    last_gun_spawn_time = current_time
            
                if green_powerup and md.map_grid[green_powerup[1]][green_powerup[0]] == 1: 
                    green_powerup = None
                    green_spawn_time = current_time + POWERUP_RESPAWN
            
                if blue_powerup and md.map_grid[blue_powerup[1]][blue_powerup[0]] == 1: 
                    blue_powerup = None
                    blue_spawn_time = current_time + POWERUP_RESPAWN

        p1_delay = NORMAL_MOVE_DELAY
        p2_delay = NORMAL_MOVE_DELAY

        if speed_boost_p1 and current_time < speed_boost_p1: p1_delay = FAST_MOVE_DELAY
        if slow_p1 and current_time < slow_p1: p1_delay = SLOW_MOVE_DELAY
        if speed_boost_p2 and current_time < speed_boost_p2: p2_delay = FAST_MOVE_DELAY
        if slow_p2 and current_time < slow_p2: p2_delay = SLOW_MOVE_DELAY

        if keys[pygame.K_w]: player1.move(0, -1, md.map_data, current_time, p1_delay)
        if keys[pygame.K_s]: player1.move(0, 1, md.map_data, current_time, p1_delay)
        if keys[pygame.K_a]: player1.move(-1, 0, md.map_data, current_time, p1_delay)
        if keys[pygame.K_d]: player1.move(1, 0, md.map_data, current_time, p1_delay)

        if keys[pygame.K_UP]: player2.move(0, -1, md.map_data, current_time, p2_delay)
        if keys[pygame.K_DOWN]: player2.move(0, 1, md.map_data, current_time, p2_delay)
        if keys[pygame.K_LEFT]: player2.move(-1, 0, md.map_data, current_time, p2_delay)
        if keys[pygame.K_RIGHT]: player2.move(1, 0, md.map_data, current_time, p2_delay)
        
        # Shoot via 'keys' state rather than isolated events to bypass ghosting drops
        if keys[pygame.K_f]: shoot(gun, player1, bullets, current_time, md.map_data)
        if keys[pygame.K_RCTRL]: shoot(gun, player2, bullets, current_time, md.map_data)

        if gun.pos:
            if player1.pos == gun.pos: gun.pickup(player1, current_time)
            elif player2.pos == gun.pos: gun.pickup(player2, current_time)

        if gun.owner and gun.ammo <= 0:
            from guns import gun_last_used
            gun_last_used[gun.type] = current_time
            gun.owner = None
            last_gun_spawn_time = current_time

        # Drop if duration expired
        if gun.owner and gun.pickup_time and (current_time - gun.pickup_time >= gun.duration):
            from guns import gun_last_used
            gun_last_used[gun.type] = current_time
            gun.owner = None
            gun.pickup_time = None
            last_gun_spawn_time = current_time

        # Respawn if no position and no owner
        if not gun.pos and not gun.owner:
            if current_time - last_gun_spawn_time >= GUN_RESPAWN_TIME:
                spawned = gun.spawn(md.map_data, current_time)
                if not spawned:
                    last_gun_spawn_time = current_time

       # Check if a player was hit
        hit_player = update_bullets(bullets, [player1, player2], md.map_data, dt)
        if hit_player:
            # Only respawn the player who actually took the damage
            if hit_player.hp > 0:
                if hit_player == player1:
                    player1.pos = md.get_valid_spawn(True)
                    player1.dir = [1, 0]
                elif hit_player == player2:
                    player2.pos = md.get_valid_spawn(False) # False for player 2's spawn side
                    player2.dir = [-1, 0]
            
            # Clear all bullets from the screen after a hit to reset the skirmish
            bullets.clear()
            
            # If the player who got hit was holding the gun, they drop it
            if gun.owner:
                gun.owner = None
                gun.pickup_time = None
                last_gun_spawn_time = current_time

        if not player1.is_alive: game_state, winner_text = "win", "Player 2"
        elif not player2.is_alive: game_state, winner_text = "win", "Player 1"
        elif time_left == 0:
            game_state = "win"
            if player1.hp > player2.hp: winner_text = "Player 1"
            elif player2.hp > player1.hp: winner_text = "Player 2"
            else: winner_text = "Nobody"
    
        if green_powerup and player1.pos == green_powerup:
            speed_boost_p1 = current_time + SPEED_BOOST_DURATION
            green_powerup = None
            green_spawn_time = current_time + POWERUP_RESPAWN 
            
        if blue_powerup and player1.pos == blue_powerup:
            slow_p2 = current_time + SLOW_DURATION
            blue_powerup = None
            blue_spawn_time = current_time + POWERUP_RESPAWN 
            
        if green_powerup and player2.pos == green_powerup:
            speed_boost_p2 = current_time + SPEED_BOOST_DURATION
            green_powerup = None
            green_spawn_time = current_time + POWERUP_RESPAWN 
            
        if blue_powerup and player2.pos == blue_powerup:
            slow_p1 = current_time + SLOW_DURATION
            blue_powerup = None
            blue_spawn_time = current_time + POWERUP_RESPAWN

    screen.fill((30, 30, 30))

    # --- Draw the Background Image ---
    if BACKGROUND_IMG:
        map_w = md.MAP_COLS * TILE_SIZE
        map_h = md.MAP_ROWS * TILE_SIZE
        
        # Only rescale the image if the window size/tile size has changed
        if current_bg_size != (map_w, map_h):
            scaled_bg = pygame.transform.scale(BACKGROUND_IMG, (map_w, map_h))
            current_bg_size = (map_w, map_h)
            
        # Draw the background exactly where the map grid starts
        screen.blit(scaled_bg, (md.map_data.offset_x, md.map_data.offset_y))

    # Draw the shrinking map layers over the background
    md.map_data.draw_map(screen)
    draw_powerups(screen)

    md.map_data.draw_map(screen)
    draw_powerups(screen)

    if gun.pos:
        img = GUN_TYPES[gun.type]["map_image"]
        draw_x = md.map_data.offset_x + gun.pos[0] * TILE_SIZE + (TILE_SIZE - img.get_width()) // 2
        draw_y = md.map_data.offset_y + gun.pos[1] * TILE_SIZE + (TILE_SIZE - img.get_height()) // 2
        screen.blit(img, (draw_x, draw_y))

    for player in [player1, player2]:
        pygame.draw.rect(screen, player.color,
            (md.map_data.offset_x + player.pos[0] * TILE_SIZE,
             md.map_data.offset_y + player.pos[1] * TILE_SIZE,
             TILE_SIZE, TILE_SIZE))

    draw_held_gun(screen, gun, player1, md.map_data)
    draw_held_gun(screen, gun, player2, md.map_data)
    draw_bullets(screen, bullets)

    draw_weapon_ui(screen, gun, player1, 10, 10)
    draw_health_bar(screen, player1, 10, 46)
    draw_weapon_ui(screen, gun, player2, 10, HEIGHT - 70)
    draw_health_bar(screen, player2, 10, HEIGHT - 34)

    if game_state == "playing":
        timer_text = HUD_FONT.render(f"Time: {time_left // 1000}", True, (255, 255, 255))
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))

        map_text = HUD_FONT.render(f"Map: {selected_map_name}", True, (255, 255, 255))
        screen.blit(map_text, (WIDTH // 2 - map_text.get_width() // 2, 45))

    if game_state == "win":
        draw_win_screen(screen, winner_text)

    pygame.display.update()
