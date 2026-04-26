from .base_enemy import BaseEnemy
from engine.animation import AnimationManager
import pygame
import os
import math

class BeeEnemy(BaseEnemy):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        self.gravity = 0 # Flying
        self.load_animations()

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Enemies", "Tiles", "Bee")
        frames = {'fly': []}
        for name in ["fly1.png", "fly2.png", "fly3.png"]:
            img = pygame.image.load(os.path.join(path, name)).convert_alpha()
            frames['fly'].append(pygame.transform.scale(img, (36, 36)))
        self.animations = AnimationManager(frames)

    def update(self, platforms, player_rect=None, **kwargs):
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 300 and dist > 5:
                self.vel.x = (dx/dist) * self.speed
                self.vel.y = (dy/dist) * self.speed
                self.direction = 1 if self.vel.x > 0 else -1
            else:
                self.vel.x = 0
                self.vel.y = 0
        
        # Super update handles physics and animation
        super().update(platforms, **kwargs)
