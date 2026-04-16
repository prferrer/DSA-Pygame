import pygame

def update_bullets(bullets, players, map_data_module, dt):
    hit_player = None

    for b in bullets[:]:
        distance_moved = float(b["speed"]) * float(dt)
        b["x"] += b["dx"] * distance_moved
        b["y"] += b["dy"] * distance_moved
        b["distance_traveled"] += distance_moved

        # Remove bullet if max range reached
        if b["distance_traveled"] >= b["max_range"]:
            if b in bullets:
                bullets.remove(b)
            continue

        # Wall collision
        grid_x = int((b["x"] - map_data_module.offset_x) // map_data_module.TILE_SIZE)
        grid_y = int((b["y"] - map_data_module.offset_y) // map_data_module.TILE_SIZE)

        if (
            0 <= grid_y < len(map_data_module.map_grid)
            and 0 <= grid_x < len(map_data_module.map_grid[0])
        ):
            if map_data_module.map_grid[grid_y][grid_x] == 1:
                if b in bullets:
                    bullets.remove(b)
                continue
        else:
            if b in bullets:
                bullets.remove(b)
            continue

        # Player collision
        bullet_rect = pygame.Rect(int(b["x"]) - 4, int(b["y"]) - 4, 8, 8)

        for p in players:
            if p != b["owner"]:
                player_rect = pygame.Rect(
                    int(map_data_module.offset_x + p.pos[0] * map_data_module.TILE_SIZE),
                    int(map_data_module.offset_y + p.pos[1] * map_data_module.TILE_SIZE),
                    map_data_module.TILE_SIZE,
                    map_data_module.TILE_SIZE
                )

                if bullet_rect.colliderect(player_rect):
                    p.hp -= 1
                    if p.hp < 0:
                        p.hp = 0

                    hit_player = p

                    if b in bullets:
                        bullets.remove(b)

                    break

    return hit_player