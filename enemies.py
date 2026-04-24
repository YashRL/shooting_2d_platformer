import pygame
import os
import math
import random

SCALED_TILE_SIZE = 36

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, stats):
        super().__init__()
        self.stats = stats
        self.name = stats['name']
        self.hp = stats['hp']
        self.damage = stats['damage']
        self.base_speed = stats['speed']
        self.speed = self.base_speed
        self.resistance = stats['resistance']
        self.movement_type = stats.get('movement_type', 'ground') # 'ground' or 'fly'
        
        self.load_animations()
        self.state = 'walk'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['walk'][0]
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1 
        self.vel_y = 0
        self.vel_x = 0
        self.gravity = 0.8 if self.movement_type == 'ground' else 0
        
        # Guard/AI Logic
        self.spawn_pos = pygame.Vector2(x, y)
        self.target_pos = pygame.Vector2(x, y)
        self.ai_state = 'guard' # 'guard' or 'chase'
        self.last_player_pos = None
        self.chase_range = 10 * SCALED_TILE_SIZE
        self.guard_range = 5 * SCALED_TILE_SIZE
        self.next_guard_time = 0
        
        # Hit effects
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 150 
        self.hit_flash_duration = 100

    def load_animations(self):
        self.animations = {'walk': [], 'dead': []}
        path = self.stats['asset_path']
        for frame_name in self.stats['walk_frames']:
            img = pygame.image.load(os.path.join(path, frame_name)).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            self.animations['walk'].append(img)
        
        dead_img_name = self.stats.get('dead_frame', "dead.png")
        dead_img = pygame.image.load(os.path.join(path, dead_img_name)).convert_alpha()
        self.animations['dead'].append(pygame.transform.scale(dead_img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)))

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        image = animation[int(self.frame_index)].copy()
        
        if self.is_hit and pygame.time.get_ticks() - self.hit_timer < self.hit_flash_duration:
            red_surf = pygame.Surface(image.get_size()).convert_alpha()
            red_surf.fill((255, 0, 0, 180))
            image.blit(red_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if self.direction == 1:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def apply_gravity(self):
        if self.movement_type == 'ground':
            self.vel_y += self.gravity
            self.rect.y += self.vel_y

    def check_collisions(self, platforms):
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.vel_y = 0

    def update_ai(self, player_rect):
        dist_to_player = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player_rect.center))
        
        if dist_to_player < self.chase_range:
            self.ai_state = 'chase'
            self.target_pos = pygame.Vector2(player_rect.center)
            self.last_player_pos = pygame.Vector2(player_rect.center)
        else:
            if self.ai_state == 'chase':
                # Just lost player, guard the last seen position
                self.ai_state = 'guard'
                self.spawn_pos = pygame.Vector2(self.last_player_pos)
            
            # Guarding logic: move to random points around spawn
            if pygame.time.get_ticks() > self.next_guard_time:
                angle = random.uniform(0, math.pi * 2)
                r = random.uniform(0, self.guard_range)
                self.target_pos = self.spawn_pos + pygame.Vector2(math.cos(angle) * r, math.sin(angle) * r)
                self.next_guard_time = pygame.time.get_ticks() + random.randint(1000, 3000)

    def move(self, platforms):
        if self.is_hit:
            self.rect.x += self.vel_x
            # Add horizontal collision check during knockback
            for sprite in platforms:
                if sprite.rect.colliderect(self.rect):
                    if self.vel_x > 0: self.rect.right = sprite.rect.left
                    else: self.rect.left = sprite.rect.right
            return

        if self.movement_type == 'fly':
            # Fly towards target_pos with obstacle avoidance
            diff = self.target_pos - pygame.Vector2(self.rect.center)
            if diff.length() > 5:
                dir_vec = diff.normalize()
                
                # Predict next position
                next_x = self.rect.x + dir_vec.x * self.speed
                next_y = self.rect.y + dir_vec.y * self.speed
                
                # Check if direct path is blocked
                test_rect = self.rect.copy()
                test_rect.x = next_x
                test_rect.y = next_y
                
                blocked = False
                for sprite in platforms:
                    if sprite.rect.colliderect(test_rect):
                        blocked = True
                        break
                
                if blocked:
                    # Try to find an alternative direction (Up or Down) to bypass
                    # If blocked horizontally, try moving vertically
                    alt_dir = pygame.Vector2(0, 1 if dir_vec.y >= 0 else -1)
                    if abs(dir_vec.x) > abs(dir_vec.y): # Mostly horizontal block
                        # Shift target slightly up or down to find gap
                        self.rect.y += self.speed * (1 if self.rect.centery < self.target_pos.y else -1)
                    else: # Mostly vertical block
                        self.rect.x += self.speed * (1 if self.rect.centerx < self.target_pos.x else -1)
                else:
                    # Path is clear, move normally
                    self.rect.x = next_x
                    self.rect.y = next_y
                
                self.direction = 1 if dir_vec.x > 0 else -1
                
                # Final collision safety to prevent getting inside tiles
                for sprite in platforms:
                    if sprite.rect.colliderect(self.rect):
                        if abs(dir_vec.x) > abs(dir_vec.y):
                            if dir_vec.x > 0: self.rect.right = sprite.rect.left
                            else: self.rect.left = sprite.rect.right
                        else:
                            if dir_vec.y > 0: self.rect.bottom = sprite.rect.top
                            else: self.rect.top = sprite.rect.bottom
        else:
            # Ground patrol
            self.rect.x += self.direction * self.speed
            hit_wall = False
            for sprite in platforms:
                if sprite.rect.colliderect(self.rect):
                    hit_wall = True
                    if self.direction > 0: self.rect.right = sprite.rect.left
                    else: self.rect.left = sprite.rect.right
                    self.direction *= -1
                    break
            if not hit_wall:
                look_ahead = self.rect.right if self.direction > 0 else self.rect.left
                test_rect = pygame.Rect(look_ahead, self.rect.bottom + 1, 2, 2)
                on_edge = True
                for sprite in platforms:
                    if sprite.rect.colliderect(test_rect):
                        on_edge = False
                        break
                if on_edge: self.direction *= -1

    def take_damage(self, amount, bullet_direction):
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        impact = (amount / 10.0) * (1.0 - self.resistance)
        self.speed = max(0.5, self.speed - impact * 0.1)
        self.vel_x = bullet_direction * (impact * 4)
        if self.movement_type == 'fly':
            self.vel_y = -2 * impact
        else:
            self.vel_y = -3 * impact 
        
        if self.hp <= 0:
            self.kill()

    def update(self, platforms, player_rect):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
                self.vel_x = 0

        self.update_ai(player_rect)
        self.apply_gravity()
        if self.movement_type == 'ground':
            self.check_collisions(platforms)
        self.move(platforms)
        self.animate()

# Registry for different enemy types
ENEMY_TYPES = {
    'Insect': {
        'name': 'Insect',
        'asset_path': os.path.join("Assets", "PNG", "Enemies", "Tiles", "Insect"),
        'walk_frames': ["walk1.png", "walk2.png", "walk3.png"],
        'dead_frame': "dead.png",
        'hp': 40,
        'damage': 1,
        'speed': 1.5,
        'resistance': 0.2,
        'movement_type': 'ground'
    },
    'Bee': {
        'name': 'Bee',
        'asset_path': os.path.join("Assets", "PNG", "Enemies", "Tiles", "Bee"),
        'walk_frames': ["fly1.png", "fly2.png", "fly3.png"],
        'dead_frame': "fly_dead.png",
        'hp': 60, # 50% more than Insect (40 * 1.5)
        'damage': 1,
        'speed': 1.8, # 20% faster than Insect (1.5 * 1.2)
        'resistance': 0.4, # Slightly harder to push back
        'movement_type': 'fly'
    }
}
