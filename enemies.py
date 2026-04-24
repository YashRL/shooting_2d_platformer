import pygame
import os

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
        self.resistance = stats['resistance'] # 0.0 to 1.0 (0 = no resistance, 1 = full resistance)
        
        self.load_animations()
        self.state = 'walk'
        self.frame_index = 0
        self.animation_speed = 0.1
        self.image = self.animations['walk'][0]
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 1 
        self.vel_y = 0
        self.vel_x = 0
        self.gravity = 0.8
        
        # Hit effects
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 150 # ms
        self.hit_flash_duration = 100

    def load_animations(self):
        self.animations = {'walk': [], 'dead': []}
        path = self.stats['asset_path']
        for frame_name in self.stats['walk_frames']:
            img = pygame.image.load(os.path.join(path, frame_name)).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            self.animations['walk'].append(img)
        dead_img = pygame.image.load(os.path.join(path, "dead.png")).convert_alpha()
        self.animations['dead'].append(pygame.transform.scale(dead_img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)))

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        image = animation[int(self.frame_index)].copy()
        
        # Red flash effect
        if self.is_hit and pygame.time.get_ticks() - self.hit_timer < self.hit_flash_duration:
            red_surf = pygame.Surface(image.get_size()).convert_alpha()
            red_surf.fill((255, 0, 0, 180))
            image.blit(red_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if self.direction == 1:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def apply_gravity(self):
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

    def move(self, platforms):
        if self.is_hit:
            # During hit, move by vel_x (knockback)
            self.rect.x += self.vel_x
        else:
            # Normal patrol
            self.rect.x += self.direction * self.speed
        
        # Check wall collision
        hit_wall = False
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                hit_wall = True
                if self.direction > 0 or self.vel_x > 0:
                    self.rect.right = sprite.rect.left
                else:
                    self.rect.left = sprite.rect.right
                
                if not self.is_hit:
                    self.direction *= -1
                break
        
        # Edge detection
        if not hit_wall and not self.is_hit:
            look_ahead = self.rect.right if self.direction > 0 else self.rect.left
            test_rect = pygame.Rect(look_ahead, self.rect.bottom + 1, 2, 2)
            on_edge = True
            for sprite in platforms:
                if sprite.rect.colliderect(test_rect):
                    on_edge = False
                    break
            if on_edge:
                self.direction *= -1

    def take_damage(self, amount, bullet_direction):
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        
        # Juicy hit logic: slowdown and knockback jump
        # Calculated by damage vs resistance
        impact = (amount / 10.0) * (1.0 - self.resistance)
        
        # Slowdown: Decrease patrol speed permanently (simple version)
        self.speed = max(0.5, self.speed - impact * 0.2)
        
        # Knockback Jump
        self.vel_x = bullet_direction * (impact * 4)
        self.vel_y = -3 * impact # Upward pop
        
        if self.hp <= 0:
            self.kill()

    def update(self, platforms):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
                self.vel_x = 0

        self.apply_gravity()
        self.check_collisions(platforms)
        self.move(platforms)
        self.animate()

# Registry for different enemy types
ENEMY_TYPES = {
    'Insect': {
        'name': 'Insect',
        'asset_path': os.path.join("Assets", "PNG", "Enemies", "Tiles", "Insect"),
        'walk_frames': ["walk1.png", "walk2.png", "walk3.png"],
        'hp': 40,
        'damage': 1,
        'speed': 1.5,
        'resistance': 0.2 # Low resistance, gets pushed back easily
    }
}
