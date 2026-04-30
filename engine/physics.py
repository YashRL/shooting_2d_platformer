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
        # 1. Pre-sync with platform (Sticky & Carrying Logic)
        # Check slightly below the current position to catch platforms moving away
        self.rect.y += 6 
        for sprite in platforms:
            if sprite.rect.colliderect(self.rect):
                # ONLY stick if we aren't trying to jump up (vel.y < 0)
                if self.vel.y >= 0:
                    if hasattr(sprite, 'vel'):
                        self.pos.x += sprite.vel.x
                        self.pos.y += sprite.vel.y
                    
                    # Snap to top to prevent vibrating/slipping
                    self.rect.bottom = sprite.rect.top
                    self.pos.y = self.rect.y
                    self.vel.y = 0
                    self.on_ground = True
                break
        self.rect.y -= 6

        # 2. Horizontal Movement & Collision
        self.pos.x += self.vel.x
        self.rect.x = round(self.pos.x)
        self._handle_collisions(platforms, 'horizontal')

        # 3. Vertical Movement (Gravity) & Collision
        # Note: vel.y might have been reset to 0 by sticky logic above
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
                    elif self.vel.x < 0: self.rect.left = sprite.rect.right
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
                    self.rect.y = round(self.pos.y)
