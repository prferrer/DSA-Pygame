import pygame

# Function definition: takes the list of bullets, list of players, map data, and delta time (dt)
def update_bullets(bullets, players, map_data_module, dt):
    # Initialize a variable to track if a player was hit this frame; defaults to None
    hit_player = None  
    
    # Iterate over a *copy* of the bullets list (using [:]) so we can safely remove items from the original list during the loop
    for b in bullets[:]:
        
        # Calculate exactly how many pixels the bullet should move this frame based on its speed and the time passed (dt)
        distance_moved = float(b["speed"]) * float(dt)
        
        # Update the bullet's exact X pixel coordinate by multiplying its X direction vector by the distance
        b["x"] += b["dx"] * distance_moved
        # Update the bullet's exact Y pixel coordinate by multiplying its Y direction vector by the distance
        b["y"] += b["dy"] * distance_moved
        # Add the distance moved this frame to the total distance this specific bullet has traveled
        b["distance_traveled"] += distance_moved

        # --- 1. Range Exhaustion ---
        # Check if the bullet has traveled further than its weapon's maximum allowed range
        if b["distance_traveled"] >= b["max_range"]:
            # Double-check the bullet is still in the list to prevent ValueError, then remove it
            if b in bullets:
                bullets.remove(b)
            # Skip the rest of the loop for this bullet since it no longer exists
            continue

        # Convert the bullet's exact pixel X coordinate into a map grid column index
        grid_x = int((b["x"] - map_data_module.offset_x) // map_data_module.TILE_SIZE)
        # Convert the bullet's exact pixel Y coordinate into a map grid row index
        grid_y = int((b["y"] - map_data_module.offset_y) // map_data_module.TILE_SIZE)

        # --- 2. Wall/Bounds Collision ---
        # Check if the bullet is out of bounds on the left/right (grid_x) OR top/bottom (grid_y)
        # OR if the specific tile the bullet is currently over is a wall (value of 1 in map_grid)
        if (grid_x < 0 or grid_x >= map_data_module.MAP_COLS or 
            grid_y < 0 or grid_y >= map_data_module.MAP_ROWS or 
            map_data_module.map_grid[grid_y][grid_x] == 1):
            
            # If it hit a wall or went out of bounds, remove it from the game
            if b in bullets:
                bullets.remove(b)
            # Skip to the next bullet
            continue

        # --- 3. Player Collision ---
        # Loop through all players in the game (Player 1 and Player 2)
        for p in players:
            # Check to ensure the bullet cannot damage the person who fired it
            if p != b["owner"]:
                # Create a pygame.Rect representing the player's current physical hit box on the screen
                p_rect = pygame.Rect(
                    map_data_module.offset_x + p.pos[0] * map_data_module.TILE_SIZE,
                    map_data_module.offset_y + p.pos[1] * map_data_module.TILE_SIZE,
                    map_data_module.TILE_SIZE, map_data_module.TILE_SIZE
                )
                
                # Check if the bullet's current pixel coordinates (x, y) overlap with the player's hit box
                if p_rect.collidepoint(b["x"], b["y"]):
                    # Deduct the bullet's damage from the player's health points
                    p.hp -= b["damage"]
                    # Mark that this specific player was hit
                    hit_player = p  
                    # Remove the bullet from the game since it struck a target
                    if b in bullets:
                        bullets.remove(b)
                    # Break out of the player-checking loop since the bullet is destroyed
                    break
        
        # If a player was hit by this bullet, break the main bullet loop entirely.
        # This clears remaining checks this frame, preventing simultaneous/double damage bugs
        if hit_player:
            break

    # Return the player who was hit (if any) to main.py so it can handle respawns and resetting the round
    return hit_player