import pygame
import random
import math
from src.game.world.Tile import Tile
from src.engine.graphics.Particle import Particle

class ExplodingTile(Tile):
    def __init__(self, x, y, image, parallax_factor=1.0, damage=0):
        super().__init__(x, y, image, parallax_factor, damage)
        self.original_image = image.copy()
        self.pos = pygame.Vector2(x, y)
        self.triggered = False
        self.trigger_time = 0
        self.timer_duration = 3000
        self.tile_size = self.rect.width
        
    def update(self, *args, **kwargs):
        player = kwargs.get('player')
        effect_manager = kwargs.get('effect_manager')
        
        if not player or (self.triggered and not effect_manager):
            return

        if not self.triggered:
            # Trigger if player is grounded on this tile
            if getattr(player, 'current_ground', None) == self:
                self.triggered = True
                self.trigger_time = pygame.time.get_ticks()

        if self.triggered:
            elapsed = pygame.time.get_ticks() - self.trigger_time
            progress = min(1.0, elapsed / self.timer_duration)
            
            # Growth
            scale = 1.0 + (progress * 0.05)
            new_size = int(self.tile_size * scale)
            resized_image = pygame.transform.scale(self.original_image, (new_size, new_size))
            
            # Pulse overlay
            overlay = pygame.Surface(resized_image.get_size(), pygame.SRCALPHA)
            pulse = (math.sin(elapsed * 0.02) + 1) / 2
            alpha = int(progress * 150 + pulse * 50) 
            overlay.fill((255, 0, 0, min(255, alpha)))
            
            self.image = resized_image.copy()
            self.image.blit(overlay, (0, 0))
            
            if progress > 0.7 and (elapsed // 100) % 2 == 0:
                flash = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                flash.fill((255, 255, 255, 100))
                self.image.blit(flash, (0, 0))

            if elapsed >= self.timer_duration:
                self.explode(effect_manager, player)

    def explode(self, effect_manager, player=None):
        if effect_manager:
            effect_manager.trigger_shake(300, 10)
            for _ in range(25):
                vel_x = random.uniform(-6, 6)
                vel_y = random.uniform(-6, 6)
                lifetime = random.randint(400, 1200)
                color = random.choice([(255, 0, 0), (255, 100, 0), (255, 255, 255), (200, 0, 0)])
                effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))
        
        if player:
            dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
            if dist < 60:
                player.take_damage(3, self.rect)
        
        self.kill()
