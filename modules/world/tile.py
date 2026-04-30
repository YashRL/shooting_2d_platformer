import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, parallax_factor=1.0, damage=0):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.parallax_factor = parallax_factor
        self.damage = damage
        if self.damage > 0:
            print(f"[DEBUG] Created damaging Tile at {self.rect.topleft} with damage {self.damage}")
