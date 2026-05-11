import pygame

def update_bullets(bullets, players, map_data_module, dt):
    """
    Move every bullet, check wall and player collisions.

    Returns a tuple  (hit_player, armor_absorbed)
      hit_player    – the Player instance that was hit, or None
      armor_absorbed – True if the hit was soaked by armor (player does NOT respawn)
    """
    hit_player     = None
    armor_absorbed = False

    for b in bullets[:]:
        distance_moved = float(b["speed"]) * float(dt)
        b["x"] += b["dx"] * distance_moved
        b["y"] += b["dy"] * distance_moved
        b["distance_traveled"] += distance_moved

        # ── Range check ───────────────────────────────────────────────
        if b["distance_traveled"] >= b["max_range"]:
            if b in bullets:
                bullets.remove(b)
            continue

        # ── Wall collision ────────────────────────────────────────────
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

        # ── Player collision ──────────────────────────────────────────
        bullet_rect = pygame.Rect(int(b["x"]) - 4, int(b["y"]) - 4, 8, 8)

        for p in players:
            if p == b["owner"]:
                continue

            player_rect = pygame.Rect(
                int(map_data_module.offset_x + p.pos[0] * map_data_module.TILE_SIZE),
                int(map_data_module.offset_y + p.pos[1] * map_data_module.TILE_SIZE),
                map_data_module.TILE_SIZE,
                map_data_module.TILE_SIZE,
            )

            if bullet_rect.colliderect(player_rect):
                # ── Armor absorbs the hit ──────────────────────────
                if p.armor > 0:
                    p.armor        -= 1
                    armor_absorbed  = True
                    # bullet is consumed but the player keeps their position
                else:
                    p.hp -= 1
                    if p.hp < 0:
                        p.hp = 0
                    armor_absorbed = False

                hit_player = p

                if b in bullets:
                    bullets.remove(b)
                break

    return hit_player, armor_absorbed


def try_melee(attacker, defender, current_time, active_animations, map_data_module):
    """
    Attempt a melee strike from `attacker` toward `defender`.

    Rules
    -----
    • Attacker must NOT own a gun (checked in main before calling).
    • Attacker must have waited MELEE_COOLDOWN ms since last swing.
    • Defender must be standing on the tile directly in front of attacker.
    • On success: defender is stunned for MELEE_STUN_DURATION ms.
    • A hit-spark animation entry is added to active_animations.

    Returns True if a hit landed, False otherwise.
    """
    from config import MELEE_COOLDOWN, MELEE_STUN_DURATION, MELEE_ANIM_DURATION

    # Cooldown gate
    if current_time - attacker.last_melee < MELEE_COOLDOWN:
        return False

    attacker.last_melee = current_time

    # Check adjacency: target tile in facing direction
    target_x = attacker.pos[0] + attacker.dir[0]
    target_y = attacker.pos[1] + attacker.dir[1]

    if [target_x, target_y] != defender.pos:
        return False

    # Apply stun
    defender.stunned_until = current_time + MELEE_STUN_DURATION

    # Register animation at the target tile's pixel centre
    anim_cx = (map_data_module.offset_x
               + target_x * map_data_module.TILE_SIZE
               + map_data_module.TILE_SIZE // 2)
    anim_cy = (map_data_module.offset_y
               + target_y * map_data_module.TILE_SIZE
               + map_data_module.TILE_SIZE // 2)

    active_animations.append({
        "cx":        anim_cx,
        "cy":        anim_cy,
        "start":     current_time,
        "duration":  MELEE_ANIM_DURATION,
        "frame":     0,
    })

    return True