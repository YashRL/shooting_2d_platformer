import pygame
import os
import random
import math
from src.engine.core.PhysicsEntity import PhysicsEntity

class BaseEnemy(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.hp = properties.get('hp', 1)
        self.speed = properties.get('speed', 2)
        self.damage = properties.get('damage', 1)
        self.resistance = properties.get('resistance', 0.1)
        
        self.direction = 1
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 150
        
        self.spawn_pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y)
        self.ai_state = 'guard'
        self.next_ai_update_time = 0
        
        self.animations = None
        self.rect = pygame.Rect(x, y, 36, 36) # Default size

    def take_damage(self, amount, knockback_source):
        if self.is_hit: return
        
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        
        # Knockback logic
        knockback_force = 5 * (1.0 - self.resistance)
        if isinstance(knockback_source, pygame.Rect):
            source_center_x = knockback_source.centerx
        elif isinstance(knockback_source, int):
            # If it's a direction (-1 or 1)
            source_center_x = self.rect.centerx - (knockback_source * 10)
        else:
            source_center_x = self.rect.centerx

        if source_center_x < self.rect.centerx:
            self.vel.x = knockback_force
        else:
            self.vel.x = -knockback_force
        self.vel.y = -4
        self.on_ground = False
        
        if self.hp <= 0:
            self.kill()

    def draw(self, screen, camera):
        if hasattr(self, 'image') and self.image:
            screen.blit(self.image, camera.apply(self))

    def update(self, platforms, player=None, **kwargs):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
        
        if self.animations:
            self.animations.flip = self.direction < 0
            self.animations.flash_red = self.is_hit
            self.animations.update()
            frame = self.animations.get_current_frame()
            if frame:
                self.image = frame
                self.rect = self.image.get_rect(center=self.rect.center)
