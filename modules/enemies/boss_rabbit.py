from .rabbit import RabbitEnemy
import pygame
import random
import math

class BossRabbit(RabbitEnemy):
    def __init__(self, x, y, properties):
        # Force 'tiny' variant logic for the erratic movements, but we'll use 'big' animations
        properties['variant'] = 'big' 
        super().__init__(x, y, properties)
        
        self.weapon = None
        self.weapon_id = properties.get('weapon', 'P')
        self.resources = properties.get('resources')
        
        if self.resources:
            self.weapon = self.resources.spawn(self.weapon_id, 0, 0)
        
        self.shoot_range = properties.get('shoot_range', 12 * 36)
        self.is_boss = True
        self.hp = properties.get('hp', 200) # Bosses are tough

    def update(self, platforms, player=None, effect_manager=None, **kwargs):
        if not player:
            super().update(platforms, player, effect_manager, **kwargs)
            return

        now = pygame.time.get_ticks()
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))

        # 1. Weapon Tactical State
        if self.weapon:
            self.weapon.update()
            
            if self.weapon.current_ammo <= 0:
                # FEAR/RELOAD STATE
                if not self.weapon.is_reloading:
                    self.weapon.start_reload()
                
                self.personality_state = 'panic'
                # While reloading, use the erratic escape logic
            else:
                # AGGRESSION MODE
                self.personality_state = 'locked_in'
                
                # Auto-shoot if in range and facing player
                if dist < self.shoot_range:
                    # Check if facing player
                    facing_player = (self.direction > 0 and player.rect.centerx > self.rect.centerx) or \
                                    (self.direction < 0 and player.rect.centerx < self.rect.centerx)
                    
                    if facing_player and self.weapon.can_shoot():
                        self.enemy_shoot(effect_manager, kwargs.get('entities'))

        # 2. Run the Rabbit AI (which handles movement based on personality_state)
        # We override the personality logic for the Boss specifically
        self.update_tiny_personality(player, effect_manager, platforms)
        
        # Apply Physics & Animation
        # We don't call super().update() because it would run RabbitEnemy's basic AI if not tiny
        # But we forced variant to 'big' for animations. 
        # So we manually do the base class stuff.
        
        # Physics
        from modules.enemies.base_enemy import BaseEnemy
        BaseEnemy.update(self, platforms, player=player, **kwargs)
        
        if not self.on_ground:
            self.animations.change_state('jump')
        else:
            self.animations.change_state('walk')
            
        self.apply_personality_visuals()

    def enemy_shoot(self, effect_manager, entities):
        if not effect_manager or not self.weapon: return
        
        # Determine direction
        muzzle_dir = self.direction
        offset_x = 25 * muzzle_dir
        muzzle_x = self.rect.centerx + offset_x
        muzzle_y = self.rect.centery + 5
        
        effect_manager.trigger_shake(100, 3)
        effect_manager.create_muzzle_flash(muzzle_x, muzzle_y, muzzle_dir)
        
        # Use player for rocket AOE if needed
        # (Assuming the bullet system handles 'player' as a target)
        if self.weapon.shoot_type == 'rocket':
            # Note: Rockets need the target group to damage. 
            # We'll pass a group containing just the player for now, or just handle it in main.
            player_group = pygame.sprite.Group()
            # We don't have easy access to a player-only group here without passing it.
            # However, the rocket logic in engine/effects.py takes 'entities' and 'player'.
            # We can pass kwargs.get('player') if we had it.
            # For now, let's assume the rocket AOE hits everything.
            effect_manager.spawn_rocket(muzzle_x, muzzle_y, muzzle_dir, self.weapon.bullet_speed, self.weapon.damage, entities, None, owner=self)
        else:
            effect_manager.spawn_bullet(muzzle_x, muzzle_y, muzzle_dir, self.weapon.bullet_speed, self.weapon.damage, owner=self)
            
        self.weapon.current_ammo -= 1
        self.weapon.last_fire_time = pygame.time.get_ticks()

    def apply_personality_visuals(self):
        # Force visual feedback even though we are 'big' variant
        now = pygame.time.get_ticks()
        
        # Boss Specific: Redder tint when aggressive
        if self.personality_state == 'locked_in':
            self.animations.flash_red = True # Constant red glow when attacking
        elif self.personality_state == 'panic':
            self.animations.flash_red = (now // 100) % 2 == 0 # Flashing red when scared/reloading
        else:
            self.animations.flash_red = False

        if self.personality_state == 'taunt':
            self.draw_offset.y = math.sin(now * 0.05) * 6
        else:
            self.draw_offset.y = 0

    def draw(self, screen, camera):
        # Draw the Rabbit
        super().draw(screen, camera)
        
        # Draw the Weapon
        if self.weapon:
            w_img = self.weapon.image
            if self.direction < 0: w_img = pygame.transform.flip(w_img, True, False)
            offset_x = -15 if self.direction < 0 else 15
            w_rect = w_img.get_rect(center=self.rect.center)
            w_rect.x += offset_x
            w_rect.y += 5
            screen.blit(w_img, camera.apply_rect(w_rect))
            
            # Reload bar for boss
            if self.weapon.is_reloading:
                elapsed = (pygame.time.get_ticks() - self.weapon.reload_start_time) / 1000.0
                progress = min(1.0, elapsed / self.weapon.reload_speed)
                pos = camera.apply_rect(w_rect).center
                pygame.draw.arc(screen, (255, 255, 255), (pos[0]-8, pos[1]-8, 16, 16), -math.pi/2, progress*2*math.pi - math.pi/2, 2)
