import random
import pygame
import map_data

#slop ni clarence

GUN_TYPES = {
    "pistol": {"ammo": 8, "bullet_speed": 300, "cooldown": 400, "damage": 1, "range": 300, "duration": 15000, "path": "assets/guns/Glock18c-PxNBG.png", "map_scale": 0.8, "equip_scale": 0.5},
    "rifle": {"ammo": 20, "bullet_speed": 500, "cooldown": 120, "damage": 1.5, "range": 600, "duration": 15000, "path": "assets/guns/M4A1-Px-PxNBG.png", "map_scale": 0.6, "equip_scale": 0.4},
    "shotgun": {"ammo": 5, "bullet_speed": 200, "cooldown": 800, "damage": 0.7, "spread": 8, "range": 150, "duration": 15000, "path": "assets/guns/Rem870-Px-PxNBG.png", "map_scale": 0.6, "equip_scale": 0.4}
}

GUN_COOLDOWNS = {
    "pistol": 400,
    "rifle": 15000,
    "shotgun": 12000
}
gun_last_used = {"pistol": 0, "rifle": 0, "shotgun":0}

def scale_gun_images(tile_size):
    for gun in GUN_TYPES.values():
        try:
            img = pygame.image.load(gun["path"]).convert_alpha()
            # Calculate aspect ratio to prevent squishing
            aspect_ratio = img.get_width() / img.get_height()
            
            # Base the height on the tile_size, and scale the width to match
            base_height = tile_size
            base_width = int(tile_size * aspect_ratio)

            # Create the Map version
            map_w = int(base_width * gun.get("map_scale", 1.0))
            map_h = int(base_height * gun.get("map_scale", 1.0))
            gun["map_image"] = pygame.transform.scale(img, (map_w, map_h))

            # Create the Equipped version
            equip_w = int(base_width * gun.get("equip_scale", 1.0))
            equip_h = int(base_height * gun.get("equip_scale", 1.0))
            gun["equipped_image"] = pygame.transform.scale(img, (equip_w, equip_h))

        except (FileNotFoundError, pygame.error):
            # Fallback surfaces if images are missing
            gun["map_image"] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            gun["map_image"].fill((100, 100, 100))
            gun["equipped_image"] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            gun["equipped_image"].fill((100, 100, 100))

class GunSystem:
    def __init__(self):
        self.pos = None
        self.owner = None
        self.type = None
        self.ammo = 0
        self.last_shot = 0
        self.pickup_time = 0
        self.duration = 0

    def spawn(self, map_data_module, current_time=0):
        available = [
            t for t in GUN_TYPES
            if current_time - gun_last_used[t] >= GUN_COOLDOWNS[t]
        ]
        if not available:
            return False
        
        while True:
            x = random.randint(0, map_data_module.MAP_COLS - 1)
            y = random.randint(0, map_data_module.MAP_ROWS - 1)
            if map_data_module.map_grid[y][x] == 0:
                self.pos = [x, y]
                self.type = random.choice(available)
                break

    def pickup(self, player, current_time):
        gun_data = GUN_TYPES[self.type]
        self.owner = player
        self.ammo = gun_data["ammo"]
        self.pickup_time = current_time
        self.duration = gun_data.get("duration", 15000)
        self.pos = None

def shoot(gun, player, bullets, current_time, map_data_module):
    if gun.owner != player:
        return
    
    if gun.pickup_time and (current_time - gun.pickup_time >= gun.duration):
        gun.owner = None
        gun.pickup_time = None
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
