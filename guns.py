import random
import pygame
import map_data

GUN_TYPES = {
    "pistol":  {
        "ammo": 8,  "bullet_speed": 300, "cooldown": 400,
        "damage": 1,   "range": 300, "duration": 15000,
        "path": "assets/guns/Glock18c-PxNBG.png",
        "map_scale": 0.8, "equip_scale": 0.5,
    },
    "rifle":   {
        "ammo": 20, "bullet_speed": 500, "cooldown": 120,
        "damage": 1.5, "range": 600, "duration": 15000,
        "path": "assets/guns/M4A1-Px-PxNBG.png",
        "map_scale": 0.6, "equip_scale": 0.4,
    },
    "shotgun": {
        "ammo": 5,  "bullet_speed": 200, "cooldown": 800,
        "damage": 0.7, "spread": 8, "range": 150, "duration": 15000,
        "path": "assets/guns/Rem870-Px-PxNBG.png",
        "map_scale": 0.5, "equip_scale": 0.4,
    },
    "smg": {
        "ammo": 30, "bullet_speed": 400, "cooldown": 80,
        "damage": 0.8, "range": 400, "duration": 12000,
        "path": "assets/guns/MP7-PxNBG.png",
        "map_scale": 0.7, "equip_scale": 0.6,
    },
    "sniper": {
        "ammo": 5, "bullet_speed": 800, "cooldown": 1500,
        "damage": 3.0, "range": 1000, "duration": 15000,
        "path": "assets/guns/M82A1-PxNBG.png",
        "map_scale": 0.5, "equip_scale": 0.4,
    },
    "rocket_launcher": {
        "ammo": 3, "bullet_speed": 250, "cooldown": 2000,
        "damage": 2.5, "range": 500, "duration": 15000,
        "explosion_radius": 3, "is_explosive": True,
        "path": "assets/guns/AT4-PxNBG.png",
        "map_scale": 0.55, "equip_scale": 0.38,
    },
}

# Per-type respawn cooldowns (ms) – how long after a gun of this type
# was last used before it may spawn again.
GUN_COOLDOWNS = {
    "pistol":  400,
    "rifle":   15000,
    "shotgun": 12000,
    "smg":     10000,
    "sniper":  20000,
    "rocket_launcher": 25000,
}
gun_last_used = {"pistol": 0, "rifle": 0, "shotgun": 0, "smg": 0, "sniper": 0, "rocket_launcher": 0}


# ── Image loading ─────────────────────────────────────────────────────────────

def scale_gun_images(tile_size):
    for gun in GUN_TYPES.values():
        try:
            img          = pygame.image.load(gun["path"]).convert_alpha()
            aspect_ratio = img.get_width() / img.get_height()
            base_h       = tile_size
            base_w       = int(tile_size * aspect_ratio)

            map_w = int(base_w * gun.get("map_scale",   1.0))
            map_h = int(base_h * gun.get("map_scale",   1.0))
            gun["map_image"] = pygame.transform.scale(img, (map_w, map_h))

            eq_w = int(base_w * gun.get("equip_scale", 1.0))
            eq_h = int(base_h * gun.get("equip_scale", 1.0))
            gun["equipped_image"] = pygame.transform.scale(img, (eq_w, eq_h))

        except (FileNotFoundError, pygame.error):
            fb = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            fb.fill((100, 100, 100))
            gun["map_image"]      = fb
            gun["equipped_image"] = fb


# ── GunSystem ─────────────────────────────────────────────────────────────────

