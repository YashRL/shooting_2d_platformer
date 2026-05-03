import pygame
import os

class Trampoline(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        self.tile_size = properties.get('tile_size', 36)
        self.jump_power = properties.get('jump_power', 18)
        
        # Animation states
        self.frames = {}
        try:
            up_img = pygame.image.load("Assets/PNG/Tiles/Tiles/Trampoline/up.png").convert_alpha()
            down_img = pygame.image.load("Assets/PNG/Tiles/Tiles/Trampoline/down.png").convert_alpha()
            self.frames['up'] = pygame.transform.scale(up_img, (self.tile_size, self.tile_size))
            self.frames['down'] = pygame.transform.scale(down_img, (self.tile_size, self.tile_size))
        except:
            # Fallback
            self.frames['up'] = pygame.Surface((self.tile_size, self.tile_size))
            self.frames['up'].fill((255, 255, 0))
            self.frames['down'] = pygame.Surface((self.tile_size, self.tile_size))
            self.frames['down'].fill((200, 200, 0))

        self.state = 'up'
        self.image = self.frames[self.state]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.animation_timer = 0
        self.animation_duration = 300 # ms
        
    def update(self, *args, **kwargs):
        player_obj = kwargs.get('player')
        
        if player_obj:
            # Detect if player is on top
            # Standard logic: if player is falling and their feet are at trampoline level
            detect_rect = self.rect.inflate(0, 10) 
            detect_rect.bottom = self.rect.top + 5
            
            if player_obj.rect.colliderect(detect_rect) and player_obj.vel.y >= 0:
                self.trigger_bounce(player_obj)

        # Animation reset (Always happens)
        if self.state == 'down':
            if pygame.time.get_ticks() - self.animation_timer > self.animation_duration:
                self.state = 'up'
                self.image = self.frames[self.state]

    def trigger_bounce(self, player):
        player.vel.y = -self.jump_power
        player.on_ground = False
        self.state = 'down'
        self.image = self.frames[self.state]
        self.animation_timer = pygame.time.get_ticks()
        print(f"[DEBUG] Trampoline launch! Power: {self.jump_power}")

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
