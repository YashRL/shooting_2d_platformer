import pygame
import random
import math
from engine.effects import Particle

class ExplosiveBarrel(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = properties.get('tile_size', 36)
        self.timer_duration = 3000 # 3 seconds
        self.triggered = False
        self.trigger_time = 0
        
        # Load asset
        self.asset_path = properties.get('asset', "Assets/PNG/Tiles/Tiles/Barrel/203.png")
        try:
            self.original_image = pygame.image.load(self.asset_path).convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (self.tile_size, self.tile_size))
        except:
            self.original_image = pygame.Surface((self.tile_size, self.tile_size))
            self.original_image.fill((150, 75, 0)) # Brown fallback
            
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.Vector2(x, y)
        
    def take_damage(self, amount, direction=1):
        if not self.triggered:
            self.triggered = True
            self.trigger_time = pygame.time.get_ticks()
            print(f"[DEBUG] Barrel at {self.pos} triggered by bullet!")

    def update(self, *args, **kwargs):
        player = kwargs.get('player')
        effect_manager = kwargs.get('effect_manager')

        if self.triggered:
            elapsed = pygame.time.get_ticks() - self.trigger_time
            progress = min(1.0, elapsed / self.timer_duration)
            
            # Growth (up to 5%)
            scale = 1.0 + (progress * 0.05)
            new_size = int(self.tile_size * scale)
            resized_image = pygame.transform.scale(self.original_image, (new_size, new_size))
            
            # Juicy color shift: overlay red with increasing alpha
            overlay = pygame.Surface(resized_image.get_size(), pygame.SRCALPHA)
            # Pulse effect
            pulse = (math.sin(elapsed * 0.02) + 1) / 2
            alpha = int(progress * 150 + pulse * 50) 
            overlay.fill((255, 0, 0, min(255, alpha)))
            
            self.image = resized_image.copy()
            self.image.blit(overlay, (0, 0))
            
            # White "flash" warnings
            if progress > 0.7 and (elapsed // 100) % 2 == 0:
                flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                flash.fill((255, 255, 255, 100))
                self.image.blit(flash, (0, 0))

            # Local vibration
            shake_offset = (0, 0)
            if progress > 0.5:
                intensity = int(progress * 4)
                shake_offset = (random.randint(-intensity, intensity), random.randint(-intensity, intensity))

            # Recenter as it grows and add local shake
            self.rect = self.image.get_rect(center=(self.pos.x + self.tile_size/2 + shake_offset[0], 
                                                   self.pos.y + self.tile_size/2 + shake_offset[1]))
            
            if elapsed >= self.timer_duration:
                self.explode(effect_manager, player)

    def explode(self, effect_manager, player=None):
        if effect_manager:
            # Stronger camera shake for barrels
            effect_manager.trigger_shake(400, 12)
            
            # Red/Orange/White particles
            for _ in range(30):
                vel_x = random.uniform(-8, 8)
                vel_y = random.uniform(-8, 8)
                lifetime = random.randint(500, 1500)
                color = random.choice([(255, 0, 0), (255, 100, 0), (255, 255, 255), (100, 100, 100)])
                effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))
        
        # Damage logic: Check for player in radius (High Damage)
        if player:
            dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
            if dist < 80: # Slightly larger radius than tiles
                player.take_damage(3, self.rect)
        
        print(f"[DEBUG] Barrel Exploded at {self.pos}")
        self.kill()

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
