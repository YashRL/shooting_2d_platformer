import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, lifetime):
        super().__init__()
        size = random.randint(2, 4)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = velocity
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if pygame.time.get_ticks() - self.start_time > self.lifetime:
            self.kill()
