from src.game.weapons.BaseWeapon import BaseWeapon

class RocketLauncher(BaseWeapon):
    def __init__(self, x, y, properties):
        properties.setdefault('name', 'Rocket Launcher')
        properties.setdefault('damage', 5)
        properties.setdefault('fire_rate', 1500)
        properties.setdefault('bullet_speed', 8)
        properties.setdefault('ammo_capacity', 1)
        properties.setdefault('reload_speed', 3.0)
        properties.setdefault('shoot_type', 'rocket')
        super().__init__(x, y, properties)
