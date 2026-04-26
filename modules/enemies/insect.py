from .base_enemy import BaseEnemy
from engine.animation import AnimationManager
import pygame
import os

class InsectEnemy(BaseEnemy):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        self.load_animations()

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Enemies", "Tiles", "Insect")
        frames = {'walk': []}
        for name in ["walk1.png", "walk2.png", "walk3.png"]:
            img = pygame.image.load(os.path.join(path, name)).convert_alpha()
            frames['walk'].append(pygame.transform.scale(img, (36, 36)))
        self.animations = AnimationManager(frames)

    def update(self, platforms, **kwargs):
        # Patrol logic
        self.vel.x = self.direction * self.speed
        
        # Physics (handles gravity & walls)
        self.apply_physics(platforms)
        
        # Edge Detection
        if self.on_ground:
            look_ahead = self.rect.right if self.direction > 0 else self.rect.left
            test_rect = pygame.Rect(look_ahead, self.rect.bottom + 1, 2, 2)
            on_edge = True
            for sprite in platforms:
                if sprite.rect.colliderect(test_rect):
                    on_edge = False
                    break
            if on_edge: self.direction *= -1
            
        # Wall turn
        if self.vel.x == 0: # Hit a wall
            self.direction *= -1

        # Super update handles animation
        super().update(platforms, **kwargs)
