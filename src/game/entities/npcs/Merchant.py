import pygame
import os
from src.engine.core.PhysicsEntity import PhysicsEntity
from src.engine.graphics.AnimationManager import AnimationManager

class Merchant(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.load_animations()
        self.rect = self.animations.get_current_frame().get_rect(topleft=(x, y))

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Characters", "Merchant")
        frames = {'idle': []}
        # Assuming Merchant has an idle.png
        img_path = os.path.join(path, "idle.png")
        if not os.path.exists(img_path):
            # Fallback to walk1 or similar if exists
            img_path = os.path.join(path, "walk1.png")
            
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert_alpha()
            frames['idle'].append(pygame.transform.scale(img, (36, 36)))
        else:
            surf = pygame.Surface((36, 36))
            surf.fill((0, 255, 0))
            frames['idle'].append(surf)
            
        self.animations = AnimationManager(frames)

    def update(self, platforms, **kwargs):
        self.apply_physics(platforms)
        self.animations.update()
        self.image = self.animations.get_current_frame()

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
