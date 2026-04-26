import os
import pygame

# Registry Categories
CAT_TILE = "Tiles"
CAT_ENEMY = "Enemies"
CAT_WEAPON = "Weapons"
CAT_PLAYER = "Player"
CAT_DECOR = "Decor"

# Base Item Registry for specialized objects
# This is what makes the system future-proof
ITEM_REGISTRY = {
    # Player Spawn
    'START': {
        'category': CAT_PLAYER,
        'name': 'Player Spawn',
        'image_path': os.path.join("Assets", "PNG", "Players", "Tiles", "fox", "walk1.png"),
        'layer': 1 # 0 for background/tiles, 1 for entities
    },
    
    # Weapons
    'P': {
        'category': CAT_WEAPON,
        'name': 'Pistol',
        'image_path': os.path.join("Assets", "PNG", "Weapons", "Tiles", "pistol.png"),
        'layer': 1
    },
    'CT': {
        'category': CAT_WEAPON,
        'name': 'Chicago Typewriter',
        'image_path': os.path.join("Assets", "PNG", "Weapons", "Tiles", "chicago_typwriter.png"),
        'layer': 1
    },
    
    # Enemies
    'E_I': {
        'category': CAT_ENEMY,
        'name': 'Insect',
        'image_path': os.path.join("Assets", "PNG", "Enemies", "Tiles", "Insect", "walk1.png"),
        'layer': 1
    },
    'E_b': {
        'category': CAT_ENEMY,
        'name': 'Bee',
        'image_path': os.path.join("Assets", "PNG", "Enemies", "Tiles", "Bee", "fly1.png"),
        'layer': 1
    }
}

def get_full_registry():
    """Returns the full registry including auto-discovered environment tiles."""
    full_registry = ITEM_REGISTRY.copy()
    
    # Auto-discover numeric environment tiles
    tiles_path = os.path.join("Assets", "PNG", "Tiles", "Tiles")
    if os.path.exists(tiles_path):
        for f in os.listdir(tiles_path):
            if f.endswith('.png'):
                try:
                    # If the filename is a number, it's a tile
                    tile_id = f.split('.')[0]
                    if tile_id.isdigit():
                        full_registry[tile_id] = {
                            'category': CAT_TILE,
                            'name': f"Tile {tile_id}",
                            'image_path': os.path.join(tiles_path, f),
                            'layer': 0
                        }
                except ValueError:
                    continue
                    
    return full_registry

def load_registry_images(tile_size):
    """Loads and scales all images from the registry."""
    registry = get_full_registry()
    images = {}
    for item_id, data in registry.items():
        try:
            img = pygame.image.load(data['image_path']).convert_alpha()
            img = pygame.transform.scale(img, (tile_size, tile_size))
            images[item_id] = img
        except Exception as e:
            print(f"Warning: Could not load image for {item_id}: {e}")
            # Create a placeholder if image fails
            surf = pygame.Surface((tile_size, tile_size))
            surf.fill((255, 0, 255)) # Magenta placeholder
            images[item_id] = surf
    return images
