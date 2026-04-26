import json
import os
import pygame
import importlib

class ResourceManager:
    def __init__(self, tile_size=36):
        self.tile_size = tile_size
        self.registry = {}
        self.images = {}
        self.load_registry()

    def load_registry(self):
        with open('data/registry.json', 'r') as f:
            data = json.load(f)
            self.registry = data['items']
            self.settings = data.get('settings', {})

        # Pre-load images
        for item_id, info in self.registry.items():
            try:
                img = pygame.image.load(info['asset']).convert_alpha()
                img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                self.images[item_id] = img
            except Exception as e:
                print(f"Error loading asset {info['asset']}: {e}")
                # Fallback placeholder
                surf = pygame.Surface((self.tile_size, self.tile_size))
                surf.fill((255, 0, 255))
                self.images[item_id] = surf

    def spawn(self, item_id, x, y, **kwargs):
        """Dynamic instantiation of modules based on the registry."""
        if item_id not in self.registry:
            return None
        
        info = self.registry[item_id]
        if info['type'] == 'static':
            return None # Tiles are handled separately for performance
            
        module_path = info.get('module')
        class_name = info.get('class')
        
        if not module_path or not class_name:
            return None

        try:
            # Dynamic Import
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            
            # Merge default properties from registry with any overrides
            properties = info.get('properties', {}).copy()
            properties.update(kwargs)
            
            return cls(x, y, properties)
        except Exception as e:
            print(f"Failed to spawn {item_id} at ({x}, {y}): {e}")
            return None

    def get_image(self, item_id):
        return self.images.get(item_id)
