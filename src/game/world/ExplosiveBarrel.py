import pygame
import random
from src.engine.core.PhysicsEntity import PhysicsEntity
from src.engine.graphics.Particle import Particle

class ExplosiveBarrel(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.tile_size = 36
        asset_path = properties.get('asset', "Assets/PNG/Tiles/Tiles/Props/barrel.png")
        try:
            self.image = pygame.image.load(asset_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.tile_size, self.tile_size))
        except:
            self.image = pygame.Surface((self.tile_size, self.tile_size))
            self.image.fill((139, 69, 19))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = properties.get('hp', 1)
        self.explosion_damage = properties.get('damage', 3)
        self.explosion_radius = properties.get('radius', 100)

    def take_damage(self, amount, source_rect):
        self.hp -= amount
        if self.hp <= 0:
            self.explode(getattr(self, '_last_effect_manager', None), 
                         getattr(self, '_last_entities', []), 
                         getattr(self, '_last_player', None))

    def explode(self, effect_manager, entities, player):
        if effect_manager:
            effect_manager.trigger_shake(400, 12)
            for _ in range(30):
                vel_x = random.uniform(-8, 8)
                vel_y = random.uniform(-8, 8)
                lifetime = random.randint(500, 1500)
                color = random.choice([(255, 50, 0), (255, 200, 0), (100, 100, 100), (50, 50, 50)])
                effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))
        
        # Area Damage
        for entity in entities:
            if entity != self and hasattr(entity, 'take_damage'):
                dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(entity.rect.center))
                if dist < self.explosion_radius:
                    entity.take_damage(self.explosion_damage, self.rect)
        
        if player:
            dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
            if dist < self.explosion_radius:
                player.take_damage(self.explosion_damage, self.rect)
        
        self.kill()

    def update(self, platforms, **kwargs):
        self._last_effect_manager = kwargs.get('effect_manager')
        self._last_entities = kwargs.get('entities', [])
        self._last_player = kwargs.get('player')
        self.apply_physics(platforms)
