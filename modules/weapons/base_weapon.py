import pygame

class BaseWeapon(pygame.sprite.Sprite):
    def __init__(self, x, y, properties):
        super().__init__()
        # Essential stats from registry
        self.item_id = properties.get('item_id', 'P') 
        self.properties = properties
        self.ammo_capacity = properties.get('ammo_capacity', 10)
        self.reload_speed = properties.get('reload_speed', 1.0)
        self.fire_rate = properties.get('fire_rate', 0.5)
        self.damage = properties.get('damage', 10)
        self.shoot_type = properties.get('shoot_type', 'single')
        self.bullet_speed = properties.get('bullet_speed', 10)
        
        # Runtime state
        self.current_ammo = self.ammo_capacity
        self.last_fire_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        
        # Visuals (handled by subclass)
        self.image = pygame.Surface((36, 36))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        if self.is_reloading:
            now = pygame.time.get_ticks()
            if (now - self.reload_start_time) / 1000.0 >= self.reload_speed:
                self.current_ammo = self.ammo_capacity
                self.is_reloading = False

    def can_shoot(self):
        if self.is_reloading or self.current_ammo <= 0:
            return False
        now = pygame.time.get_ticks()
        if (now - self.last_fire_time) / 1000.0 >= self.fire_rate:
            return True
        return False

    def start_reload(self):
        if not self.is_reloading and self.current_ammo < self.ammo_capacity:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            return True
        return False
