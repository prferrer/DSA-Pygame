# Imports Python's built-in random module to help generate random map coordinates for gun spawns.
import random
# Imports the Pygame library, which handles rendering images, transformations, and game loops.
import pygame
# Imports your local map_data module so the gun system can check grid layouts and tile sizes.
import map_data

#slop ni clarence

# A dictionary defining the core stats and asset paths for every gun type in the game.
GUN_TYPES = {
    # Pistol: Low ammo, moderate speed, quick cooldown, low damage.
    "pistol": {"ammo": 8, "bullet_speed": 300, "cooldown": 400, "damage": 1, "range": 300, "duration": 15000, "path": "assets/guns/Glock18c-PxNBG.png", "map_scale": 0.8, "equip_scale": 0.5},
    # Rifle: High ammo, high bullet speed, very fast firing rate (low cooldown), moderate damage.
    "rifle": {"ammo": 20, "bullet_speed": 500, "cooldown": 120, "damage": 1.5, "range": 600, "duration": 15000, "path": "assets/guns/M4A1-Px-PxNBG.png", "map_scale": 0.6, "equip_scale": 0.4},
    # Shotgun: Low ammo, slow bullet speed, slow firing rate, fires multiple bullets with spread (defined in shoot function).
    "shotgun": {"ammo": 5, "bullet_speed": 200, "cooldown": 800, "damage": 0.7, "spread": 0.1, "range": 150, "duration": 15000, "path": "assets/guns/Rem870-Px-PxNBG.png", "map_scale": 0.6, "equip_scale": 0.4}
}

# Defines the global respawn cooldowns (in milliseconds) for each gun type after they are depleted or dropped.
GUN_COOLDOWNS = {
    "pistol": 400,
    "rifle": 400,
    "shotgun": 400
}

# A dictionary tracking the exact timestamp (in milliseconds) when each gun was last dropped or emptied.
gun_last_used = {"pistol": 0, "rifle": 0, "shotgun":0}

# A function that scales the original high-resolution gun images to fit the map's current tile size.
def scale_gun_images(tile_size):
    # Iterates through the values (dictionaries) of every gun defined in GUN_TYPES.
    for gun in GUN_TYPES.values():
        # A try-except block to gracefully handle missing image files.
        try:
            # Loads the image from the specified path and converts it to support alpha (transparency).
            img = pygame.image.load(gun["path"]).convert_alpha()
            # Calculates the image's aspect ratio to ensure scaling doesn't stretch or squish the gun.
            aspect_ratio = img.get_width() / img.get_height()
            
            # Sets the base bounding box based on the current tile size.
            base_height = tile_size
            base_width = int(tile_size * aspect_ratio)

            # Calculates the dimensions for when the gun is lying on the floor (map version).
            map_w = int(base_width * gun.get("map_scale", 1.0))
            map_h = int(base_height * gun.get("map_scale", 1.0))
            # Stores the scaled-down map image back into the GUN_TYPES dictionary.
            gun["map_image"] = pygame.transform.scale(img, (map_w, map_h))

            # Calculates the dimensions for when the gun is actively held by a player (equipped version).
            equip_w = int(base_width * gun.get("equip_scale", 1.0))
            equip_h = int(base_height * gun.get("equip_scale", 1.0))
            # Stores the scaled-down equipped image back into the GUN_TYPES dictionary.
            gun["equipped_image"] = pygame.transform.scale(img, (equip_w, equip_h))

        # Triggers if the image file isn't found or Pygame fails to load it.
        except (FileNotFoundError, pygame.error):
            # Creates a grey square placeholder for the map image to prevent the game from crashing.
            gun["map_image"] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            gun["map_image"].fill((100, 100, 100))
            # Creates a grey square placeholder for the equipped image.
            gun["equipped_image"] = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            gun["equipped_image"].fill((100, 100, 100))

# A class representing the current active gun entity in the game map.
class GunSystem:
    # Initializes default properties for the gun when the class is instantiated.
    def __init__(self):
        self.pos = None         # [x, y] coordinates when dropped on the map.
        self.owner = None       # Reference to the Player object holding the gun.
        self.type = None        # String indicating if it's a "pistol", "rifle", etc.
        self.ammo = 0           # Current ammo count.
        self.last_shot = 0      # Timestamp of the last time it was fired (for firing rate).
        self.pickup_time = 0    # Timestamp of when it was picked up (for duration tracking).
        self.duration = 0       # How long the gun lasts in a player's hands before disappearing.

##================= GUN SPAWN ALGO =================}

