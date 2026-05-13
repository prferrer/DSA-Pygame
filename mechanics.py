import pygame
from guns import GUN_TYPES


def update_bullets(bullets, players, map_data_module, dt):
    """
    Move every bullet, check wall and player collisions.
    Handle explosive bullets (rockets) with area damage.

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
            # If explosive, trigger explosion at max range
            if b.get("is_explosive", False):
                hit_player, armor_absorbed = handle_explosion(
                    b, players, map_data_module, hit_player, armor_absorbed
                )
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
                # If explosive, trigger explosion at wall
                if b.get("is_explosive", False):
                    hit_player, armor_absorbed = handle_explosion(
                        b, players, map_data_module, hit_player, armor_absorbed
                    )
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
                # Determine how much damage this specific bullet does
                # We use .get() as a safety measure in case 'damage' isn't defined
                bullet_damage = b.get("damage", 1) 
                # If explosive, handle explosion damage
                if b.get("is_explosive", False):
                    hit_player, armor_absorbed = handle_explosion(
                        b, players, map_data_module, hit_player, armor_absorbed
                    )
                else:
                    # Regular bullet hit
                    # ── Armor Logic ──────────────────────────────────────────
                    if p.armor > 0:
                        # Armor absorbs damage first
                        p.armor -= bullet_damage
                        if p.armor <= 0:
                            # Armor broken, overflow damage goes to HP
                            p.hp += p.armor  # p.armor is negative here, so this reduces HP
                            p.armor = 0
                            if p.hp < 0:
                                p.hp = 0
                            armor_absorbed = False  # Armor broke, player respawns
                        else:
                            armor_absorbed = True  # Armor absorbed the hit
                    else:
                        # No armor: reduce HP by the weapon's specific damage value
                        p.hp -= bullet_damage
                        if p.hp < 0:
                            p.hp = 0
                        armor_absorbed = False

                    hit_player = p

                if b in bullets:
                    bullets.remove(b)
                break

    return hit_player, armor_absorbed


def handle_explosion(bullet, players, map_data_module, current_hit_player, current_armor_absorbed):
    """
    Handle explosion damage for rocket launcher.
    Damages all players within explosion_radius tiles of the impact point.
    
    Returns updated (hit_player, armor_absorbed) tuple.
    """
    explosion_radius = bullet.get("explosion_radius", 0)
    if explosion_radius <= 0:
        return current_hit_player, current_armor_absorbed
    
    # Convert bullet position to tile coordinates
    impact_tile_x = (bullet["x"] - map_data_module.offset_x) / map_data_module.TILE_SIZE
    impact_tile_y = (bullet["y"] - map_data_module.offset_y) / map_data_module.TILE_SIZE
    
    hit_player = current_hit_player
    armor_absorbed = current_armor_absorbed
    
    for p in players:
        if p == bullet["owner"]:
            continue
        
        # Calculate distance in tiles
        dx = p.pos[0] - impact_tile_x
        dy = p.pos[1] - impact_tile_y
        distance = (dx * dx + dy * dy) ** 0.5

        boomer_damage = bullet.get("damage", 50)

        if distance <= explosion_radius:
            # Apply explosion damage
            if p.armor > 0:
                # Armor absorbs damage first
                p.armor -= boomer_damage
                if p.armor <= 0:
                    # Armor broken, overflow damage goes to HP
                    p.hp += p.armor  # p.armor is negative here, so this reduces HP
                    p.armor = 0
                    if p.hp < 0:
                        p.hp = 0
                    armor_absorbed = False  # Armor broke, player respawns
                else:
                    armor_absorbed = True  # Armor absorbed the hit
            else:
                # No armor: reduce HP by explosion damage
                p.hp -= boomer_damage
                if p.hp < 0:
                    p.hp = 0
                armor_absorbed = False
            
            hit_player = p
    
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
