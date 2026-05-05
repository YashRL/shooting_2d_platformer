from .base_enemy import BaseEnemy
from engine.animation import AnimationManager
import pygame
import os
import random
import math

class RabbitEnemy(BaseEnemy):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        self.jump_power = properties.get('jump_power', -12)
        self.jump_cooldown = 0
        self.jump_delay = properties.get('jump_delay', 2000) # ms between jumps
        self.variant = properties.get('variant', 'big')
        self.load_animations(self.variant)
        
        # Tiny personality state
        self.personality_state = 'calm' # calm, locked_in, taunt, panic
        self.taunt_timer = 0
        self.panic_timer = 0
        self.is_dashing = False
        self.dash_stop_timer = 0
        self.change_dir_timer = 0
        
        # Detection ranges
        self.chase_range = 8 * 36 # 8 tiles
        self.panic_range = 4 * 36
        
        # Visuals
        self.draw_offset = pygame.Vector2(0, 0)

    def load_animations(self, variant):
        folder = "big_rabit" if variant == "big" else "Tiny_rabit"
        path = os.path.join("Assets", "PNG", "Enemies", "Tiles", folder)
        
        frames = {
            'walk': [],
            'jump': [],
            'dead': []
        }
        
        # Walk
        for name in ["walk_1.png", "walk_2.png"]:
            try:
                img = pygame.image.load(os.path.join(path, name)).convert_alpha()
                frames['walk'].append(pygame.transform.scale(img, (36, 36)))
            except:
                pass
            
        # Jump
        try:
            img_jump = pygame.image.load(os.path.join(path, "jump.png")).convert_alpha()
            frames['jump'].append(pygame.transform.scale(img_jump, (36, 36)))
        except:
            pass
        
        # Dead
        try:
            img_dead = pygame.image.load(os.path.join(path, "dead.png")).convert_alpha()
            frames['dead'].append(pygame.transform.scale(img_dead, (36, 36)))
        except:
            pass
        
        self.animations = AnimationManager(frames)

    def update(self, platforms, player=None, effect_manager=None, **kwargs):
        # 1. State Switching
        if self.variant == "tiny":
            self.update_tiny_personality(player, effect_manager, platforms)
        else:
            self.update_basic_ai(platforms)

        # 2. Apply Physics & Base Updates (NEVER skip this or it "disappears/freezes")
        super().update(platforms, player=player, **kwargs)
        
        # 3. Animation State Overrides
        if not self.on_ground:
            self.animations.change_state('jump')
        else:
            self.animations.change_state('walk')
            
        # 4. Personality Visuals (Juicy feedback for limited animations)
        self.apply_personality_visuals()

    def update_basic_ai(self, platforms):
        if self.on_ground:
            self.vel.x = self.direction * self.speed
            # Randomly jump
            if abs(self.vel.x) > 0 and pygame.time.get_ticks() > self.jump_cooldown:
                if random.random() < 0.01:
                    self.jump()
            
            # Wall turn
            if self.is_blocked(platforms):
                self.jump() # Try to jump over
        else:
            self.vel.x = self.direction * self.speed * 0.7

    def is_blocked(self, platforms):
        # Look ahead for a wall
        test_rect = self.rect.copy()
        test_rect.x += self.direction * 15
        for sprite in platforms:
            if sprite.rect.colliderect(test_rect):
                return True
        return False

    def update_tiny_personality(self, player, effect_manager, platforms):
        now = pygame.time.get_ticks()
        
        if not player: return
        
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))

        # --- A. Bullet Dodging (Triggers TAUNT) ---
        if effect_manager and self.personality_state != 'taunt':
            for bullet in effect_manager.bullets:
                bullet_dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(bullet.rect.center))
                if bullet_dist < 100:
                    # If bullet is coming towards us
                    if (bullet.direction > 0 and bullet.rect.centerx < self.rect.centerx) or \
                       (bullet.direction < 0 and bullet.rect.centerx > self.rect.centerx):
                        self.jump(power_mult=1.3)
                        self.personality_state = 'taunt'
                        self.taunt_timer = now + 600
                        # Dash away briefly
                        self.direction = 1 if bullet.direction > 0 else -1
                        self.start_dash(800)
                        # Do NOT return; let physics update run below

        # --- B. State Logic ---
        if self.personality_state == 'taunt':
            self.vel.x = 0
            if now > self.taunt_timer:
                self.personality_state = 'locked_in' if dist < self.chase_range else 'calm'
            return # Skip movement logic while taunting

        # PANIC Check: If player is aiming at it and is close
        player_dir = -1 if player.animations.flip else 1
        is_player_facing = (player_dir > 0 and player.rect.centerx < self.rect.centerx) or \
                           (player_dir < 0 and player.rect.centerx > self.rect.centerx)
        
        if dist < self.panic_range and is_player_facing:
            if self.personality_state != 'panic':
                self.start_dash(600) # Shorter burst
                self.personality_state = 'panic'
                self.panic_timer = now + 600
        elif self.personality_state == 'panic':
            # STOP panicking if player turns away or we've run enough
            if not is_player_facing or now > self.panic_timer:
                self.personality_state = 'locked_in' if dist < self.chase_range else 'calm'

        # CHASE vs CALM (if not panicking)
        if self.personality_state not in ['panic', 'taunt']:
            if dist < self.chase_range:
                if self.personality_state == 'calm':
                    self.jump(power_mult=1.2) # Excitement jump when locking in
                self.personality_state = 'locked_in'
            else:
                self.personality_state = 'calm'

        # --- C. Movement execution based on state ---
        blocked = self.is_blocked(platforms)

        if self.personality_state == 'calm':
            # Cute, slow, small random jumps
            self.speed = self.base_speed * 0.4
            if now > self.change_dir_timer or blocked:
                self.direction *= -1
                self.change_dir_timer = now + random.randint(2000, 5000)
            if self.on_ground and random.random() < 0.005:
                self.jump(power_mult=0.5)
        
        elif self.personality_state == 'locked_in':
            # Joyous aggressive chase
            self.speed = self.base_speed * 1.8 
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
            if self.on_ground:
                if blocked: self.jump(power_mult=1.1)
                elif random.random() < 0.04: self.jump(power_mult=1.1)

        elif self.personality_state == 'panic':
            # Run AWAY from player at extreme speed
            self.speed = self.base_speed * 2.2
            self.direction = 1 if player.rect.centerx < self.rect.centerx else -1
            if self.on_ground:
                # If blocked while panicking, jump OVER whatever is in the way
                if blocked: self.jump(power_mult=1.3)
                else: self.jump(power_mult=0.8)

        # Apply final velocity
        current_move_speed = self.speed * (2.0 if self.is_dashing else 1.0)
        self.vel.x = self.direction * current_move_speed
        
        if self.is_dashing and now > self.dash_stop_timer:
            self.is_dashing = False

    def apply_personality_visuals(self):
        self.draw_offset = pygame.Vector2(0, 0) # Reset offset
        if self.variant != "tiny": return
        
        now = pygame.time.get_ticks()
        
        # TAUNT Visual: Rapid vertical vibration using draw_offset
        if self.personality_state == 'taunt':
            self.draw_offset.y = math.sin(now * 0.05) * 6
            
        # LOCKED IN Visual: Subtle "JOY" pulse (red tint pulse)
        if self.personality_state == 'locked_in':
            self.animations.flash_red = (now // 200) % 2 == 0
        
        # PANIC Visual: Fast flash
        if self.personality_state == 'panic':
            self.animations.flash_red = (now // 100) % 2 == 0

    def draw(self, screen, camera):
        # Use draw_offset for vibration without affecting collision/physics
        draw_rect = camera.apply(self).move(self.draw_offset.x, self.draw_offset.y)
        screen.blit(self.image, draw_rect)

    def start_dash(self, duration):
        self.is_dashing = True
        self.dash_stop_timer = pygame.time.get_ticks() + duration

    def jump(self, power_mult=1.0):
        if self.on_ground and pygame.time.get_ticks() > self.jump_cooldown:
            power = self.jump_power * power_mult
            if self.variant == "tiny":
                power *= random.uniform(0.9, 1.1)
            
            self.vel.y = power
            self.on_ground = False
            # Lower cooldown for tiny rabbits to allow rapid hops
            self.jump_cooldown = pygame.time.get_ticks() + (400 if self.variant == "tiny" else self.jump_delay)


    def start_dash(self, duration):
        self.is_dashing = True
        self.dash_stop_timer = pygame.time.get_ticks() + duration

    def jump(self, power_mult=1.0):
        if self.on_ground and pygame.time.get_ticks() > self.jump_cooldown:
            power = self.jump_power * power_mult
            if self.variant == "tiny":
                power *= random.uniform(0.9, 1.1)
            
            self.vel.y = power
            self.on_ground = False
            # Lower cooldown for tiny rabbits to allow rapid hops
            self.jump_cooldown = pygame.time.get_ticks() + (400 if self.variant == "tiny" else self.jump_delay)


