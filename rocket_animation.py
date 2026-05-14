"""
Retro diffusion animation system for rocket launcher projectiles.
Creates pixel-art style diffusion effects using Pygame surface manipulation.
"""

import pygame
import random
import math

class RocketDiffusionEffect:
    """Generates retro diffusion animation frames for rocket projectiles."""
    
    def __init__(self, size=32):
        """
        Initialize the diffusion effect generator.
        
        Args:
            size: Base size of the effect in pixels
        """
        self.size = size
        self.frames = []
        self.generate_frames()
    
    def generate_frames(self, num_frames=8):
        """
        Generate retro diffusion animation frames.
        Uses expanding circles with noise for a classic 80s/90s look.
        
        Args:
            num_frames: Number of animation frames to generate
        """
        self.frames = []
        base_color = (255, 165, 0)  # Orange/yellow for rockets
        
        for frame_idx in range(num_frames):
            frame_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            progress = frame_idx / num_frames
            
            # Create expanding circle rings
            for ring in range(1, int(4 * progress) + 1):
                radius = (self.size // 2) * (ring / 3.0)
                alpha = int(255 * (1 - (ring / 3.0)))
                
                if alpha > 0:
                    color = (*base_color, alpha)
                    center = self.size * 1.5
                    pygame.draw.circle(
                        frame_surf, 
                        color, 
                        (int(center), int(center)), 
                        int(radius),
                        width=max(1, int(self.size * 0.1))
                    )
            
            # Add pixelated noise for retro effect
            self._add_pixel_noise(frame_surf, progress)
            self.frames.append(frame_surf)
    
    def _add_pixel_noise(self, surface, progress):
        """
        Add retro pixel noise to the surface.
        
        Args:
            surface: Pygame surface to modify
            progress: Animation progress (0.0 to 1.0)
        """
        noise_intensity = int(255 * progress * 0.6)
        if noise_intensity > 0:
            pixel_array = pygame.surfarray.array3d(surface)
            
            # Add random noise at intervals for pixel-art aesthetic
            for _ in range(int(20 * progress)):
                x = random.randint(0, surface.get_width() - 1)
                y = random.randint(0, surface.get_height() - 1)
                
                if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
                    pygame.draw.circle(surface, (255, 200, 0, noise_intensity), (x, y), 1)
    
    def get_frame(self, frame_index):
        """
        Get a specific animation frame.
        
        Args:
            frame_index: Index of the frame to retrieve
            
        Returns:
            Pygame surface of the requested frame
        """
        if not self.frames:
            return pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        idx = frame_index % len(self.frames)
        return self.frames[idx]
    
    def get_frame_count(self):
        """Return total number of animation frames."""
        return len(self.frames)


class RocketProjectile:
    """Enhanced rocket projectile with diffusion animation."""
    
    def __init__(self, x, y, dx, dy, speed, damage, max_range, owner):
        """
        Initialize a rocket projectile.
        
        Args:
            x, y: Starting position
            dx, dy: Direction vector
            speed: Movement speed
            damage: Damage dealt on impact
            max_range: Maximum travel distance
            owner: Player that fired the rocket
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.max_range = max_range
        self.distance_traveled = 0
        self.owner = owner
        
        # Animation properties
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_duration = 50  # ms per frame
        
        # Rocket-specific properties
        self.is_explosive = True
        self.explosion_radius = 3
        self.trail_particles = []
    
    def update(self, dt):
        """
        Update projectile position and animation.
        
        Args:
            dt: Delta time since last update (in seconds)
        """
        # Update position
        pixels_moved = self.speed * dt * 1000  # Convert to pixels
        self.x += self.dx * pixels_moved
        self.y += self.dy * pixels_moved
        self.distance_traveled += pixels_moved
        
        # Update animation
        self.frame_timer += dt * 1000
        if self.frame_timer >= self.frame_duration:
            self.frame_index += 1
            self.frame_timer = 0
    
    def generate_trail_particle(self):
        """Generate a particle for the rocket's trail."""
        particle = {
            "x": self.x,
            "y": self.y,
            "vx": random.uniform(-0.5, 0.5),
            "vy": random.uniform(-0.5, 0.5),
            "life": random.uniform(200, 400),  # ms
            "max_life": 300,
            "color": (255, 165, 0, 200),
        }
        self.trail_particles.append(particle)
    
    def is_out_of_range(self):
        """Check if projectile has exceeded max range."""
        return self.distance_traveled >= self.max_range
    
    def to_bullet_dict(self):
        """
        Convert to standard bullet dictionary format for compatibility.
        
        Returns:
            Dictionary containing bullet properties
        """
        return {
            "x": self.x,
            "y": self.y,
            "dx": self.dx,
            "dy": self.dy,
            "speed": self.speed,
            "damage": self.damage,
            "max_range": self.max_range,
            "distance_traveled": self.distance_traveled,
            "owner": self.owner,
            "is_explosive": self.is_explosive,
            "explosion_radius": self.explosion_radius,
            "is_rocket": True,
        }


def render_rocket(surface, rocket, animation_effect, tile_size, map_data):
    """
    Render a rocket projectile with diffusion animation.
    
    Args:
        surface: Pygame surface to draw on
        rocket: RocketProjectile instance
        animation_effect: RocketDiffusionEffect instance
        tile_size: Size of game tiles
        map_data: Map data module for coordinate conversion
    """
    if isinstance(rocket, dict) and not rocket.get("is_rocket"):
        return
    
    # Get animation frame
    frame = animation_effect.get_frame(rocket.frame_index)
    
    # Calculate screen position
    screen_x = int(rocket.x - frame.get_width() // 2)
    screen_y = int(rocket.y - frame.get_height() // 2)
    
    # Draw the diffusion effect
    surface.blit(frame, (screen_x, screen_y))
    
    # Draw rocket core (bright center)
    core_color = (255, 100, 0)
    core_size = max(3, tile_size // 6)
    pygame.draw.circle(surface, core_color, (int(rocket.x), int(rocket.y)), core_size)
    
    # Draw trail particles
    for particle in rocket.trail_particles[:]:
        age = particle["max_life"] - particle["life"]
        progress = age / particle["max_life"]
        
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 16  # Approximate dt
        
        alpha = int(200 * (1 - progress))
        color = (*particle["color"][:3], alpha)
        
        if particle["life"] <= 0:
            rocket.trail_particles.remove(particle)
        else:
            pygame.draw.circle(
                surface,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                max(1, int(core_size * (1 - progress)))
            )


def render_explosion(surface, x, y, radius_tiles, tile_size, intensity=1.0):
    """
    Render a retro diffusion explosion effect.
    
    Args:
        surface: Pygame surface to draw on
        x, y: Explosion center coordinates
        radius_tiles: Radius in tile units
        tile_size: Size of game tiles
        intensity: Visual intensity multiplier
    """
    radius_pixels = radius_tiles * tile_size
    
    # Outer explosion ring (expanding)
    for ring in range(1, 4):
        radius = radius_pixels * (ring / 3.0)
        alpha = int(255 * (1 - ring / 3.0) * intensity)
        
        if alpha > 0:
            color = (255, 165, 0, alpha)
            pygame.draw.circle(
                surface,
                color,
                (int(x), int(y)),
                int(radius),
                width=max(1, int(tile_size * 0.15))
            )
    
    # Core bright burst
    core_radius = int(radius_pixels * 0.3 * intensity)
    pygame.draw.circle(surface, (255, 255, 100), (int(x), int(y)), core_radius)

