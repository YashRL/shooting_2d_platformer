from src.game.weapons.BaseWeapon import BaseWeapon

class Pistol(BaseWeapon):
    def __init__(self, x, y, properties):
        # Stats are usually overridden by registry.json, these are defaults
        properties.setdefault('name', 'Pistol')
        properties.setdefault('damage', 1)
        properties.setdefault('fire_rate', 400)
        properties.setdefault('bullet_speed', 12)
        properties.setdefault('ammo_capacity', 8)
        properties.setdefault('reload_speed', 1.2)
        properties.setdefault('shoot_type', 'semi')
        super().__init__(x, y, properties)
