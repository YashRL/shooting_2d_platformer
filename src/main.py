import sys
import os

# Add project root to sys.path to allow absolute src.* imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import pygame
import json
from src.engine.core.ResourceManager import ResourceManager
from src.game.world.Tile import Tile
from src.game.world.ExplodingTile import ExplodingTile
from src.engine.graphics.EffectManager import EffectManager
from src.engine.ui.UIManager import UIManager
from src.engine.graphics.ParallaxManager import ParallaxManager

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
        factor = getattr(entity, 'parallax_factor', 1.0)
        return self.apply_rect(entity.rect, factor)

    def apply_rect(self, rect, factor=1.0):
        px = self.camera.x * factor
        py = self.camera.y * factor
        return rect.move(px, py).move(self.offset_shake)

    def update(self, target, shake_offset=(0,0)):
        self.offset_shake = shake_offset
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, max(-(self.width - SCREEN_WIDTH), x))
        y = min(0, max(-(self.height - SCREEN_HEIGHT), y))
        self.camera.topleft = (x, y)

class WorldItem(pygame.sprite.Sprite):
    def __init__(self, x, y, item_id, image, parallax_factor=1.0):
        super().__init__()
        self.item_id = item_id
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.parallax_factor = parallax_factor

class Game:
    def __init__(self, level_name):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TheTreeSentinal Engine - Reborn")
        self.clock = pygame.time.Clock()
        
        self.resources = ResourceManager()
        self.effect_manager = EffectManager()
        self.ui_manager = UIManager()
        
        self.platforms = pygame.sprite.Group()
        self.background_statics = pygame.sprite.Group()
        self.foreground_statics = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.player = None
        
        self.load_scene(level_name)
        self.camera = Camera(self.map_width, self.map_height)
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def load_scene(self, level_name):
        result = self.resources.load_level(level_name)
        if not result:
            print(f"Error: Level {level_name} could not be loaded.")
            sys.exit()

        self.metadata = result.get('metadata', {})
        grid = result['grid']
        entities = result['entities']
        
        theme = self.metadata.get("theme", "nature_1")
        intensity = self.metadata.get("parallax_intensity", 1.0)
        y_offset = self.metadata.get("parallax_y_offset", 0)
        
        self.parallax_manager = ParallaxManager(f"Assets/PNG/Backgrounds/{theme}", SCREEN_HEIGHT, intensity, y_offset)
        
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.map_width = self.cols * 36
        self.map_height = self.rows * 36
        
        # 1. Process Grid (Tiles)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = grid[r][c]
                if cell == '-1': continue
                
                x, y = c * 36, r * 36
                actual_id = cell.split('[')[0] if '[' in cell else cell
                info = self.resources.registry.get(actual_id)
                if not info: continue

                parallax = info.get('parallax_factor', 1.0)
                layer = "back"
                if '[' in cell and 'layer:front' in cell.lower(): layer = "front"

                if info.get('category') == 'Danger':
                    sprite = ExplodingTile(x, y, self.resources.get_image(cell), parallax)
                    self.platforms.add(sprite)
                    self.entities.add(sprite)
                else:
                    sprite = Tile(x, y, self.resources.get_image(cell), parallax, damage=info.get('damage', 0))
                    if info.get('type') == 'static':
                        self.platforms.add(sprite)
                
                if layer == "front": self.foreground_statics.add(sprite)
                else: self.background_statics.add(sprite)

        # 2. Process Spawned Entities
        for entity in entities:
            from src.game.entities.players.FoxPlayer import FoxPlayer
            from src.game.weapons.BaseWeapon import BaseWeapon
            
            # Use properties if available, otherwise guess
            props = getattr(entity, 'properties', {})
            category = props.get('category')

            if isinstance(entity, FoxPlayer):
                self.player = entity
            elif isinstance(entity, BaseWeapon):
                # standalone weapon pickable
                item_id = props.get('item_id', 'UNKNOWN')
                self.items.add(WorldItem(entity.x, entity.y, item_id, entity.image))
            elif category == 'Platforms':
                self.platforms.add(entity)
            else:
                if isinstance(entity, pygame.sprite.Sprite):
                    self.entities.add(entity)

        if not self.player:
            # Check for a manually placed START point in the loaded entities
            start_pos = (100, 100)
            for entity in entities:
                # We need to check the original data if it was a START type
                # But since the entities are already spawned, let's look for FoxPlayer type
                from src.game.entities.players.FoxPlayer import FoxPlayer
                if isinstance(entity, FoxPlayer):
                    # Already spawned in the loop above! 
                    # If the loop above didn't find one, we'll hit this block.
                    # Wait, FoxPlayer is spawned via 'START' in registry.
                    # Let's check the level data directly to be safe.
                    pass
            
            # Re-spawn if none found
            if not self.player:
                self.player = self.resources.spawn('START', start_pos[0], start_pos[1])

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            # Update
            self.platforms.update()
            self.player.update(self.platforms, self.effect_manager, self.items, entities=self.entities, resources=self.resources)
            self.entities.update(self.platforms, player=self.player, effect_manager=self.effect_manager)
            self.effect_manager.update()
            
            # Bullet Collisions
            for bullet in self.effect_manager.bullets:
                hits = pygame.sprite.spritecollide(bullet, self.entities, False)
                for enemy in hits:
                    if enemy != bullet.owner and hasattr(enemy, 'take_damage'):
                        enemy.take_damage(bullet.damage, bullet.direction)
                        bullet.kill()
                        break
                if not bullet.alive(): continue
                if bullet.owner != self.player and bullet.rect.colliderect(self.player.rect):
                    self.player.take_damage(bullet.damage, bullet.rect)
                    bullet.kill()
                    continue
                if pygame.sprite.spritecollideany(bullet, self.platforms):
                    bullet.kill()

            # Player-Enemy Collisions
            enemy_hits = pygame.sprite.spritecollide(self.player, self.entities, False)
            for enemy in enemy_hits:
                if isinstance(enemy, ExplodingTile): continue
                if hasattr(enemy, 'damage'):
                    self.player.take_damage(enemy.damage, enemy.rect)

            self.camera.update(self.player, self.effect_manager.get_shake_offset())

            # Draw to world_surface
            self.world_surface.fill((0, 0, 0)) # Clear
            self.parallax_manager.draw(self.world_surface, self.camera.camera.x)
            for sprite in self.background_statics: self.world_surface.blit(sprite.image, self.camera.apply(sprite))
            for item in self.items: self.world_surface.blit(item.image, self.camera.apply(item))
            
            for entity in self.entities: 
                if hasattr(entity, 'draw'): entity.draw(self.world_surface, self.camera)
                else: self.world_surface.blit(entity.image, self.camera.apply(entity))
            
            for platform in self.platforms:
                if platform not in self.entities and platform not in self.background_statics and platform not in self.foreground_statics:
                    if hasattr(platform, 'draw'): platform.draw(self.world_surface, self.camera)
                    else: self.world_surface.blit(platform.image, self.camera.apply(platform))

            self.effect_manager.draw(self.world_surface, self.camera)
            self.player.draw(self.world_surface, self.camera)
            for sprite in self.foreground_statics: self.world_surface.blit(sprite.image, self.camera.apply(sprite))
            
            # UI (Drawn to world_surface so it gets filtered too)
            self.ui_manager.draw_health_bar(self.world_surface, 20, 20, self.player.hp, self.player.max_hp, width_in_segments=6)
            active_weapon = self.player.weapon_slots[self.player.active_slot]
            if active_weapon:
                self.ui_manager.draw_ammo(self.world_surface, 20, 65, active_weapon.current_ammo, active_weapon.ammo_capacity)
            
            # Apply Filters
            final_view = self.world_surface
            if self.metadata.get("filters", {}).get("noir", False):
                final_view = pygame.transform.grayscale(self.world_surface)
            
            self.screen.blit(final_view, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    # Add root to sys.path
    sys.path.append(os.getcwd())
    level = sys.argv[1] if len(sys.argv) > 1 else "level_0"
    if level.endswith('.json'): level = level[:-5]
    elif level.endswith('.csv'): level = level[:-4]
    
    game = Game(level)
    game.run()
