import pygame

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_size=36):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.gravity = 0.8
        self.on_ground = False
        self.terminal_velocity = 10

    def apply_physics(self, platforms):
        # Horizontal Movement & Collision
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self._handle_collisions(platforms, 'horizontal')

        # Vertical Movement (Gravity) & Collision
        self.vel.y = min(self.terminal_velocity, self.vel.y + self.gravity)
        self.pos.y += self.vel.y
        self.rect.y = round(self.pos.y)
        self.on_ground = False
        self._handle_collisions(platforms, 'vertical')

    def _handle_collisions(self, platforms, direction):
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.vel.x > 0: self.rect.right = sprite.rect.left
                    if self.vel.x < 0: self.rect.left = sprite.rect.right
                    self.pos.x = self.rect.x
                    self.vel.x = 0
                elif direction == 'vertical':
                    if self.vel.y > 0:
                        self.rect.bottom = sprite.rect.top
                        self.on_ground = True
                        self.vel.y = 0
                    elif self.vel.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.vel.y = 0
                    self.pos.y = self.rect.y
