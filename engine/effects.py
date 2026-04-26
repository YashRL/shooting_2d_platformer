import pygame
import random
import math

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.right < -1000 or self.rect.left > 5000:
            self.kill()

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

class EffectManager:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.shake_amount = 0
        self.shake_timer = 0
        
        # Load bullet asset once
        bullet_path = "Assets/PNG/Weapons/Tiles/bullet.png"
        self.bullet_img = pygame.image.load(bullet_path).convert_alpha()
        self.bullet_img = pygame.transform.scale(self.bullet_img, (12, 12))

    def trigger_shake(self, duration, amount):
        self.shake_timer = pygame.time.get_ticks() + duration
        self.shake_amount = amount

    def get_shake_offset(self):
        if pygame.time.get_ticks() < self.shake_timer:
            return (random.randint(-self.shake_amount, self.shake_amount),
                    random.randint(-self.shake_amount, self.shake_amount))
        return (0, 0)

    def create_muzzle_flash(self, x, y, direction):
        for _ in range(8):
            vel_x = direction * random.uniform(2, 6)
            vel_y = random.uniform(-2, 2)
            lifetime = random.randint(100, 400)
            color = random.choice([(255, 220, 0), (255, 255, 255), (255, 150, 0)])
            self.particles.add(Particle(x, y, color, (vel_x, vel_y), lifetime))

    def spawn_bullet(self, x, y, direction, speed, damage):
        bullet = Bullet(x, y, direction, speed, damage, self.bullet_img)
        self.bullets.add(bullet)
        return bullet

    def update(self):
        self.particles.update()
        self.bullets.update()

    def draw(self, screen, camera):
        for p in self.particles:
            screen.blit(p.image, camera.apply(p))
        for b in self.bullets:
            screen.blit(b.image, camera.apply(b))
