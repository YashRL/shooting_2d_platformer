import pygame
import math

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = properties.get('tile_size', 36)
        self.speed = properties.get('speed', 2.0)
        self.nodes = properties.get('nodes', [(x, y)]) # List of (x, y) coordinates
        
        raw_loop = properties.get('loop', True)
        if isinstance(raw_loop, str):
            self.loop = raw_loop.lower() == 'true'
        else:
            self.loop = bool(raw_loop)
        
        # Load images
        self.image = pygame.Surface((self.tile_size * 2, self.tile_size), pygame.SRCALPHA)
        try:
            img6 = pygame.image.load("Assets/PNG/Tiles/Tiles/Green_Grass/6.png").convert_alpha()
            img8 = pygame.image.load("Assets/PNG/Tiles/Tiles/Green_Grass/8.png").convert_alpha()
            img6 = pygame.transform.scale(img6, (self.tile_size, self.tile_size))
            img8 = pygame.transform.scale(img8, (self.tile_size, self.tile_size))
            self.image.blit(img6, (0, 0))
            self.image.blit(img8, (self.tile_size, 0))
        except:
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        
        self.current_node_idx = 0
        self.target_node_idx = 1 if len(self.nodes) > 1 else 0
        self.moving_forward = True

    def update(self, *args, **kwargs):
        if len(self.nodes) < 2:
            return

        old_pos = pygame.Vector2(self.pos)
        target = pygame.Vector2(self.nodes[self.target_node_idx])
        direction = target - self.pos
        distance = direction.length()

        if distance > 0:
            direction.normalize_ip()
            move_step = direction * self.speed
            if move_step.length() > distance:
                self.pos = target
                self.advance_node()
            else:
                self.pos += move_step
        else:
            self.advance_node()

        self.vel = self.pos - old_pos
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def advance_node(self):
        if self.moving_forward:
            if self.target_node_idx + 1 < len(self.nodes):
                self.target_node_idx += 1
            else:
                if self.loop:
                    self.target_node_idx = 0
                else:
                    self.moving_forward = False
                    self.target_node_idx -= 1
        else:
            if self.target_node_idx - 1 >= 0:
                self.target_node_idx -= 1
            else:
                self.moving_forward = True
                self.target_node_idx += 1

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
