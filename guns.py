import random
import pygame
import map_data

#slop ni clarence

GUN_TYPES = {
    "pistol": {"ammo": 8, "bullet_speed": 300, "cooldown": 400, "damage": 1, "range": 300, "path": "guns/assets/Glock18c-PxNBG.png"},
    "rifle": {"ammo": 20, "bullet_speed": 500, "cooldown": 120, "damage": 1.5, "range": 600, "path": "guns/assets/M4A1-Px-PxNBG.png"},
    "shotgun": {"ammo": 5, "bullet_speed": 200, "cooldown": 800, "damage": 0.7, "spread": 8, "range": 150, "path": "guns/assets/Rem870-Px-PxNBG.png"}
}

def scale_gun_images(tile_size):
    for gun in GUN_TYPES.values():
        try:
            img = pygame.image.load(gun["path"]).convert_alpha()
            gun["image"] = pygame.transform.scale(img, (tile_size, tile_size))
        except (FileNotFoundError, pygame.error):
            gun["image"] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            gun["image"].fill((100, 100, 100))

class GunSystem:
    def __init__(self):
        self.pos = None
        self.owner = None
        self.type = None
        self.ammo = 0
        self.last_shot = 0

    def spawn(self, map_data_module):
        while True:
            x = random.randint(0, map_data_module.MAP_COLS - 1)
            y = random.randint(0, map_data_module.MAP_ROWS - 1)
            if map_data_module.map_grid[y][x] == 0:
                self.pos = [x, y]
                self.type = random.choice(list(GUN_TYPES.keys()))
                break

    def pickup(self, player):
        gun_data = GUN_TYPES[self.type]
        self.owner = player
        self.ammo = gun_data["ammo"]
        self.pos = None

def shoot(gun, player, bullets, current_time, map_data_module):
    if gun.owner != player:
        return
    gun_data = GUN_TYPES[gun.type]
    if current_time - gun.last_shot < gun_data["cooldown"] or gun.ammo <= 0:
        return
        
    gun.last_shot = current_time
    gun.ammo -= 1

    dx, dy = player.dir
    
    # Calculate center position
    center_x = map_data_module.offset_x + player.pos[0] * map_data_module.TILE_SIZE + map_data_module.TILE_SIZE / 2
    center_y = map_data_module.offset_y + player.pos[1] * map_data_module.TILE_SIZE + map_data_module.TILE_SIZE / 2
    
    # Shift spawn to the "barrel" of the gun so it doesn't hide under the player block
    spawn_x = center_x + (dx * (map_data_module.TILE_SIZE / 1.5))
    spawn_y = center_y + (dy * (map_data_module.TILE_SIZE / 1.5))

    if gun.type == "shotgun":
        for i in range(-1, 2):
            perp_dx = -dy
            perp_dy = dx
            bullets.append({
                "x": spawn_x, "y": spawn_y,
                "dx": dx + i * 0.3 * perp_dx, "dy": dy + i * 0.3 * perp_dy,
                "speed": gun_data["bullet_speed"], "damage": gun_data["damage"],
                "max_range": gun_data["range"], "distance_traveled": 0,
                "owner": player
            })
    else:
        bullets.append({
            "x": spawn_x, "y": spawn_y,
            "dx": dx, "dy": dy,
            "speed": gun_data["bullet_speed"], "damage": gun_data["damage"],
            "max_range": gun_data["range"], "distance_traveled": 0,
            "owner": player
        })