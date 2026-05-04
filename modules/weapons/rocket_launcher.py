from .base_weapon import BaseWeapon
import pygame
import os

class RocketLauncher(BaseWeapon):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "ROCKET_LAUNCHER", "RPG.png")
        try:
            self.image = pygame.image.load(path).convert_alpha()
            # The RPG looks like it might be bigger than 36x36, but let's scale it to fit the hand reasonably
            self.image = pygame.transform.scale(self.image, (42, 24))
        except Exception as e:
            print(f"Error loading Rocket Launcher asset: {e}")
            self.image = pygame.Surface((36, 18))
            self.image.fill((100, 100, 100))
