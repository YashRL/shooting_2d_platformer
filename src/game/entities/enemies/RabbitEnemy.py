import pygame
import os
import random
from src.game.entities.enemies.BaseEnemy import BaseEnemy
from src.engine.graphics.AnimationManager import AnimationManager

class RabbitEnemy(BaseEnemy):
    def __init__(self, x, y, properties):
        super().__init__(x, y, properties)
        self.load_animations()
        self.personality_timer = 0
        self.personality_state = 'idle' # 'idle', 'taunt', 'dodge'
        self.jump_force = -10

    def load_animations(self):
        variant = self.properties.get('variant', 'big')
        folder_name = "big_rabit" if variant == 'big' else "Tiny_rabit"
        path = os.path.join("Assets", "PNG", "Enemies", "Tiles", folder_name)
        frames = {'idle': [], 'walk': [], 'jump': [], 'taunt': [], 'dodge': []}
        
        # Mapping: state -> file_prefix
        # Some assets might have different names, let's try to be flexible
        def load_frame(name, fallback=None):
            p = os.path.join(path, name)
            if not os.path.exists(p) and fallback:
                p = os.path.join(path, fallback)
            if os.path.exists(p):
                return pygame.transform.scale(pygame.image.load(p).convert_alpha(), (36, 36))
            return None

        # Idle
        img = load_frame("idle.png", "walk_1.png")
        if img: frames['idle'].append(img)
        
        # Walk
        for name in ["walk_1.png", "walk_2.png"]:
            img = load_frame(name)
            if img: frames['walk'].append(img)
            
        # Jump
        img = load_frame("jump.png", "walk_1.png")
        if img: frames['jump'].append(img)
        
        # Taunt
        img = load_frame("taunt.png", "walk_2.png")
        if img: frames['taunt'].append(img)
        
        # Dodge
        img = load_frame("dodge.png", "walk_1.png")
        if img: frames['dodge'].append(img)
        
        self.animations = AnimationManager(frames)

    def handle_ai(self, player):
        if not player: return
        
        dist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(player.rect.center))
        
        # Erratic state switching
        if pygame.time.get_ticks() > self.personality_timer:
            if dist < 150:
                self.personality_state = random.choice(['dodge', 'taunt', 'walk'])
            else:
                self.personality_state = random.choice(['idle', 'walk'])
            self.personality_timer = pygame.time.get_ticks() + random.randint(1000, 3000)

        if self.personality_state == 'walk':
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self.vel.x = self.direction * self.speed
            if self.on_ground and random.random() < 0.02:
                self.vel.y = self.jump_force
        elif self.personality_state == 'dodge':
            # Move AWAY from player
            self.direction = -1 if player.rect.centerx > self.rect.centerx else 1
            self.vel.x = self.direction * (self.speed * 1.5)
            if self.on_ground: self.vel.y = self.jump_force * 0.7
        elif self.personality_state == 'taunt':
            self.vel.x = 0
            self.direction = 1 if player.rect.centerx > self.rect.centerx else -1
        else:
            self.vel.x = 0

    def update(self, platforms, player=None, **kwargs):
        if not self.is_hit:
            self.handle_ai(player)
            
        self.apply_physics(platforms)
        
        # Animation State
        if not self.on_ground: self.animations.change_state('jump')
        elif self.personality_state == 'taunt': self.animations.change_state('taunt')
        elif self.personality_state == 'dodge': self.animations.change_state('dodge')
        elif self.vel.x != 0: self.animations.change_state('walk')
        else: self.animations.change_state('idle')
        
        super().update(platforms, player=player, **kwargs)
