import pygame
import os
from engine.physics import PhysicsEntity
from engine.animation import AnimationManager

class Merchant(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.tile_size = 36
        
        self.load_animations()
        self.rect = self.animations.get_current_frame().get_rect(topleft=(x, y))

    def load_animations(self):
        # Using the base_idle frames provided by the user
        path = os.path.join("Assets", "PNG", "Characters", "Merchant", "frames", "base_idle")
        frames = {'idle': []}
        
        # Load all 8 frames for idle
        for i in range(1, 9):
            img_path = os.path.join(path, f"{i}.png")
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                # Scaling to tile_size to match engine standards
                frames['idle'].append(pygame.transform.scale(img, (self.tile_size, self.tile_size)))
        
        self.animations = AnimationManager(frames)
        self.animations.change_state('idle')

    def update(self, platforms, **kwargs):
        # Merchant is harmless and stationary, but still needs basic physics (gravity)
        self.apply_physics(platforms)
        self.animations.update()
        self.image = self.animations.get_current_frame()

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
