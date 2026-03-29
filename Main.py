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
GUN_DURATION = 10000
gun_ammo = 0
MAX_AMMO =  8
move_delay = 100
last_move_time = 0
player1_hp = 3
player2_hp = 3
game_state = "playing"
winner_text = ""

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
    new_x = player[0] + dx
    new_y = player[1] + dy

    #Check boundary para di tumagos sa walls
    if 0 <= new_x < MAP_COLS and 0 <= new_y < MAP_ROWS:
        if map_grid[new_y][new_x] == 0:
            player[0] = new_x
            player[1] = new_y  

            direction[0] = dx
            direction[1] = dy 

#player spawn
def draw_players():
    pygame.draw.rect(
        screen, BLUE, 
        (player1[0]*TILE_SIZE, player1[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
    )

    pygame.draw.rect(
        screen, RED, 
        (player2[0]*TILE_SIZE, player2[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
    )

    for i in range (player1_hp):
        screen.blit(heart_image, (
            offset_x + player1[0]*TILE_SIZE + (i * 22) - 11,
            offset_y + player1[1]*TILE_SIZE - 25
        ))

    for i in range (player2_hp):
        screen.blit(heart_image, (
            offset_x + player2[0]*TILE_SIZE + (i * 22) - 11,
            offset_y + player2[1]*TILE_SIZE - 25
        ))


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

        if map_grid[y][x] == 0:
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
    pygame.draw.rect(screen (30, 30, 30), (panel_x, panel_y, panel_width, panel_height), border_radius = 15)
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

heart_image = pygame.image.load ("hearts.png")
heart_image = pygame.transform.scale(heart_image, (20, 20))


#game loopppp
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        #player shooting
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if gun_owner == "p1" and gun_ammo > 0:
                    shoot(player1, player1_dir, "p1")
                    gun_ammo -= 1
                elif gun_owner == "p2" and gun_ammo > 0:
                    shoot(player2, player2_dir, "p2")
                    gun_ammo -= 1


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

    #bg refresh
    screen.fill((30, 30, 30))
    draw_map()
    draw_players()
    draw_gun()

    #bullets logic
    p1_rect = pygame.Rect(player1[0]*TILE_SIZE, player1[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)
    p2_rect = pygame.Rect(player2[0]*TILE_SIZE, player2[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE)

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
                print("Player 1 wins!")
                player1_hp = 3
                player2_hp = 3
                gun_owner = None
                spawn_gun()
                player1[:] = [2, 2]
                player2[:] = [45, 24]
            else:
                player2[:] = [45, 24]
                gun_owner = None
                spawn_gun()
            break

        if bullet["owner"] == "p2" and p1_rect.clipline(old_pos, new_pos):
            bullets.clear()
            player1_hp -= 1

            if player1_hp <= 0:
                print("Player 2 wins!")
                player1_hp = 3
                player2_hp = 3
                gun_owner = None
                spawn_gun()
                player1[:] = [2, 2]
                player2[:] = [45, 24]
            else:
                player1[:] = [2, 2]
                gun_owner = None
                spawn_gun()
            break

        pygame.draw.rect(screen, (255, 255, 0), (bullet["x"], bullet["y"], 5, 5))

    if gun_owner is not None:
        if pygame.time.get_ticks() >= gun_timer or gun_ammo <= 0:
            gun_owner = None
            spawn_gun()

    font = pygame.font.SysFont(None, 36)

    if gun_owner is not None:
        ammo_text = font.render(f"Ammo: {gun_ammo}", True, (255, 255, 255))
        screen.blit(ammo_text, (900, 500))

    pygame.display.update()

#Things to add:
# map 3
# character customization (shape color)
# weapons with different interactions (guns)
# point or life system (3 hearts)
# map hidden features(?) 3 
# game timer and game end game (3 mins, 1 minute map shrink)

#Things to improve:
# Gun Spawn minsan mas malapit sa isa 
# bullet logic depende sa baril
# character movement 
# map design.....
# weapon design 
# colors.....

#Maps and hidden feature: Girlssssss 
#Weapons: Ezekiel and Clarence
#Shrink Map: 
#Add Life:  
#  
#Character Customize: Gale