class GunSystem:
    """Represents a single gun pickup / equipped weapon."""

    def __init__(self):
        self.pos         = None
        self.owner       = None
        self.type        = None
        self.ammo        = 0
        self.last_shot   = 0
        self.pickup_time = 0
        self.duration    = 0

    def spawn(self, map_data_module, current_time=0, occupied_positions=None):
        """
        Try to place this gun on the map.
        `occupied_positions` is a list of [x,y] lists that must be avoided
        (used so the two guns don't spawn on the same tile).

        Returns True on success, False if no valid gun type is available.
        """
        occupied_positions = occupied_positions or []

        available = [
            t for t in GUN_TYPES
            if current_time - gun_last_used[t] >= GUN_COOLDOWNS[t]
        ]
        if not available:
            return False

        # Try up to 100 random positions to find a free floor tile
        for _ in range(100):
            x = random.randint(0, map_data_module.MAP_COLS - 1)
            y = random.randint(0, map_data_module.MAP_ROWS - 1)
            if map_data_module.map_grid[y][x] != 0:
                continue
            if any([x, y] == op for op in occupied_positions):
                continue
            self.pos  = [x, y]
            self.type = random.choice(available)
            return True

        return False

    def pickup(self, player, current_time):
        gun_data         = GUN_TYPES[self.type]
        self.owner       = player
        self.ammo        = gun_data["ammo"]
        self.pickup_time = current_time
        self.duration    = gun_data.get("duration", 15000)
        self.pos         = None

    def drop(self, current_time):
        """Release ownership without respawning; caller handles respawn timer."""
        gun_last_used[self.type] = current_time
        self.owner       = None
        self.pickup_time = None


# ── Shooting ──────────────────────────────────────────────────────────────────

def shoot(gun, player, bullets, current_time, map_data_module):
    if gun.owner != player:
        return

    if gun.pickup_time and (current_time - gun.pickup_time >= gun.duration):
        gun.drop(current_time)
        return

    gun_data = GUN_TYPES[gun.type]
    if current_time - gun.last_shot < gun_data["cooldown"] or gun.ammo <= 0:
        return

    gun.last_shot  = current_time
    gun.ammo      -= 1

    dx, dy = player.dir

    center_x = (map_data_module.offset_x
                + player.pos[0] * map_data_module.TILE_SIZE
                + map_data_module.TILE_SIZE / 2)
    center_y = (map_data_module.offset_y
                + player.pos[1] * map_data_module.TILE_SIZE
                + map_data_module.TILE_SIZE / 2)

    spawn_x = center_x + dx * (map_data_module.TILE_SIZE / 1.5)
    spawn_y = center_y + dy * (map_data_module.TILE_SIZE / 1.5)

    base_bullet = {
        "x": spawn_x, "y": spawn_y,
        "dx": dx, "dy": dy,
        "speed": gun_data["bullet_speed"],
        "damage": gun_data["damage"],
        "max_range": gun_data["range"],
        "distance_traveled": 0,
        "owner": player,
        "is_explosive": gun_data.get("is_explosive", False),
        "explosion_radius": gun_data.get("explosion_radius", 0),
    }

    if gun.type == "shotgun":
        perp_dx = -dy
        perp_dy =  dx
        for i in range(-1, 2):
            b = dict(base_bullet)
            b["dx"] = dx + i * 0.3 * perp_dx
            b["dy"] = dy + i * 0.3 * perp_dy
            bullets.append(b)
    else:
        bullets.append(base_bullet)


# ── Armor pickup ──────────────────────────────────────────────────────────────

class ArmorPickup:
    """
    A single armor-pickup token that sits on the map until collected or despawned.
    """

    def __init__(self):
        self.pos          = None   # [x, y] tile or None
        self.spawn_time   = 0      # when it appeared
        self.despawn_time = 0      # when it should vanish

    def spawn(self, map_data_module, current_time, occupied_positions=None):
        """
        Place the armor token on a random free floor tile.
        `occupied_positions` – list of [x,y] to avoid (guns, other items).
        Returns True on success.
        """
        from config import ARMOR_DESPAWN_TIME
        occupied_positions = occupied_positions or []

        for _ in range(100):
            x = random.randint(0, map_data_module.MAP_COLS - 1)
            y = random.randint(0, map_data_module.MAP_ROWS - 1)
            if map_data_module.map_grid[y][x] != 0:
                continue
            if any([x, y] == op for op in occupied_positions):
                continue
            self.pos          = [x, y]
            self.spawn_time   = current_time
            self.despawn_time = current_time + ARMOR_DESPAWN_TIME
            return True

        return False

    def clear(self):
        self.pos = None
