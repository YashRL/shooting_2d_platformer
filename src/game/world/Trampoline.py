import pygame
import os
from src.engine.graphics.AnimationManager import AnimationManager

class Trampoline(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = 36
        self.jump_boost = properties.get('boost', -18)
        self.load_animations()
        self.image = self.animations.animations['idle'][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_active = False

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Tiles", "Tiles", "Props")
        frames = {'idle': [], 'boing': []}
        # Assuming trampoline frames exist or use placeholders
        img = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(img, (0, 200, 0), (0, 20, 36, 16))
        frames['idle'].append(img)
        
        img2 = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(img2, (0, 255, 0), (0, 10, 36, 26))
        frames['boing'].append(img2)
        frames['boing'].append(img) # Loop back to idle
        
        self.animations = AnimationManager(frames, animation_speed=0.2)

    def update(self, *args, **kwargs):
        player = kwargs.get('player')
        if player and player.rect.colliderect(self.rect) and player.vel.y > 0:
            if player.rect.bottom <= self.rect.top + 10:
                player.vel.y = self.jump_boost
                player.on_ground = False
                self.animations.change_state('boing')
                print("[DEBUG] Trampoline Boing!")

        self.animations.update()
        self.image = self.animations.get_current_frame()
        if self.animations.state == 'boing' and self.animations.frame_index == 0:
            self.animations.change_state('idle')
