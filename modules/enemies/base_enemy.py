from engine.physics import PhysicsEntity
from engine.animation import AnimationManager
import pygame
import random
import math

class BaseEnemy(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.hp = properties.get('hp', 10)
        self.base_speed = properties.get('speed', 1)
        self.speed = self.base_speed
        self.damage = properties.get('damage', 1)
        self.resistance = properties.get('resistance', 0.2)
        self.direction = 1
        
        # AI State
        self.spawn_pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y)
        self.ai_state = 'guard'
        self.last_player_pos = None
        self.next_ai_update_time = 0
        
        # Hit Feedback
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 200 # ms
        
        self.animations = None
        self.image = pygame.Surface((36, 36))
        self.rect = self.image.get_rect(topleft=(x, y))

    def take_damage(self, amount, bullet_direction=0):
        if self.is_hit: return
        
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        
        # Impact Physics: Resistance reduces knockback
        impact = (amount / 10.0) * (1.0 - self.resistance)
        self.vel.x = bullet_direction * (impact * 5)
        self.vel.y = -4 * impact # Small back jump
        self.on_ground = False
        
        # Slow down slightly permanently or temporarily? 
        # Previous logic: self.speed = max(0.5, self.speed - impact * 0.1)
        self.speed = max(0.5, self.speed - impact * 0.1)
        
        if self.hp <= 0:
            self.kill()

    def update(self, platforms, player=None, **kwargs):
        # Handle Hit Recovery
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
            
        # Apply Physics (BaseEnemy subclass will set vel.x/y before this)
        self.apply_physics(platforms)
        
        if self.animations:
            # Face the direction of movement only if not hit (knockback)
            if not self.is_hit:
                if self.vel.x > 0: self.direction = 1
                elif self.vel.x < 0: self.direction = -1
            
            self.animations.flip = self.direction == 1
            self.animations.flash_red = self.is_hit
            self.animations.update()
            self.image = self.animations.get_current_frame()
