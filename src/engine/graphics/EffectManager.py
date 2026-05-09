import pygame
import random
from src.engine.graphics.Particle import Particle
from src.engine.graphics.Projectile import Bullet, Rocket

class EffectManager:
    def __init__(self):
        self.particles = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.shake_amount = 0
        self.shake_timer = 0
        
        # Load bullet assets
        self.bullet_img = self.load_and_scale("Assets/PNG/Weapons/Tiles/bullet.png", (12, 12))
        self.rocket_img = self.load_and_scale("Assets/PNG/Weapons/Tiles/ROCKET_LAUNCHER/Rocket.png", (24, 12))

    def load_and_scale(self, path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            surf = pygame.Surface(size)
            surf.fill((255, 0, 255))
            return surf

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

    def spawn_bullet(self, x, y, direction, speed, damage, owner=None):
        bullet = Bullet(x, y, direction, speed, damage, self.bullet_img, owner)
        self.bullets.add(bullet)
        return bullet

    def spawn_rocket(self, x, y, direction, speed, damage, entities, player, owner=None):
        rocket = Rocket(x, y, direction, speed, damage, self.rocket_img, self, entities, player, owner)
        self.bullets.add(rocket)
        return rocket

    def update(self):
        self.particles.update()
        self.bullets.update()

    def draw(self, screen, camera):
        for p in self.particles:
            screen.blit(p.image, camera.apply(p))
        for b in self.bullets:
            screen.blit(b.image, camera.apply(b))
