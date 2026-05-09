import pygame

class BaseWeapon:
    def __init__(self, x, y, properties):
        self.x = x
        self.y = y
        self.name = properties.get('name', 'Unknown')
        self.damage = properties.get('damage', 1)
        self.fire_rate = properties.get('fire_rate', 500) # ms
        self.bullet_speed = properties.get('bullet_speed', 10)
        self.ammo_capacity = properties.get('ammo_capacity', 10)
        self.current_ammo = self.ammo_capacity
        self.reload_speed = properties.get('reload_speed', 1.5) # seconds
        self.shoot_type = properties.get('shoot_type', 'semi') # semi, auto, rocket
        
        self.last_fire_time = 0
        self.is_reloading = False
        self.reload_start_time = 0
        
        # Image
        self.image = None
        asset_path = properties.get('asset')
        if asset_path:
            self.image = pygame.image.load(asset_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((200, 200, 200))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return not self.is_reloading and self.current_ammo > 0 and now - self.last_fire_time > self.fire_rate

    def start_reload(self):
        if not self.is_reloading and self.current_ammo < self.ammo_capacity:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            print(f"[DEBUG] {self.name} Reloading...")

    def update(self):
        if self.is_reloading:
            now = pygame.time.get_ticks()
            if now - self.reload_start_time > self.reload_speed * 1000:
                self.current_ammo = self.ammo_capacity
                self.is_reloading = False
                print(f"[DEBUG] {self.name} Reloaded!")
