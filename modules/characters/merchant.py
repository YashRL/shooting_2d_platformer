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
        # Initialize rect using the position set by PhysicsEntity
        self.rect = self.animations.get_current_frame().get_rect(topleft=(self.pos.x, self.pos.y))
        # Shrink height so physics brings the feet all the way to the tile
        self.rect.height = 30 

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Characters", "Merchant", "frames", "base_idle_styled")
        frames = {'idle': []}
        
        for i in range(1, 9):
            img_path = os.path.join(path, f"{i}.png")
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                frames['idle'].append(pygame.transform.scale(img, (self.tile_size, self.tile_size)))
        
        # Very slow animation speed
        self.animation_speed = 0.03
        self.animations = AnimationManager(frames, animation_speed=self.animation_speed)
        self.animations.change_state('idle')

    def update(self, platforms, **kwargs):
        self.apply_physics(platforms)
        self.animations.update()
        self.image = self.animations.get_current_frame()

    def draw(self, screen, camera):
        # Draw with a 6-pixel downward offset to compensate for the 32x32 transparent padding
        # and ensure the feet touch the ground.
        pos = camera.apply(self)
        pos.y += 6
        screen.blit(self.image, pos)
