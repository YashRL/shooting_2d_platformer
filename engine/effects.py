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

class Rocket(Bullet):
    def __init__(self, x, y, direction, speed, damage, image, effect_manager, entities, player):
        super().__init__(x, y, direction, speed, damage, image)
        self.effect_manager = effect_manager
        self.entities = entities
        self.player = player
        
        # Rotate image based on direction
        if direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        super().update()
        # Smoke trail
        if random.random() > 0.3:
            vel_x = -self.direction * random.uniform(1, 3)
            vel_y = random.uniform(-1, 1)
            color = random.choice([(100, 100, 100), (150, 150, 150), (200, 200, 200)])
            lifetime = random.randint(200, 500)
            self.effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))

    def kill(self):
        if self.alive():
            self.explode()
        super().kill()

    def explode(self):
        # Stronger camera shake for RPG
        self.effect_manager.trigger_shake(500, 15)
        
        # Red/Orange/White/Smoke particles
        for _ in range(40):
            vel_x = random.uniform(-10, 10)
            vel_y = random.uniform(-10, 10)
            lifetime = random.randint(600, 1800)
            color = random.choice([(255, 0, 0), (255, 150, 0), (255, 255, 255), (80, 80, 80)])
            self.effect_manager.particles.add(Particle(self.rect.centerx, self.rect.centery, color, (vel_x, vel_y), lifetime))
        
        # Damage logic: Check for entities in radius
        explosion_radius = 100
        for entity in self.entities:
            if hasattr(entity, 'take_damage') and entity != self:
                dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(entity.rect.center))
                if dist < explosion_radius:
                    entity.take_damage(self.damage, 1 if entity.rect.centerx > self.rect.centerx else -1)

        # Damage player if in radius
        if self.player:
            dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(self.player.rect.center))
            if dist < explosion_radius:
                self.player.take_damage(2, self.rect)
        
        print(f"[DEBUG] Rocket Exploded at {self.rect.center}")

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

    def spawn_bullet(self, x, y, direction, speed, damage):
        bullet = Bullet(x, y, direction, speed, damage, self.bullet_img)
        self.bullets.add(bullet)
        return bullet

    def spawn_rocket(self, x, y, direction, speed, damage, entities, player):
        rocket = Rocket(x, y, direction, speed, damage, self.rocket_img, self, entities, player)
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
