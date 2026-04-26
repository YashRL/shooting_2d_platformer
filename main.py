import pygame
import sys
import csv
import os
from engine.loader import ResourceManager
from modules.world.tile import Tile
from engine.effects import EffectManager
from engine.ui import UIManager

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

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

    def update(self, target, shake_offset=(0,0)):
        self.offset_shake = shake_offset
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        self.camera.topleft = (x, y)

class WorldItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_id, image):
        super().__init__()
        self.item_id = item_id
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

class Game:
    def __init__(self, level_path):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TheTreeSentinal Engine by Yash - Juicy Combat")
        self.clock = pygame.time.Clock()
        
        self.resources = ResourceManager()
        self.effect_manager = EffectManager()
        self.ui_manager = UIManager()
        
        self.platforms = pygame.sprite.Group()
        self.decors = pygame.sprite.Group() # New group for props
        self.entities = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.player = None
        
        self.load_scene(level_path)
        self.camera = Camera(self.map_width, self.map_height)

    def load_scene(self, path):
        if not os.path.exists(path):
            print(f"Error: Level {path} not found.")
            sys.exit()
            
        with open(path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            
        self.map_height = len(data) * 36
        self.map_width = len(data[0]) * 36
        for r, row in enumerate(data):
            for c, cell in enumerate(row):
                if cell == '-1': continue
                x, y = c * 36, r * 36

                # Split cell into World and Entity layers
                parts = cell.split(';')
                ids_to_spawn = parts if len(parts) > 1 else [cell]

                for item_id in ids_to_spawn:
                    if item_id == '-1': continue

                    info = self.resources.registry.get(item_id)
                    if not info: continue

                    if info['type'] == 'static':
                        self.platforms.add(Tile(x, y, self.resources.get_image(item_id)))
                    elif info['type'] == 'decor':
                        self.decors.add(Tile(x, y, self.resources.get_image(item_id)))
                    elif info['category'] == 'Weapons':
                        self.items.add(WorldItem(x, y, item_id, self.resources.get_image(item_id)))
                    elif info['type'] == 'entity':
                        entity = self.resources.spawn(item_id, x, y)
                        if entity:
                            if item_id == 'START': self.player = entity
                            else: self.entities.add(entity)

        if not self.player:
            self.player = self.resources.spawn('START', 100, 100)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            # Update
            self.player.update(self.platforms, self.effect_manager, self.items)
            self.entities.update(self.platforms, player_rect=self.player.rect)
            self.effect_manager.update()
            
            # Bullet Collisions
            for bullet in self.effect_manager.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.entities, False)
                for enemy in hits:
                    if hasattr(enemy, 'take_damage'):
                        enemy.take_damage(bullet.damage, bullet.direction)
                    bullet.kill()
                if pygame.sprite.spritecollideany(bullet, self.platforms):
                    bullet.kill()

            # Player-Enemy Collisions
            enemy_hits = pygame.sprite.spritecollide(self.player, self.entities, False)
            for enemy in enemy_hits:
                if hasattr(enemy, 'damage'):
                    self.player.take_damage(enemy.damage, enemy.rect)

            self.camera.update(self.player, self.effect_manager.get_shake_offset())

            # Draw
            self.screen.fill((135, 206, 235))
            
            # 1. Draw decors (background props)
            for sprite in self.decors: self.screen.blit(sprite.image, self.camera.apply(sprite))
            # 2. Draw platforms (solid tiles)
            for sprite in self.platforms: self.screen.blit(sprite.image, self.camera.apply(sprite))
            
            for item in self.items: self.screen.blit(item.image, self.camera.apply(item))
            for entity in self.entities: self.screen.blit(entity.image, self.camera.apply(entity))
            
            self.effect_manager.draw(self.screen, self.camera)
            self.player.draw(self.screen, self.camera)
            
            # HUD
            self.ui_manager.draw_health_bar(self.screen, 20, 20, self.player.hp, self.player.max_hp, width_in_segments=6)
            
            # Ammo HUD
            active_weapon = self.player.weapon_slots[self.player.active_slot]
            if active_weapon:
                self.ui_manager.draw_ammo(self.screen, 20, 65, active_weapon.current_ammo, active_weapon.ammo_capacity)
            
            self.player.draw_hud(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "levels/level_0.csv"
    game = Game(level)
    game.run()
