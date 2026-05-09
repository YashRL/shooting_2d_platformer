from src.game.weapons.BaseWeapon import BaseWeapon

class SMG(BaseWeapon):
    def __init__(self, x, y, properties):
        properties.setdefault('name', 'SMG')
        properties.setdefault('damage', 1)
        properties.setdefault('fire_rate', 100)
        properties.setdefault('bullet_speed', 15)
        properties.setdefault('ammo_capacity', 30)
        properties.setdefault('reload_speed', 2.0)
        properties.setdefault('shoot_type', 'auto')
        super().__init__(x, y, properties)
