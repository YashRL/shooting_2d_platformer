from engine.physics import PhysicsEntity
from engine.animation import AnimationManager
import pygame

class BaseEnemy(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.hp = properties.get('hp', 10)
        self.speed = properties.get('speed', 1)
        self.damage = properties.get('damage', 1)
        self.direction = 1
        
        self.animations = None # To be set by subclass
        self.image = pygame.Surface((36, 36))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, platforms, **kwargs):
        self.apply_physics(platforms)
        if self.animations:
            self.animations.flip = self.direction == 1 # Flip if facing right (asset dependent)
            self.animations.update()
            self.image = self.animations.get_current_frame()
