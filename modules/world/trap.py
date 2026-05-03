import pygame
import math

class ThrowingKnife(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = properties.get('tile_size', 36)
        self.direction = properties.get('direction', 'UP').upper()
        self.speed = properties.get('speed', 10)
        self.damage = properties.get('damage', 1)
        self.detection_range = self.tile_size * 5
        
        self.triggered = False
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        
        # Load and rotate asset
        asset_path = properties.get('asset', "Assets/PNG/Throw/Knife.png")
        try:
            self.original_image = pygame.image.load(asset_path).convert_alpha()
            # Scaling depends on asset size, assuming it fits tile_size
            self.original_image = pygame.transform.scale(self.original_image, (self.tile_size, self.tile_size))
        except:
            self.original_image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, (200, 200, 200), [(18, 0), (25, 36), (11, 36)]) # Fallback triangle
            
        # Set rotation and velocity vector
        angle = 0
        if self.direction == "UP":
            angle = 0
            self.velocity = pygame.Vector2(0, -self.speed)
            self.ray_rect = pygame.Rect(x + self.tile_size//4, y - self.detection_range, self.tile_size//2, self.detection_range)
        elif self.direction == "DOWN":
            angle = 180
            self.velocity = pygame.Vector2(0, self.speed)
            self.ray_rect = pygame.Rect(x + self.tile_size//4, y + self.tile_size, self.tile_size//2, self.detection_range)
        elif self.direction == "LEFT":
            angle = 90
            self.velocity = pygame.Vector2(-self.speed, 0)
            self.ray_rect = pygame.Rect(x - self.detection_range, y + self.tile_size//4, self.detection_range, self.tile_size//2)
        elif self.direction == "RIGHT":
            angle = 270
            self.velocity = pygame.Vector2(self.speed, 0)
            self.ray_rect = pygame.Rect(x + self.tile_size, y + self.tile_size//4, self.detection_range, self.tile_size//2)
            
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(topleft=(x, y))
        
    def update(self, platforms, *args, **kwargs):
        player = kwargs.get('player')
        
        if not self.triggered:
            # Check detection
            if player and self.ray_rect.colliderect(player.rect):
                self.triggered = True
                print(f"[DEBUG] Trap triggered! Direction: {self.direction}")
        else:
            # Move
            self.pos += self.velocity
            self.rect.topleft = (self.pos.x, self.pos.y)
            
            # Check player collision
            if player and self.rect.colliderect(player.rect):
                player.take_damage(self.damage, self.rect)
                self.kill()
                
            # Check tile collision
            if pygame.sprite.spritecollideany(self, platforms):
                self.kill()
                
            # Kill if way off screen (approximate)
            if self.pos.x < -1000 or self.pos.x > 5000 or self.pos.y < -1000 or self.pos.y > 5000:
                self.kill()

    def draw(self, screen, camera):
        # Only draw if triggered
        if self.triggered:
            screen.blit(self.image, camera.apply(self))
        # Optional: Debug raycast
        # pygame.draw.rect(screen, (255, 0, 0), camera.apply_rect(self.ray_rect), 1)
