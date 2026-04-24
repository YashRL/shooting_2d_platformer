import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, lifetime):
        super().__init__()
        self.image = pygame.Surface((4, 4))
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

class EffectManager:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.shake_amount = 0
        self.shake_timer = 0

    def create_muzzle_flash(self, x, y, direction):
        for _ in range(5):
            vel_x = direction * random.uniform(2, 5)
            vel_y = random.uniform(-1, 1)
            lifetime = random.randint(100, 300)
            color = random.choice([(255, 200, 0), (255, 255, 255), (255, 100, 0)])
            p = Particle(x, y, color, (vel_x, vel_y), lifetime)
            self.particles.add(p)

    def trigger_shake(self, duration, amount):
        self.shake_timer = pygame.time.get_ticks() + duration
        self.shake_amount = amount

    def get_shake_offset(self):
        if pygame.time.get_ticks() < self.shake_timer:
            return (random.randint(-self.shake_amount, self.shake_amount),
                    random.randint(-self.shake_amount, self.shake_amount))
        return (0, 0)

    def update(self):
        self.particles.update()

    def draw(self, screen, camera):
        for p in self.particles:
            screen.blit(p.image, camera.apply(p))
