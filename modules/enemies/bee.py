from .base_enemy import BaseEnemy
from engine.animation import AnimationManager
import pygame
import os
import math
import random

class BeeEnemy(BaseEnemy):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        self.gravity = 0 # It flies
        self.chase_range = 10 * 36
        self.guard_range = 5 * 36
        self.load_animations()

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Enemies", "Tiles", "Bee")
        frames = {'fly': []}
        for name in ["fly1.png", "fly2.png", "fly3.png"]:
            img = pygame.image.load(os.path.join(path, name)).convert_alpha()
            frames['fly'].append(pygame.transform.scale(img, (36, 36)))
        self.animations = AnimationManager(frames)

    def update_ai(self, player_rect):
        if not player_rect: return
        
        dist_to_player = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player_rect.center))
        
        if dist_to_player < self.chase_range:
            self.ai_state = 'chase'
            self.target_pos = pygame.Vector2(player_rect.center)
            self.last_player_pos = pygame.Vector2(player_rect.center)
        else:
            if self.ai_state == 'chase' and self.last_player_pos:
                # Just lost player, move spawn point to where we last saw them to "guard" that area
                self.ai_state = 'guard'
                self.spawn_pos = pygame.Vector2(self.last_player_pos)
            
            # Guarding logic: move to random points around the guard center (spawn_pos)
            if pygame.time.get_ticks() > self.next_ai_update_time:
                angle = random.uniform(0, math.pi * 2)
                r = random.uniform(0, self.guard_range)
                self.target_pos = self.spawn_pos + pygame.Vector2(math.cos(angle) * r, math.sin(angle) * r)
                self.next_ai_update_time = pygame.time.get_ticks() + random.randint(1500, 4000)

    def move_towards_target(self, platforms):
        diff = self.target_pos - pygame.Vector2(self.rect.center)
        if diff.length() > 5:
            dir_vec = diff.normalize()
            self.vel = dir_vec * self.speed
            
            # Simple Obstacle Avoidance
            # Check if direct path is likely blocked
            test_rect = self.rect.copy()
            test_rect.x += self.vel.x
            test_rect.y += self.vel.y
            
            for sprite in platforms:
                if sprite.rect.colliderect(test_rect):
                    # If blocked, try to shift vertically or horizontally to bypass
                    if abs(dir_vec.x) > abs(dir_vec.y): # Horizontal block
                        self.vel.y = self.speed if self.rect.centery < self.target_pos.y else -self.speed
                    else: # Vertical block
                        self.vel.x = self.speed if self.rect.centerx < self.target_pos.x else -self.speed
                    break
        else:
            self.vel = pygame.Vector2(0, 0)

    def update(self, platforms, player_rect=None, **kwargs):
        self.update_ai(player_rect)
        self.move_towards_target(platforms)
        
        # Base class handles physics application and animation cycling
        super().update(platforms, **kwargs)
