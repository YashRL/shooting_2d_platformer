from .base_weapon import BaseWeapon
import pygame
import os

class SMG(BaseWeapon):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "chicago_typwriter.png")
        self.image = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (36, 36))
