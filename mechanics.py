import pygame

def update_bullets(bullets, players, map_data_module, dt):
    hit_occurred = False
    
    for b in bullets[:]:
        # Force float multiplication for smooth pixel movement
        distance_moved = float(b["speed"]) * float(dt)
        b["x"] += b["dx"] * distance_moved
        b["y"] += b["dy"] * distance_moved
        b["distance_traveled"] += distance_moved

        # 1. Range Exhaustion
        if b["distance_traveled"] >= b["max_range"]:
            if b in bullets:
                bullets.remove(b)
            continue

        grid_x = int((b["x"] - map_data_module.offset_x) // map_data_module.TILE_SIZE)
        grid_y = int((b["y"] - map_data_module.offset_y) // map_data_module.TILE_SIZE)

        # 2. Wall/Bounds Collision
        if (grid_x < 0 or grid_x >= map_data_module.MAP_COLS or 
            grid_y < 0 or grid_y >= map_data_module.MAP_ROWS or 
            map_data_module.map_grid[grid_y][grid_x] == 1):
            if b in bullets:
                bullets.remove(b)
            continue

        # 3. Player Collision
        for p in players:
            if p != b["owner"]:
                p_rect = pygame.Rect(
                    map_data_module.offset_x + p.pos[0] * map_data_module.TILE_SIZE,
                    map_data_module.offset_y + p.pos[1] * map_data_module.TILE_SIZE,
                    map_data_module.TILE_SIZE, map_data_module.TILE_SIZE
                )
                if p_rect.collidepoint(b["x"], b["y"]):
                    p.hp -= b["damage"]
                    hit_occurred = True
                    if b in bullets:
                        bullets.remove(b)
                    break
        
        # Stop processing other bullets this frame to avoid simultaneous damage bugs
        if hit_occurred:
            break

    return hit_occurred