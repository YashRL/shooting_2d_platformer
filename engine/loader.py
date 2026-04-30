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
        # 1. Load explicit entities from JSON (Players, Enemies, Weapons)
        with open('data/registry.json', 'r') as f:
            data = json.load(f)
            self.registry = data['items']
            self.settings = data.get('settings', {})

        # 2. Auto-discover organized tiles and props
        base_tiles_path = os.path.join("Assets", "PNG", "Tiles", "Tiles")
        
        # Mapping folders to Categories and Physics Types
        groups = {
            'Concrete_platform': ('Concrete', 'static'),
            'Foundation_tiles': ('Foundation', 'static'),
            'Green_Grass': ('Green Grass', 'static'),
            'Purple_Grass': ('Purple Grass', 'static'),
            'Props': ('Props', 'decor'),
            'Clouds': ('Props', 'decor')
        }

        for folder, (cat, p_type) in groups.items():
            path = os.path.join(base_tiles_path, folder)
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.endswith('.png'):
                        item_id = f.split('.')[0]
                        # Use a prefix to avoid ID collisions if necessary, or just the number
                        # To keep CSV simple, let's use the number. 
                        # NOTE: If numbers overlap between folders, we should use 'Folder_ID'
                        full_id = f"{folder}_{item_id}" 
                        
                        damage_val = 1 if cat == 'Purple Grass' else 0
                        if damage_val > 0:
                            print(f"[DEBUG] Tile {full_id} assigned damage: {damage_val}")
                        
                        self.registry[full_id] = {
                            'category': cat,
                            'name': f"{cat} {item_id}",
                            'asset': os.path.join(path, f),
                            'type': p_type,
                            'parallax_factor': 1.0,
                            'damage': damage_val
                        }

        # 3. Pre-load images
        for item_id, info in self.registry.items():
            # Ensure parallax_factor exists for JSON-loaded items too
            if 'parallax_factor' not in info:
                info['parallax_factor'] = 1.0
            
            try:
                img = pygame.image.load(info['asset']).convert_alpha()
                img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                self.images[item_id] = img
            except Exception as e:
                print(f"Error loading asset {info['asset']}: {e}")
                surf = pygame.Surface((self.tile_size, self.tile_size))
                surf.fill((255, 0, 255))
                self.images[item_id] = surf

    def spawn(self, item_id, x, y, **kwargs):
        # Handle per-instance properties: ID[prop1:val1,prop2:val2]
        instance_props = {}
        actual_id = item_id
        if '[' in item_id and item_id.endswith(']'):
            actual_id = item_id.split('[')[0]
            props_str = item_id.split('[')[1][:-1]
            # Handle both legacy ';' and new '&'
            for pair in props_str.replace(';', '&').split('&'):
                if ':' in pair:
                    k, v = pair.split(':')
                    # Parse specific types if needed
                    if k == 'nodes':
                        # nodes:x1,y1|x2,y2
                        nodes = []
                        for node_str in v.split('|'):
                            if ',' in node_str:
                                nx, ny = node_str.split(',')
                                nodes.append((int(nx), int(ny)))
                        instance_props[k] = nodes
                    elif k == 'speed':
                        instance_props[k] = float(v)
                    else:
                        instance_props[k] = v

        if actual_id not in self.registry: return None
        info = self.registry[actual_id]
        if info['type'] in ['static', 'decor']: return None
            
        module_path = info.get('module')
        class_name = info.get('class')
        if not module_path or not class_name: return None

        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            properties = info.get('properties', {}).copy()
            properties.update(instance_props)
            properties.update(kwargs)
            return cls(x, y, properties)
        except Exception as e:
            print(f"Failed to spawn {actual_id}: {e}")
            return None

    def get_image(self, item_id):
        actual_id = item_id.split('[')[0] if '[' in item_id else item_id
        return self.images.get(actual_id)
