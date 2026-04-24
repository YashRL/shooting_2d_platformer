import pygame
import sys
import os
import csv
import math
from enemies import Enemy, ENEMY_TYPES
from effects import EffectManager

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 18
SCALED_TILE_SIZE = 36
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = -12
BASE_BULLET_SPEED = 10

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

# Weapon Definitions
WEAPON_STATS = {
    'P': {
        'name': 'Pistol',
        'description': 'An old 6-shooter. Decent damage, reliable.',
        'ammo_capacity': 6,
        'reload_speed': 1.0, 
        'bullet_speed_multiplier': 1.0,
        'damage': 20,
        'shoot_type': 'single',
        'fire_rate': 0.3,
        'tile_id': 'P'
    },
    'CT': {
        'name': 'Chicago Typewriter',
        'description': 'Classic submachine gun. Fast and deadly.',
        'ammo_capacity': 30,
        'reload_speed': 2.0,
        'bullet_speed_multiplier': 1.2,
        'damage': 15,
        'shoot_type': 'auto',
        'fire_rate': 0.1,
        'tile_id': 'CT'
    }
}

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.offset_shake = (0, 0)

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft).move(self.offset_shake)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft).move(self.offset_shake)

    def update(self, target, shake_offset=(0, 0)):
        self.offset_shake = shake_offset
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = max(-(self.height - SCREEN_HEIGHT), y)

        self.camera.topleft = (x, y)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, image, speed, damage):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.right < -500 or self.rect.left > 3000:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_images):
        super().__init__()
        self.tile_images = tile_images
        self.load_animations()
        self.state = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][0]
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.facing_right = True
        
        self.hp = 3
        self.can_double_jump = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 200
        
        self.weapon_slots = [None, None]
        self.active_slot = 0
        self.ammo = [0, 0]
        self.last_shot_time = 0
        self.is_reloading = False
        self.reload_start_time = 0

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Players", "Tiles", "fox")
        self.animations = {'idle': [], 'walk': [], 'jump': []}
        idle_img = pygame.image.load(os.path.join(path, "walk1.png")).convert_alpha()
        self.animations['idle'].append(pygame.transform.scale(idle_img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)))
        for name in ["walk1.png", "walk2.png"]:
            img = pygame.image.load(os.path.join(path, name)).convert_alpha()
            self.animations['walk'].append(pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)))
        jump_img = pygame.image.load(os.path.join(path, "jump.png")).convert_alpha()
        self.animations['jump'].append(pygame.transform.scale(jump_img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE)))

    def animate(self):
        animation = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
            
        image = animation[int(self.frame_index)].copy()
        if self.is_hit:
            red_surf = pygame.Surface(image.get_size()).convert_alpha()
            red_surf.fill((255, 0, 0, 150))
            image.blit(red_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if not self.facing_right:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def get_state(self):
        if not self.on_ground:
            self.state = 'jump'
        elif self.vel_x != 0:
            self.state = 'walk'
        else:
            self.state = 'idle'

    def get_input(self):
        if self.is_hit: return
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

    def handle_event(self, event, items, bullets_group, effect_manager):
        if self.is_hit: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if self.on_ground:
                    self.jump()
                    self.can_double_jump = True
                elif self.can_double_jump:
                    self.jump()
                    self.can_double_jump = False
            
            if event.key == pygame.K_SPACE:
                weapon_id = self.weapon_slots[self.active_slot]
                if weapon_id and WEAPON_STATS[weapon_id]['shoot_type'] == 'single':
                    self.shoot(bullets_group, effect_manager)

            if event.key == pygame.K_e:
                self.check_pickup(items)
            if event.key == pygame.K_r:
                self.start_reload()
            if event.key == pygame.K_1:
                self.active_slot = 0
                self.is_reloading = False
            if event.key == pygame.K_2:
                self.active_slot = 1
                self.is_reloading = False

    def start_reload(self):
        weapon_id = self.weapon_slots[self.active_slot]
        if weapon_id and not self.is_reloading:
            stats = WEAPON_STATS[weapon_id]
            if self.ammo[self.active_slot] < stats['ammo_capacity']:
                self.is_reloading = True
                self.reload_start_time = pygame.time.get_ticks()

    def update_reload(self):
        if self.is_reloading:
            weapon_id = self.weapon_slots[self.active_slot]
            stats = WEAPON_STATS[weapon_id]
            if (pygame.time.get_ticks() - self.reload_start_time) / 1000.0 >= stats['reload_speed']:
                self.ammo[self.active_slot] = stats['ammo_capacity']
                self.is_reloading = False

    def shoot(self, bullets_group, effect_manager):
        if self.is_reloading: return
        weapon_id = self.weapon_slots[self.active_slot]
        if weapon_id:
            stats = WEAPON_STATS[weapon_id]
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_shot_time) / 1000.0 >= stats['fire_rate']:
                if self.ammo[self.active_slot] > 0:
                    direction = 1 if self.facing_right else -1
                    offset_x = 25 if self.facing_right else -25
                    
                    # Effects: Screen Shake & Muzzle Flash
                    effect_manager.trigger_shake(100, 3)
                    effect_manager.create_muzzle_flash(self.rect.centerx + offset_x, self.rect.centery + 5, direction)
                    
                    bullet_img = self.tile_images['bullet']
                    speed = BASE_BULLET_SPEED * stats['bullet_speed_multiplier']
                    new_bullet = Bullet(self.rect.centerx + offset_x, self.rect.centery + 5, 
                                        direction, bullet_img, speed, stats['damage'])
                    bullets_group.add(new_bullet)
                    self.ammo[self.active_slot] -= 1
                    self.last_shot_time = current_time

    def take_damage(self, amount, source_rect):
        if self.is_hit: return
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        knockback_force = 8
        if source_rect.centerx < self.rect.centerx:
            self.vel_x = knockback_force
        else:
            self.vel_x = -knockback_force
        self.vel_y = -6
        self.on_ground = False
        if self.hp <= 0:
            self.hp = 3
            self.rect.topleft = (100, 100)

    def check_pickup(self, items):
        hits = pygame.sprite.spritecollide(self, items, False)
        for item in hits:
            for i in range(2):
                if self.weapon_slots[i] is None:
                    self.weapon_slots[i] = item.tile_id
                    self.ammo[i] = WEAPON_STATS[item.tile_id]['ammo_capacity']
                    item.kill()
                    return

    def draw_weapon_and_ui(self, screen, camera):
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f"HP: {self.hp}", True, RED)
        screen.blit(hp_text, (10, 10))
        weapon_id = self.weapon_slots[self.active_slot]
        if weapon_id:
            stats = WEAPON_STATS[weapon_id]
            weapon_img = self.tile_images[weapon_id]
            if not self.facing_right: weapon_img = pygame.transform.flip(weapon_img, True, False)
            offset_x = 10 if self.facing_right else -10
            weapon_rect = weapon_img.get_rect(center=self.rect.center)
            weapon_rect.x += offset_x
            weapon_rect.y += 5
            screen.blit(weapon_img, camera.apply_rect(weapon_rect))
            if self.is_reloading:
                elapsed = (pygame.time.get_ticks() - self.reload_start_time) / 1000.0
                progress = min(1.0, elapsed / stats['reload_speed'])
                pos = camera.apply_rect(weapon_rect).center
                radius = 4
                pygame.draw.circle(screen, DARK_GRAY, pos, radius, 1)
                if progress > 0:
                    rect = pygame.Rect(pos[0]-radius, pos[1]-radius, radius*2, radius*2)
                    pygame.draw.arc(screen, YELLOW, rect, -math.pi/2, progress * 2 * math.pi - math.pi/2, 2)
            ammo_text = font.render(f"Ammo: {self.ammo[self.active_slot]} / {stats['ammo_capacity']}", True, WHITE)
            screen.blit(ammo_text, (SCREEN_WIDTH - 150, 10))

    def jump(self):
        self.vel_y = JUMP_STRENGTH
        self.on_ground = False

    def apply_gravity(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

    def update(self, platforms, bullets_group, enemies, effect_manager):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
        else:
            self.get_input()
        
        weapon_id = self.weapon_slots[self.active_slot]
        if weapon_id and WEAPON_STATS[weapon_id]['shoot_type'] == 'auto' and not self.is_hit:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.shoot(bullets_group, effect_manager)

        self.rect.x += self.vel_x
        self.check_horizontal_collisions(platforms)
        self.apply_gravity()
        self.check_vertical_collisions(platforms)
        
        enemy_hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hits:
            self.take_damage(enemy.damage, enemy.rect)

        self.update_reload()
        self.get_state()
        self.animate()

    def check_horizontal_collisions(self, platforms):
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                if self.vel_x > 0: self.rect.right = sprite.rect.left
                elif self.vel_x < 0: self.rect.left = sprite.rect.right

    def check_vertical_collisions(self, platforms):
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                if self.vel_y > 0:
                    self.rect.bottom = sprite.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = sprite.rect.bottom
                    self.vel_y = 0
        if self.on_ground:
            self.rect.y += 1
            is_on_something = False
            for sprite in platforms:
                if sprite.rect.colliderect(self.rect):
                    is_on_something = True
                    break
            self.rect.y -= 1
            if not is_on_something: self.on_ground = False

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, image, name, tile_id):
        super().__init__()
        self.image = image
        self.name = name
        self.tile_id = tile_id
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

