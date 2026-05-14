"""
Integration guide for rocket launcher retro diffusion animation.

Steps to integrate into main.py:

1. Import the animation module at the top of main.py:
   from rocket_animation import RocketDiffusionEffect, RocketProjectile, render_rocket, render_explosion

2. Initialize the animation effect after pygame.init():
   rocket_effect = RocketDiffusionEffect(size=32)

3. Create a separate rockets list to track rocket projectiles:
   rockets = []  # Add this alongside the bullets list

4. Modify the shoot() function in guns.py to use RocketProjectile for rockets:
   
   In the shoot() function, after line 118, add:
   
   if gun.type == "rocket_launcher":
       rocket = RocketProjectile(
           x=spawn_x, y=spawn_y,
           dx=dx, dy=dy,
           speed=gun_data["bullet_speed"],
           damage=gun_data["damage"],
           max_range=gun_data["range"],
           owner=player
       )
       rockets.append(rocket)
   else:
       # ... existing bullet code ...

5. In the main game loop, update rockets:
   
   for rocket in rockets[:]:
       rocket.update(dt)
       
       # Generate trail particles
       if random.random() < 0.3:
           rocket.generate_trail_particle()
       
       # Remove if out of range
       if rocket.is_out_of_range():
           rockets.remove(rocket)

6. In the rendering section, draw rockets:
   
   for rocket in rockets:
       render_rocket(screen, rocket, rocket_effect, TILE_SIZE, md.map_data)

7. Handle rocket collisions with players (update mechanics.py):
   
   Check rockets list in collision detection
   If rocket hits player and is_explosive, call render_explosion()
   Deal damage in explosion radius

Example collision handler:
   
   for rocket in rockets[:]:
       for player in [player1, player2]:
           dist = ((rocket.x - (md.map_data.offset_x + player.pos[0] * TILE_SIZE)) ** 2 +
                   (rocket.y - (md.map_data.offset_y + player.pos[1] * TILE_SIZE)) ** 2) ** 0.5
           
           if dist < rocket.explosion_radius * TILE_SIZE:
               # Trigger explosion
               render_explosion(screen, rocket.x, rocket.y, 
                              rocket.explosion_radius, TILE_SIZE)
               player.hp -= rocket.damage
               rockets.remove(rocket)
               break

CUSTOMIZATION OPTIONS:

- Adjust animation frame count in RocketDiffusionEffect.generate_frames():
  Change num_frames=8 to higher number for smoother animation
  
- Change explosion colors in render_explosion():
  Modify (255, 165, 0) to different RGB values
  
- Adjust trail particle behavior:
  Modify rocket.trail_particles generation in generate_trail_particle()
  
- Fine-tune diffusion effect:
  Edit _add_pixel_noise() for more/less pixelation
  Adjust ring count and alphas in generate_frames()
"""

# Quick integration example for main.py:
INTEGRATION_EXAMPLE = """
# At the top
from rocket_animation import RocketDiffusionEffect, RocketProjectile, render_rocket, render_explosion

# After pygame.init()
rocket_effect = RocketDiffusionEffect(size=32)
rockets = []

# In game loop, after bullet updates:
for rocket in rockets[:]:
    rocket.update(dt)
    if random.random() < 0.3:
        rocket.generate_trail_particle()
    if rocket.is_out_of_range():
        rockets.remove(rocket)

# In rendering, after draw_bullets:
for rocket in rockets:
    render_rocket(screen, rocket, rocket_effect, TILE_SIZE, md.map_data)
"""