# The method takes 'map_data_module' to read the grid layout and 'current_time' to calculate cooldowns.
def spawn(self, map_data_module, current_time=0):
    
    # 1. DETERMINE ELIGIBLE GUNS
    # This is a Python list comprehension. It iterates through every gun type defined in the GUN_TYPES dictionary.
    # It checks the global 'gun_last_used' timestamp against the 'current_time'.
    # If the time passed is greater than or equal to the gun's mandatory cooldown, it gets added to the 'available' list.
    available = [
        t for t in GUN_TYPES
        if current_time - gun_last_used[t] >= GUN_COOLDOWNS[t]
    ]
    
    # 2. ABORT IF ALL ON COOLDOWN
    # If the 'available' list is completely empty, it means no guns are ready to spawn yet.
    # We return False to exit the function early and avoid errors.
    if not available:
        return False
    
    # 3. START COORDINATE SEARCH
    # We open a 'while True' loop. This creates an infinite loop that will keep guessing 
    # locations until it finds a valid spot, at which point we will force it to 'break'.
    while True:
        
        # 4. GUESS RANDOM X & Y
        # We use Python's random module to pick an X (column) index. 
        # It guesses a number from 0 up to the maximum number of columns on the map (minus 1 for zero-indexing).
        x = random.randint(0, map_data_module.MAP_COLS - 1)
        # We do the exact same thing to guess a Y (row) index.
        y = random.randint(0, map_data_module.MAP_ROWS - 1)
        
        # 5. CHECK GRID FOR EMPTY SPACE
        # We look up the guessed [y][x] coordinates in the map's 2D array ('map_grid').
        # If the integer at that location is '0', it represents a blank floor tile (meaning no walls).
        if map_data_module.map_grid[y][x] == 0:
            
            # 6. SET GUN POSITION
            # Because we confirmed the tile is empty, we update this gun object's internal position to these coordinates.
            self.pos = [x, y]
            
            # 7. ASSIGN RANDOM GUN TYPE
            # We use 'random.choice' to randomly pull one of the eligible gun types from the 'available' list 
            # we generated at the very beginning of the function.
            self.type = random.choice(available)
            
            # 8. STOP SEARCHING
            # We have successfully found a valid tile and assigned the gun data. 
            # We trigger 'break' to immediately kill the infinite 'while True' loop.
            break


##================= GUN PICKUP LOGIC =================}
    # Handles the logic for when a player steps on the gun to equip it.
    def pickup(self, player, current_time):
        # Fetches the base stats for this specific gun type.
        gun_data = GUN_TYPES[self.type]
        # Assigns the gun's owner to the player who picked it up.
        self.owner = player
        # Loads the gun with its designated starting ammo.
        self.ammo = gun_data["ammo"]
        # Records the time it was picked up to start the duration timer.
        self.pickup_time = current_time
        # Sets the lifespan of the gun (defaults to 15000ms / 15 seconds if missing).
        self.duration = gun_data.get("duration", 15000)
        # Removes the gun from the floor since it is now equipped.
        self.pos = None

# A standalone function to handle generating bullets when a player attempts to shoot.
def shoot(gun, player, bullets, current_time, map_data_module):
    # Failsafe: Ensures a player cannot shoot a gun they don't currently own.
    if gun.owner != player:
        return
    
    # Checks if the gun has exceeded its maximum hold duration (e.g., 15 seconds).
    if gun.pickup_time and (current_time - gun.pickup_time >= gun.duration):
        # Unassigns the owner, essentially forcing the player to drop it.
        gun.owner = None
        gun.pickup_time = None
        return
    
    # Retrieves the specific stats for the gun currently being fired.
    gun_data = GUN_TYPES[gun.type]
    
    # Prevents firing if the gun is still on cooldown (firing rate limit) or if it's out of ammo.
    if current_time - gun.last_shot < gun_data["cooldown"] or gun.ammo <= 0:
        return
        
    # Updates the last shot timestamp to enforce the cooldown for the next shot.
    gun.last_shot = current_time
    # Deducts one bullet from the active ammo pool.
    gun.ammo -= 1

    # Grabs the player's current facing direction (e.g., [1, 0] for right, [0, -1] for up).
    dx, dy = player.dir
    
    # Calculates the exact pixel X coordinate of the player's center.
    center_x = map_data_module.offset_x + player.pos[0] * map_data_module.TILE_SIZE + map_data_module.TILE_SIZE / 2
    # Calculates the exact pixel Y coordinate of the player's center.
    center_y = map_data_module.offset_y + player.pos[1] * map_data_module.TILE_SIZE + map_data_module.TILE_SIZE / 2
    
    # Shifts the bullet spawn point outwards in the direction the player is facing (acting as a "barrel").
    # This prevents the bullet from spawning directly inside the player and instantly colliding.
    spawn_x = center_x + (dx * (map_data_module.TILE_SIZE / 1.5))
    spawn_y = center_y + (dy * (map_data_module.TILE_SIZE / 1.5))

    # Special firing logic for the shotgun, which fires a spread of pellets.
    if gun.type == "shotgun":
        # Loops 3 times (-1, 0, 1) to create left, center, and right spread bullets.
        for i in range(-1, 2):
            # Calculates the perpendicular vector (90 degrees) to the player's aiming direction.
            perp_dx = -dy
            perp_dy = dx
            # Appends a new dictionary representing a shotgun pellet into the global bullets list.
            bullets.append({
                "x": spawn_x, "y": spawn_y,
                # Mixes the forward vector (dx) with a fraction of the perpendicular vector (perp_dx) based on 'i'.
                "dx": dx + i * 0.3 * perp_dx, "dy": dy + i * 0.3 * perp_dy,
                "speed": gun_data["bullet_speed"], "damage": gun_data["damage"],
                "max_range": gun_data["range"], "distance_traveled": 0,
                "owner": player # Identifies the shooter to prevent self-damage.
            })
    # Standard firing logic for single-projectile weapons like pistols and rifles.
    else:
        # Appends a single dictionary representing a standard bullet into the global bullets list.
        bullets.append({
            "x": spawn_x, "y": spawn_y,
            "dx": dx, "dy": dy, # Travels straight in the exact direction the player is facing.
            "speed": gun_data["bullet_speed"], "damage": gun_data["damage"],
            "max_range": gun_data["range"], "distance_traveled": 0,
            "owner": player # Identifies the shooter to prevent self-damage.
        })