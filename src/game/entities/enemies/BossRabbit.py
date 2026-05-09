import pygame
import os
import random
from src.game.entities.enemies.RabbitEnemy import RabbitEnemy

class BossRabbit(RabbitEnemy):
    def __init__(self, x, y, properties):
        # Default properties for Boss if not provided
        properties.setdefault('hp', 20)
        properties.setdefault('speed', 3)
        properties.setdefault('resistance', 0.6)
        super().__init__(x, y, properties)
        
        # Boss Specifics
        self.weapon = None
        weapon_id = properties.get('weapon', 'P')
        resources = properties.get('resources')
        if resources:
            self.weapon = resources.spawn(weapon_id, 0, 0)
        
        self.attack_cooldown = properties.get('attack_cooldown', 1000)
        self.last_attack_time = 0
        self.is_boss = True

    def handle_ai(self, player):
        if not player: return
        
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
        
        # Tactical Weapon AI
        if self.weapon and self.weapon.current_ammo > 0:
            self.ai_state = 'aggressive'
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
            
            # Keep a tactical distance (4-6 tiles)
            ideal_dist = 5 * 36
            if dist > ideal_dist + 20:
                self.vel.x = self.direction * self.speed
            elif dist < ideal_dist - 20:
                self.vel.x = -self.direction * self.speed
            else:
                self.vel.x = 0
            
            # Shoot if on cooldown
            if dist < 400 and pygame.time.get_ticks() - self.last_attack_time > self.attack_cooldown:
                self.shoot(player)
                self.last_attack_time = pygame.time.get_ticks()
        else:
            # Panic/Reload State
            self.ai_state = 'fleeing'
            self.direction = -1 if player.rect.centerx > self.rect.centerx else 1
            self.vel.x = self.direction * (self.speed * 1.5)
            if self.on_ground and random.random() < 0.05:
                self.vel.y = self.jump_force
            
            if self.weapon and not self.weapon.is_reloading:
                self.weapon.start_reload()

    def shoot(self, player):
        if not self.weapon or not self.weapon.can_shoot(): return
        
        effect_manager = getattr(self, '_last_effect_manager', None)
        if effect_manager:
            muzzle_x = self.rect.centerx + (self.direction * 20)
            muzzle_y = self.rect.centery + 5
            
            # Pass self as owner to ensure bullet doesn't hit the boss
            effect_manager.spawn_bullet(muzzle_x, muzzle_y, self.direction, 
                                        self.weapon.bullet_speed, self.weapon.damage, owner=self)
            self.weapon.current_ammo -= 1
            self.weapon.last_fire_time = pygame.time.get_ticks()

    def update(self, platforms, player=None, **kwargs):
        self._last_effect_manager = kwargs.get('effect_manager')
        if self.weapon: self.weapon.update()
        super().update(platforms, player=player, **kwargs)

    def draw(self, screen, camera):
        super().draw(screen, camera)
        # Draw the weapon the boss is holding
        if self.weapon:
            w_img = self.weapon.image
            if self.direction < 0: w_img = pygame.transform.flip(w_img, True, False)
            offset_x = -10 if self.direction < 0 else 10
            w_rect = w_img.get_rect(center=self.rect.center)
            w_rect.x += offset_x
            w_rect.y += 5
            screen.blit(w_img, camera.apply_rect(w_rect))