def load_tiles():
    tiles = {}
    path = os.path.join("Assets", "PNG", "Tiles", "Tiles")
    if not os.path.exists(path): return {}
    files = [f for f in os.listdir(path) if f.endswith('.png')]
    for f in files:
        try:
            idx = int(f.replace('.png', ''))
            img = pygame.image.load(os.path.join(path, f)).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            tiles[idx] = img
        except: continue
    
    pistol_path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "pistol.png")
    if os.path.exists(pistol_path):
        img = pygame.image.load(pistol_path).convert_alpha()
        img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
        tiles['P'] = img

    # Load Chicago Typewriter
    ct_path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "chicago_typwriter.png")
    if os.path.exists(ct_path):
        img = pygame.image.load(ct_path).convert_alpha()
        img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
        tiles['CT'] = img

    bullet_path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "bullet.png")
    if os.path.exists(bullet_path):
        img = pygame.image.load(bullet_path).convert_alpha()
        img = pygame.transform.scale(img, (12, 12))
        tiles['bullet'] = img
    return tiles

def load_level(filename, tile_images):
    platforms, items, enemies = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    max_width, max_height = 0, 0
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, tile_idx_str in enumerate(row):
                if not tile_idx_str: continue
                x, y = c * SCALED_TILE_SIZE, r * SCALED_TILE_SIZE
                if tile_idx_str == 'P': items.add(Item(x, y, tile_images['P'], "Pistol", 'P'))
                elif tile_idx_str == 'CT': items.add(Item(x, y, tile_images['CT'], "Chicago Typewriter", 'CT'))
                elif tile_idx_str == 'E_I': enemies.add(Enemy(x, y, ENEMY_TYPES['Insect']))
                else:
                    try:
                        tile_idx = int(tile_idx_str)
                        if tile_idx != -1 and tile_idx in tile_images:
                            platforms.add(Tile(x, y, tile_images[tile_idx]))
                            max_width, max_height = max(max_width, x + SCALED_TILE_SIZE), max(max_height, y + SCALED_TILE_SIZE)
                    except ValueError: continue
    return platforms, items, enemies, max_width, max_height

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2D Platformer - Juicy Combat")
    clock = pygame.time.Clock()
    tile_images = load_tiles()
    
    try:
        platforms, items, enemies, map_width, map_height = load_level('levels/level_0.csv', tile_images)
    except:
        platforms, items, enemies = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
        map_width, map_height = SCREEN_WIDTH, SCREEN_HEIGHT

    player = Player(100, 100, tile_images)
    camera = Camera(map_width, map_height)
    bullets = pygame.sprite.Group()
    effect_manager = EffectManager()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            player.handle_event(event, items, bullets, effect_manager)

        # Update
        effect_manager.update()
        player.update(platforms, bullets, enemies, effect_manager)
        enemies.update(platforms)
        bullets.update()
        
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hits:
                enemy.take_damage(bullet.damage, bullet.direction)
                bullet.kill()

        camera.update(player, effect_manager.get_shake_offset())

        # Draw
        screen.fill(SKY_BLUE)
        for sprite in platforms: screen.blit(sprite.image, camera.apply(sprite))
        for item in items: screen.blit(item.image, camera.apply(item))
        for enemy in enemies: screen.blit(enemy.image, camera.apply(enemy))
        for bullet in bullets: screen.blit(bullet.image, camera.apply(bullet))
        effect_manager.draw(screen, camera)
        screen.blit(player.image, camera.apply(player))
        player.draw_weapon_and_ui(screen, camera)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
