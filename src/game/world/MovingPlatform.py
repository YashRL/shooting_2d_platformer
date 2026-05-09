import pygame

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = 36
        self.width_tiles = properties.get('width_tiles', 3)
        self.image = pygame.Surface((self.width_tiles * self.tile_size, self.tile_size), pygame.SRCALPHA)
        
        # Fill with tile asset repeated
        asset_path = properties.get('asset', "Assets/PNG/Tiles/Tiles/Concrete_platform/tile_0000.png")
        try:
            tile_img = pygame.image.load(asset_path).convert_alpha()
            tile_img = pygame.transform.scale(tile_img, (self.tile_size, self.tile_size))
            for i in range(self.width_tiles):
                self.image.blit(tile_img, (i * self.tile_size, 0))
        except:
            self.image.fill((100, 100, 100))
            
        self.rect = self.image.get_rect(topleft=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        
        self.nodes = properties.get('nodes', [])
        if not self.nodes:
            self.nodes = [(x, y), (x + 200, y)]
            
        self.current_node_idx = 0
        self.speed = properties.get('speed', 2.0)

    def update(self, *args, **kwargs):
        if not self.nodes: return
        
        target = pygame.Vector2(self.nodes[self.current_node_idx])
        diff = target - self.pos
        
        if diff.length() < self.speed:
            self.pos = target
            self.current_node_idx = (self.current_node_idx + 1) % len(self.nodes)
        else:
            self.vel = diff.normalize() * self.speed
            self.pos += self.vel
            
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
