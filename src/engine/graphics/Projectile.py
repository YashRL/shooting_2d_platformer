import pygame
import random
from src.engine.graphics.Particle import Particle

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, image, owner=None):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.owner = owner

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.right < -1000 or self.rect.left > 5000:
            self.kill()

class Rocket(Bullet):
    def __init__(self, x, y, direction, speed, damage, image, effect_manager, entities, player, owner=None):
        super().__init__(x, y, direction, speed, damage, image, owner)
        self.effect_manager = effect_manager
        self.entities = entities
        self.player = player
        
        # Rotate image based on direction
        if direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        super().update()
        # Smoke trail
        if random.random() > 0.3:
            vel_x = -self.direction * random.uniform(1, 3)
            vel_y = random.uniform(-1, 1)
            color = random.choice([(100, 100, 100), (150, 150, 150), (200, 200, 200)])
            lifetime = random.randint(200, 500)
            self.effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))

    def kill(self):
        if self.alive():
            self.explode()
        super().kill()

    def explode(self):
        # Stronger camera shake for RPG
        self.effect_manager.trigger_shake(500, 15)
        
        # Red/Orange/White/Smoke particles
        for _ in range(40):
            vel_x = random.uniform(-10, 10)
            vel_y = random.uniform(-10, 10)
            lifetime = random.randint(600, 1800)
            color = random.choice([(255, 0, 0), (255, 150, 0), (255, 255, 255), (80, 80, 80)])
            self.effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))
        
        # Damage logic: Check for entities in radius
        explosion_radius = 100
        for entity in self.entities:
            if hasattr(entity, 'take_damage') and entity != self:
                dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(entity.rect.center))
                if dist < explosion_radius:
                    entity.take_damage(self.damage, 1 if entity.rect.centerx > self.rect.centerx else -1)

        # Damage player if in radius
        if self.player:
            dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(self.player.rect.center))
            if dist < explosion_radius:
                self.player.take_damage(2, self.rect)
        
        print(f"[DEBUG] Rocket Exploded at {self.rect.center}")
