import pygame
from guns import GUN_TYPES


def update_bullets(bullets, players, map_data_module, dt):
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
                # Check if this is a NEW wall tile (not the same one as last frame)
                is_new_wall = (grid_x != b.get("last_grid_x", -1) or grid_y != b.get("last_grid_y", -1))
                
                # Wall hit - check if bullet can penetrate
                if b.get("can_penetrate", False) and b.get("walls_penetrated", 0) < b.get("max_wall_penetration", 0):
                    # Only increment wall count if this is a new wall tile
                    if is_new_wall:
                        b["walls_penetrated"] += 1
                        # Reduce damage by 20% of ORIGINAL damage per wall
                        damage_reduction = b["original_damage"] * 0.2
                        b["damage"] = b["original_damage"] - (damage_reduction * b["walls_penetrated"])
                    
                    # Update last grid position
                    b["last_grid_x"] = grid_x
                    b["last_grid_y"] = grid_y
                    # Continue bullet flight - don't remove it
                else:
                    # Regular bullet or max penetration reached - destroy bullet
                    if b.get("is_explosive", False):
                        hit_player, armor_absorbed = handle_explosion(
                            b, players, map_data_module, hit_player, armor_absorbed
                        )
                    if b in bullets:
                        bullets.remove(b)
                    continue
            else:
                # Not in a wall - update grid position tracking
                b["last_grid_x"] = grid_x
                b["last_grid_y"] = grid_y
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
                    # New system: each armor has 33.33 HP
                    ARMOR_HP_PER_UNIT = 33.33
                    
                    if p.armor > 0:
                        # Armor absorbs damage first
                        p.armor_hp -= bullet_damage
                        
                        # Check if armor units need to be reduced
                        while p.armor_hp < 0 and p.armor > 0:
                            p.armor -= 1
                            if p.armor > 0:
                                p.armor_hp += ARMOR_HP_PER_UNIT
                            else:
                                # All armor broken, overflow damage goes to HP
                                p.hp += p.armor_hp  # armor_hp is negative, so this reduces HP
                                p.armor_hp = 0
                        
                        # Cap armor_hp to current armor max
                        if p.armor > 0:
                            max_armor_hp = p.armor * ARMOR_HP_PER_UNIT
                            if p.armor_hp > max_armor_hp:
                                p.armor_hp = max_armor_hp
                        
                        if p.hp < 0:
                            p.hp = 0
                        
                        # Player respawns if all armor AND hp are depleted
                        armor_absorbed = (p.hp > 0)
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
            # New system: each armor has 33.33 HP
            ARMOR_HP_PER_UNIT = 33.33
            
            if p.armor > 0:
                # Armor absorbs damage first
                p.armor_hp -= boomer_damage
                
                # Check if armor units need to be reduced
                while p.armor_hp < 0 and p.armor > 0:
                    p.armor -= 1
                    if p.armor > 0:
                        p.armor_hp += ARMOR_HP_PER_UNIT
                    else:
                        # All armor broken, overflow damage goes to HP
                        p.hp += p.armor_hp  # armor_hp is negative, so this reduces HP
                        p.armor_hp = 0
                
                # Cap armor_hp to current armor max
                if p.armor > 0:
                    max_armor_hp = p.armor * ARMOR_HP_PER_UNIT
                    if p.armor_hp > max_armor_hp:
                        p.armor_hp = max_armor_hp
                
                if p.hp < 0:
                    p.hp = 0
                
                # Player respawns if all armor AND hp are depleted
                armor_absorbed = (p.hp > 0)
            else:
                # No armor: reduce HP by explosion damage
                p.hp -= boomer_damage
                if p.hp < 0:
                    p.hp = 0
                armor_absorbed = False
            
            hit_player = p
    
    return hit_player, armor_absorbed


def try_melee(attacker, defender, current_time, active_animations, map_data_module):
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
