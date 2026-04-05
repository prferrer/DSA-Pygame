import pygame
import ctypes
import sys
import random

ctypes.windll.user32.SetProcessDPIAware()
pygame.init()

#Elements???
WIDTH = 1920
HEIGHT = 1080
gun_timer = 0
GUN_DURATION = 30000
gun_ammo = 0
MAX_AMMO =  8
move_delay = 100
last_move_time = 0
player1_hp = 3
player2_hp = 3
game_state = "playing"
winner_text = ""
btn_rects = None
GAME_DURATION = 180000
SHRINK_START = 60000
game_start_time = pygame.time.get_ticks()
gun_respawn_time = None
GUN_RESPAWN_DELAY = 3000

#Available Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0,)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (50, 50, 50)

#Screen 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Map")
clock = pygame.time.Clock()

#Map
map_grid = [
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1],
[1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,1],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

MAP_ROWS = len(map_grid)
MAP_COLS = len(map_grid[0])

TILE_SIZE = min(WIDTH // len(map_grid[0]), HEIGHT // len(map_grid))

offset_x = (WIDTH - (MAP_COLS * TILE_SIZE)) // 2
offset_y = (HEIGHT - (MAP_ROWS * TILE_SIZE)) // 2

max_radius = ((MAP_COLS * TILE_SIZE) ** 2 + (MAP_ROWS * TILE_SIZE) ** 2) ** 0.5 / 2
zone_radius = max_radius

#game timer
def draw_timer(time_remaining_ms):
    total_seconds = max(0, time_remaining_ms // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    timer_font = pygame.font.SysFont(None, 60)
    timer_text = timer_font.render(f"{minutes}:{seconds:02d}", True, WHITE)
    
    screen.blit(timer_text, (
        WIDTH // 2 -timer_text.get_width() // 2,
        offset_y // 2
    ))
    
def is_safe_tile(x, y):
    if map_grid[y][x] != 0:
        return False
    center_x = offset_x + (MAP_COLS * TILE_SIZE) // 2
    center_y = offset_y + (MAP_ROWS * TILE_SIZE) // 2
    tile_cx = offset_x + x * TILE_SIZE + TILE_SIZE //2
    tile_cy = offset_y + y * TILE_SIZE + TILE_SIZE //2
    dist = ((tile_cx - center_x) ** 2 + (tile_cy - center_y) ** 2) ** 0.5
    return dist <= zone_radius
    
#grids kasi the map is a table of binary codes
def draw_map():
    for row in range(MAP_ROWS):
        for col in range(MAP_COLS):

            if map_grid[row][col] == 1:
                color = (173, 216, 230) 
            else:
                color = (0, 0, 0)

            pygame.draw.rect (
                screen,
                color,
                (
                    offset_x + col * TILE_SIZE,
                    offset_y + row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

#PLAYERSSS
player1 = [2, 2] #spawn area sa map based sa grid
player2 = [45, 24] #spawn area sa map based sa grid

player1_dir = [1, 0]
player2_dir = [1, 0]

#Gun
gun_pos = None
gun_owner = None 
bullets = []


#Player Movement
def move(player, dx, dy, direction):
    global zone_radius
    new_x = player[0] + dx
    new_y = player[1] + dy

    #Check boundary para di tumagos sa walls
    if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS:
        if map_grid[new_y][new_x] == 0:
           
           center_x = offset_x + (MAP_COLS * TILE_SIZE) // 2
           center_y = offset_y + (MAP_ROWS * TILE_SIZE) // 2
           
           tile_cx = offset_x + new_x * TILE_SIZE + TILE_SIZE // 2
           tile_cy = offset_y + new_y * TILE_SIZE + TILE_SIZE // 2
           
           dist = ((tile_cx - center_x) ** 2 + (tile_cy - center_y) ** 2) ** 0.5
           
           if dist <= zone_radius:
               player[0] = new_x
               player[1] = new_y
               direction[0] = dx
               direction[1] = dy
               
#player spawn
def draw_players():
    pulse = (pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() / 300)).x / 2 + 0.5
    
    pygame.draw.rect(
        screen, BLUE, 
        (offset_x + player1[0]*TILE_SIZE, offset_y + player1[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    )
    pygame.draw.rect(
        screen, RED, 
        (offset_x + player2[0]*TILE_SIZE, offset_y + player2[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    )
    
    heart_spacing = 22
    heart_size = 20
    total_width_p1 = (player1_hp - 1) * heart_spacing + heart_size
    start_x_p1 = offset_x + player1[0] * TILE_SIZE + TILE_SIZE // 2 - total_width_p1 //2
    
    for i in range(player1_hp):
        x = start_x_p1 + i * heart_spacing
        y = offset_y + player1[1] * TILE_SIZE - 25
        if player1_hp ==  1:
            r = min(255, int(150 + 150 * pulse))
            heart_color = (r, 0, 0)
            tinted = heart_image.copy()
            tinted.fill(heart_color, special_flags=pygame.BLEND_MULT)
            screen.blit(tinted, (x, y))
        else:
            screen.blit(heart_image, (x, y))
            
    total_width_p2 = (player2_hp - 1) * heart_spacing + heart_size
    start_x_p2 = offset_x + player2[0] * TILE_SIZE + TILE_SIZE // 2 - total_width_p2 //2
    
    for i in range(player2_hp):
        x = start_x_p2 + i * heart_spacing
        y = offset_y + player2[1] * TILE_SIZE - 25
        if player2_hp ==  1:
            r = min(255, int(150 + 150 * pulse))
            heart_color = (r, 0, 0)
            tinted = heart_image.copy()
            tinted.fill(heart_color, special_flags=pygame.BLEND_MULT)
            screen.blit(tinted, (x, y))
        else:
            screen.blit(heart_image, (x, y))

#Spawn Gun only spawns sa 0s
def spawn_gun():
    global gun_pos

    def distance (ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    
    FAIRNESS_TRESHOLD = 10
    attempts = 0
    
    while True:
        x = random.randint(0, MAP_COLS - 1)
        y = random.randint(0, MAP_ROWS - 1)

        if is_safe_tile(x, y):
            dist_p1 = distance(x, y, player1 [0], player1[1])
            dist_p2 = distance(x, y, player2 [0], player2[1])

            if abs(dist_p1 - dist_p2) <= FAIRNESS_TRESHOLD or attempts > 200:
                gun_pos = [x, y]
                break

        attempts += 1

def draw_gun():
    gun_size = TILE_SIZE // 3

    # spawn gun sa map mismo
    if gun_pos is not None:
        pygame.draw.rect(
            screen,
            (255, 255, 0),
            (
                gun_pos[0] * TILE_SIZE + TILE_SIZE//3,
                gun_pos[1] * TILE_SIZE + TILE_SIZE//3,
                gun_size,
                gun_size
            )
        )

    #user getting gun
    if gun_owner == "p1":
        offset_x = player1_dir[0] * TILE_SIZE // 2
        offset_y = player1_dir[1] * TILE_SIZE // 2

        pygame.draw.rect(
            screen,
            (255, 255, 0),
            (
                player1[0]*TILE_SIZE + offset_x + TILE_SIZE//3,
                player1[1]*TILE_SIZE + offset_y + TILE_SIZE//3,
                gun_size,
                gun_size
            )
        )

    elif gun_owner == "p2":
        offset_x = player2_dir[0] * TILE_SIZE // 2
        offset_y = player2_dir[1] * TILE_SIZE // 2

        pygame.draw.rect(
            screen,
            (255, 255, 0),
            (
                player2[0]*TILE_SIZE + offset_x + TILE_SIZE//3,
                player2[1]*TILE_SIZE + offset_y + TILE_SIZE//3,
                gun_size,
                gun_size
            )
        )
spawn_gun()

#zone for 1 minute mark
def draw_zone(radius):
    center_x = offset_x + (MAP_COLS * TILE_SIZE) // 2
    center_y = offset_y + (MAP_ROWS * TILE_SIZE) // 2
    
    zone_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    zone_tile.fill((255, 0, 0, 100))
    
    for row in range(MAP_ROWS):
        for col in range(MAP_COLS):
            if map_grid[row][col] == 0:
                tile_cx = offset_x + col * TILE_SIZE + TILE_SIZE // 2
                tile_cy = offset_y + row * TILE_SIZE + TILE_SIZE // 2
                
                dist = ((tile_cx - center_x) ** 2 + (tile_cy - center_y) ** 2) ** 0.5
                
                if dist > radius:
                    screen.blit(zone_tile, (
                        offset_x + col * TILE_SIZE,
                        offset_y + row * TILE_SIZE
                    ))
                    
def find_safe_respawn(default_x, default_y):
    if is_safe_tile(default_x, default_y):
        return[default_x, default_y]
    
    best = None
    best_dist = float('inf')
    
    for row in range (MAP_ROWS):
        for col in range (MAP_COLS):
            if is_safe_tile(col, row):
                dist = abs(col - default_x) + abs(row - default_y)
                if dist < best_dist:
                    best_dist = dist
                    best = [col, row]
                    
    return best if best else [default_x, default_y]
                    
def check_zone_death():
    global player1_hp, player2_hp, game_state, winner_text
    
    center_x = offset_x + (MAP_COLS * TILE_SIZE) // 2
    center_y = offset_y + (MAP_ROWS * TILE_SIZE) // 2
    
    for player, player_num in [(player1, 1), (player2, 2)]:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        safe_exits = 0
        
        for dx, dy in directions:
            nx = player[0] + dx
            ny = player[1] + dy
            
            if not (0 <= nx < MAP_COLS and 0 <= ny < MAP_ROWS):
                continue
            
            if map_grid[ny][nx] == 1:
                continue
            
            tile_cx = offset_x + nx * TILE_SIZE + TILE_SIZE // 2
            tile_cy = offset_y + ny * TILE_SIZE + TILE_SIZE // 2
            dist = ((tile_cx - center_x) ** 2 + (tile_cy - center_y) ** 2) ** 0.5
            
            if dist <= zone_radius:
                safe_exits += 1
                
        if safe_exits == 0:
            if player_num == 1:
                player1_hp -= 1
                if player1_hp <= 0:
                    game_state = "win"
                    winner_text = "Player 2"
                else:
                    player1[:] = find_safe_respawn(2, 2)
                    gun_owner = None
                    gun_respawn_time = pygame.time.get_ticks() + GUN_RESPAWN_DELAY
            else:
                player2_hp -= 1
                if player2_hp <= 0:
                    game_state = "win"
                    winner_text = "Player 1"
                else:
                    player2[:] = find_safe_respawn(45, 24)
                    gun_owner = None
                    gun_respawn_time = pygame.time.get_ticks() + GUN_RESPAWN_DELAY 
                    
                
def draw_win_screen(winner):
    #Darkness Overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    #Win Panel
    panel_width = 600
    panel_height = 350
    panel_x = WIDTH // 2 - panel_width // 2
    panel_y = HEIGHT // 2 - panel_height // 2
    pygame.draw.rect(screen, (30, 30, 30), (panel_x, panel_y, panel_width, panel_height), border_radius = 15)
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3, border_radius = 15)

    #Winner Text
    title_font = pygame.font.SysFont(None, 80)
    sub_font = pygame.font.SysFont(None, 40)

    winner_text = title_font.render(f"{winner} Wins!", True, WHITE)
    screen.blit(winner_text, (
        WIDTH // 2 - winner_text.get_width() // 2,
        panel_y + 60
    ))

    #Play Again
    play_btn = pygame.Rect(WIDTH // 2 - 220, panel_y + 180, 200, 60)
    pygame.draw.rect(screen, (0, 180, 0), play_btn, border_radius = 10)
    play_text = sub_font.render("Play Again", True, WHITE)
    screen.blit(play_text, (
        play_btn.centerx - play_text.get_width() // 2,
        play_btn.centery - play_text.get_height() // 2
    ))
    
    #Menu Screen
    menu_btn = pygame.Rect(WIDTH // 2 + 20, panel_y + 180, 200, 60)
    pygame.draw.rect(screen, (0, 180, 0), menu_btn, border_radius = 10)
    menu_text = sub_font.render("Main Menu", True, WHITE)
    screen.blit(menu_text, (
        menu_btn.centerx - play_text.get_width() // 2,
        menu_btn.centery - play_text.get_height() // 2
    ))

    return play_btn, menu_btn

#boolets main settings
def shoot(player, direction, owner):
    bullet_speed = 10

    bullets.append({
        "x": player[0] * TILE_SIZE + TILE_SIZE // 2,
        "y": player[1] * TILE_SIZE + TILE_SIZE // 2,
        "dx": direction[0] * bullet_speed,
        "dy": direction[1] * bullet_speed,
        "owner": owner,
        "distance": 0
    })

#Resets All Variables
def reset_game():
    global game_state, winner_text, gun_owner, gun_ammo, gun_timer, gun_respawn_time
    global player1_hp, player2_hp, game_start_time, zone_radius

    player1[:] = [2, 2]
    player2[:] = [45, 24]
    player1_hp = 3
    player2_hp = 3
    gun_owner = None
    gun_ammo = 0
    gun_timer = 0
    bullets.clear()
    game_state = "playing"
    winner_text = ""
    game_start_time = pygame.time.get_ticks()
    zone_radius = max_radius
    spawn_gun()

heart_image = pygame.image.load ("hearts.png")
heart_image = pygame.transform.scale(heart_image, (20, 20))

#game loopppp
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "win":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if btn_rects:
                    if btn_rects[0].collidepoint(mouse_pos):
                        reset_game()
                    elif btn_rects[1].collidepoint(mouse_pos):
                        reset_game()

        #player shooting
        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if gun_owner == "p1" and gun_ammo > 0:
                        shoot(player1, player1_dir, "p1")
                        gun_ammo -= 1
                    elif gun_owner == "p2" and gun_ammo > 0:
                        shoot(player2, player2_dir, "p2")
                        gun_ammo -= 1

    #bg refresh
    screen.fill((30, 30, 30))
    
    if game_state == "playing": 
        elapsed = pygame.time.get_ticks() - game_start_time
        time_remaining = GAME_DURATION - elapsed
        
        keys = pygame.key.get_pressed()

    #player movement
    #Player 1 (WASD)
        current_time = pygame.time.get_ticks()
        if current_time - last_move_time >= move_delay:
            if keys[pygame.K_w]:
                move (player1, 0, -1, player1_dir)
            if keys[pygame.K_s]:
                move (player1, 0, 1, player1_dir)
            if keys[pygame.K_a]:
                move (player1, -1, 0, player1_dir)
            if keys[pygame.K_d]:
                move (player1, 1, 0, player1_dir)
    
    #Player 2 (Arrows)
            if keys[pygame.K_UP]:
                move (player2, 0, -1, player2_dir)
            if keys[pygame.K_DOWN]:
                move (player2, 0, 1, player2_dir)
            if keys[pygame.K_LEFT]:
                move (player2, -1, 0, player2_dir)
            if keys[pygame.K_RIGHT]:
                move (player2, 1, 0, player2_dir)

            last_move_time = current_time

    #gun usage conditions
        if gun_pos is not None:
            if player1 == gun_pos:
                gun_owner = "p1"
                gun_pos = None
                gun_ammo = MAX_AMMO
                gun_timer = pygame.time.get_ticks() + GUN_DURATION
            elif player2 == gun_pos:
                gun_owner = "p2"
                gun_pos = None 
                gun_ammo = MAX_AMMO
                gun_timer = pygame.time.get_ticks() + GUN_DURATION
    
        draw_map()
        draw_players()
        draw_gun()
    
    btn_rects = None 
    
    if game_state == "playing":
        p1_rect = pygame.Rect(offset_x + player1[0]*TILE_SIZE, offset_y + player1[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        p2_rect = pygame.Rect(offset_x + player2[0]*TILE_SIZE, offset_y + player2[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)

    #bullets logiC
        for bullet in bullets[:]:
            old_x = bullet["x"]
            old_y = bullet["y"]
            bullet["x"] += bullet["dx"] 
            bullet["y"] += bullet["dy"]
            bullet["distance"] += abs(bullet["dx"]) + abs(bullet["dy"])

            grid_x = int(bullet["x"] // TILE_SIZE)
            grid_y = int(bullet["y"] // TILE_SIZE)

    #bullets wall collision
            if 0 <= grid_x < MAP_COLS and 0 <= grid_y < MAP_ROWS:
                if map_grid[grid_y][grid_x] == 1:
                    bullets.remove(bullet)
                    continue

    #bullets distance limit
            if bullet["distance"] > 200:
                bullets.remove(bullet)
                continue

            new_pos = (bullet["x"], bullet["y"])
            old_pos = (old_x, old_y)

    #bullets when hitting a user
            if bullet["owner"] == "p1" and p2_rect.clipline(old_pos, new_pos):
                bullets.clear()
                player2_hp -= 1

                if player2_hp <= 0:
                    game_state = "win"
                    winner_text = "Player 1"
                else:
                    player2[:] = find_safe_respawn(45, 24)
                    gun_owner = None
                    gun_respawn_time = pygame.time.get_ticks() + GUN_RESPAWN_DELAY
                break

            if bullet["owner"] == "p2" and p1_rect.clipline(old_pos, new_pos):
                bullets.clear()
                player1_hp -= 1

                if player1_hp <= 0:
                    game_state = "win"
                    winner_text = "Player 2"
                else:
                    player1[:] = find_safe_respawn(2, 2)
                    gun_owner = None
                    gun_respawn_time = pygame.time.get_ticks() + GUN_RESPAWN_DELAY
                break

            pygame.draw.rect(screen, (255, 255, 0), (bullet["x"], bullet["y"], 5, 5))

        if gun_owner is not None:
            if pygame.time.get_ticks() >= gun_timer or gun_ammo <= 0:
                gun_owner = None
                gun_pos = None
                gun_respawn_time = pygame.time.get_ticks() + GUN_RESPAWN_DELAY
                
        if gun_pos is None and gun_owner is None and gun_respawn_time is not None:
            if pygame.time.get_ticks() >= gun_respawn_time:
                spawn_gun()
                gun_respawn_time = None

        font = pygame.font.SysFont(None, 36)

        if gun_owner is not None:
            ammo_text = font.render(f"Ammo: {gun_ammo}", True, (255, 255, 255))
            screen.blit(ammo_text, (900, 500))
        
        if time_remaining <= SHRINK_START:
            shrink_progress = 1 - (time_remaining / SHRINK_START)
            zone_radius = max_radius * (1 - shrink_progress)
            check_zone_death()
            
        draw_timer(time_remaining)
        
        if time_remaining <= SHRINK_START:
            draw_zone(zone_radius)

    if game_state == "win":
        draw_map()
        draw_players()
        btn_rects = draw_win_screen(winner_text)
        
    pygame.display.update()
