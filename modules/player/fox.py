import pygame
import os
import math
from engine.physics import PhysicsEntity
from engine.animation import AnimationManager

class FoxPlayer(PhysicsEntity):
    def __init__(self, x, y, properties):
        super().__init__(x, y)
        self.properties = properties
        self.tile_size = 36
        
        # Stats
        self.hp = 5
        self.max_hp = 5
        self.speed = 5
        self.jump_force = -math.sqrt(2 * self.gravity * (3.5 * self.tile_size))
        
        # Weapons System
        self.weapon_slots = [None, None]
        self.active_slot = 0
        
        # Hit State
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 500 # Invincibility frames
        
        self.jump_pressed_last_frame = False
        self.is_jumping = False
        self.interact_pressed = False
        
        self.load_animations()
        self.rect = self.animations.get_current_frame().get_rect(topleft=(x, y))

    def load_animations(self):
        path = os.path.join("Assets", "PNG", "Players", "Tiles", "fox")
        frames = {'idle': [], 'walk': [], 'jump': []}
        img = pygame.image.load(os.path.join(path, "walk1.png")).convert_alpha()
        frames['idle'].append(pygame.transform.scale(img, (self.tile_size, self.tile_size)))
        for name in ["walk1.png", "walk2.png"]:
            img = pygame.image.load(os.path.join(path, name)).convert_alpha()
            frames['walk'].append(pygame.transform.scale(img, (self.tile_size, self.tile_size)))
        img = pygame.image.load(os.path.join(path, "jump.png")).convert_alpha()
        frames['jump'].append(pygame.transform.scale(img, (self.tile_size, self.tile_size)))
        self.animations = AnimationManager(frames)

    def take_damage(self, amount, source_rect):
        if self.is_hit: return
        
        self.hp -= amount
        self.is_hit = True
        self.hit_timer = pygame.time.get_ticks()
        
        # Knockback
        knockback_force = 8
        if source_rect.centerx < self.rect.centerx:
            self.vel.x = knockback_force
        else:
            self.vel.x = -knockback_force
        self.vel.y = -6
        self.on_ground = False
        
        if self.hp <= 0:
            # Simple Respawn
            self.hp = self.max_hp
            self.pos = pygame.Vector2(100, 100)
            self.rect.topleft = (100, 100)

    def handle_input(self, effect_manager, items_group, resources=None):
        if self.is_hit and pygame.time.get_ticks() - self.hit_timer < 200: 
            return # Locked out of input during initial knockback

        keys = pygame.key.get_pressed()
        jump_input = keys[pygame.K_w]
        
        self.vel.x = 0
        if keys[pygame.K_a]:
            self.vel.x = -self.speed
            self.animations.flip = True
        if keys[pygame.K_d]:
            self.vel.x = self.speed
            self.animations.flip = False

        if jump_input:
            if self.on_ground and not self.jump_pressed_last_frame:
                self.vel.y = self.jump_force
                self.is_jumping = True
            elif self.is_jumping and self.vel.y < 0:
                self.vel.y -= self.gravity * 0.45
        else: self.is_jumping = False
        self.jump_pressed_last_frame = jump_input

        # Weapons... (1, 2, R, Space, E)
        if keys[pygame.K_1]: self.active_slot = 0
        if keys[pygame.K_2]: self.active_slot = 1
        if keys[pygame.K_r]:
            w = self.weapon_slots[self.active_slot]
            if w: w.start_reload()
        
        weapon = self.weapon_slots[self.active_slot]
        if weapon:
            shoot_input = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
            if shoot_input:
                if weapon.shoot_type == 'auto' or not getattr(self, 'shoot_pressed_last_frame', False):
                    self.shoot(weapon, effect_manager)
                self.shoot_pressed_last_frame = True
            else: self.shoot_pressed_last_frame = False

        if keys[pygame.K_e]:
            if not self.interact_pressed:
                if resources:
                    self.check_pickup(items_group, resources)
                self.interact_pressed = True
        else: self.interact_pressed = False

    def shoot(self, weapon, effect_manager):
        if weapon.can_shoot():
            direction = -1 if self.animations.flip else 1
            offset_x = -20 if self.animations.flip else 20
            muzzle_x = self.rect.centerx + offset_x
            muzzle_y = self.rect.centery + 5
            effect_manager.trigger_shake(100, 4)
            effect_manager.create_muzzle_flash(muzzle_x, muzzle_y, direction)
            effect_manager.spawn_bullet(muzzle_x, muzzle_y, direction, weapon.bullet_speed, weapon.damage)
            weapon.current_ammo -= 1
            weapon.last_fire_time = pygame.time.get_ticks()

    def check_pickup(self, items_group, resources):
        hits = pygame.sprite.spritecollide(self, items_group, False)
        for item in hits:
            for i in range(2):
                if self.weapon_slots[i] is None:
                    weapon_logic = resources.spawn(item.item_id, 0, 0)
                    if weapon_logic:
                        self.weapon_slots[i] = weapon_logic
                        item.kill()
                        return

    def update(self, platforms, effect_manager=None, items_group=None, **kwargs):
        if self.is_hit:
            if pygame.time.get_ticks() - self.hit_timer > self.hit_duration:
                self.is_hit = False
                
        resources = kwargs.get('resources')
        self.handle_input(effect_manager, items_group, resources)
        self.apply_physics(platforms)
        
        weapon = self.weapon_slots[self.active_slot]
        if weapon: weapon.update()
            
        if not self.on_ground: self.animations.change_state('jump')
        elif self.vel.x != 0: self.animations.change_state('walk')
        else: self.animations.change_state('idle')
        
        self.animations.flash_red = self.is_hit
        self.animations.update()
        self.image = self.animations.get_current_frame()

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self))
        weapon = self.weapon_slots[self.active_slot]
        if weapon:
            w_img = weapon.image
            if self.animations.flip: w_img = pygame.transform.flip(w_img, True, False)
            offset_x = -10 if self.animations.flip else 10
            w_rect = w_img.get_rect(center=self.rect.center)
            w_rect.x += offset_x
            w_rect.y += 5
            screen.blit(w_img, camera.apply_rect(w_rect))
            if weapon.is_reloading:
                elapsed = (pygame.time.get_ticks() - weapon.reload_start_time) / 1000.0
                progress = min(1.0, elapsed / weapon.reload_speed)
                pos = camera.apply_rect(w_rect).center
                pygame.draw.circle(screen, (50, 50, 50), pos, 5, 1)
                pygame.draw.arc(screen, (255, 255, 0), (pos[0]-5, pos[1]-5, 10, 10), -math.pi/2, progress*2*math.pi - math.pi/2, 2)

    def draw_hud(self, screen):
        font = pygame.font.SysFont("Arial", 20, bold=True)
        # HP and Ammo are now handled by UIManager bar and icon
