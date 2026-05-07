import json
import os
import pygame
import importlib

class ResourceManager:
    def __init__(self, tile_size=36):
        self.tile_size = tile_size
        self.registry = {}
        self.images = {}
        self.tinted_images = {}
        self.base_assets = {}   # Cache for ORIGINAL unscaled images
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
            'Purple_grass_v2': ('Purple Grass v2', 'static'),
            'Green_Grass_v2': ('Green Grass', 'static'),
            'Foundations_v2': ('Foundation', 'static'),
            'Danger_Tiles': ('Danger', 'static'),
            'Ice_Tiles': ('Ice', 'static'),
            'Mud_Tiles': ('Mud', 'static'),
            'Pipes': ('Pipes', 'static'),
            'Props': ('Props', 'decor'),
            'Clouds': ('Props', 'decor')
        }

        for folder, (cat, p_type) in groups.items():
            path = os.path.join(base_tiles_path, folder)
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.endswith('.png'):
                        item_id = f.split('.')[0]
                        full_id = f"{folder}_{item_id}" 
                        
                        direction = None
                        if folder == 'Pipes' and item_id in ['up', 'down', 'left', 'right']:
                            direction = item_id

                        damage_val = 1 if cat in ['Purple Grass', 'Purple Grass v2'] else 0
                        
                        self.registry[full_id] = {
                            'category': cat,
                            'name': f"{cat} {item_id}",
                            'asset': os.path.join(path, f),
                            'type': p_type,
                            'parallax_factor': 1.0,
                            'damage': damage_val
                        }
                        if direction:
                            self.registry[full_id]['direction'] = direction

        # 2b. Generate Tinted Blueprints (Scaling existing tilesets)
        # Structure: (Source Folder, Category Name, Registry Prefix, Tint, Damage, Extra Properties)
        blueprints = [
            ('Green_Grass', 'Danger', 'DANGER', [255, 100, 100], 5, {}),
            ('Green_Grass', 'Ice', 'ICE', [150, 200, 255], 0, {'friction': 0.05}),
            ('Green_Grass', 'Mud', 'MUD', [139, 69, 19], 0, {'friction': 0.8})
        ]

        for src_folder, cat, prefix, tint, dmg, extra_props in blueprints:
            src_path = os.path.join(base_tiles_path, src_folder)
            if os.path.exists(src_path):
                for f in os.listdir(src_path):
                    if f.endswith('.png'):
                        item_id = f.split('.')[0]
                        full_id = f"{prefix}_{item_id}"
                        
                        self.registry[full_id] = {
                            'category': cat,
                            'name': f"{cat} {item_id}",
                            'asset': os.path.join(src_path, f),
                            'type': 'static',
                            'parallax_factor': 1.0,
                            'damage': dmg,
                            'tint': tint,
                            'properties': extra_props
                        }

        # 3. Pre-load images (only once per unique asset + tint combination)
        for item_id, info in self.registry.items():
            if 'parallax_factor' not in info:
                info['parallax_factor'] = 1.0
            
            # Use asset path as key for base images to save memory
            asset_path = info['asset']
            if asset_path not in self.images:
                try:
                    # Load and store ORIGINAL unscaled asset
                    orig_img = pygame.image.load(asset_path).convert_alpha()
                    self.base_assets[asset_path] = orig_img
                    
                    # Store standard scaled version
                    scaled_img = pygame.transform.scale(orig_img, (self.tile_size, self.tile_size))
                    self.images[asset_path] = scaled_img
                except Exception as e:
                    print(f"Error loading asset {asset_path}: {e}")
                    surf = pygame.Surface((self.tile_size, self.tile_size))
                    surf.fill((255, 0, 255))
                    self.images[asset_path] = surf

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
                        # Auto-detect numeric types for generic properties like hp, damage, etc.
                        try:
                            if '.' in v:
                                instance_props[k] = float(v)
                            else:
                                instance_props[k] = int(v)
                        except ValueError:
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
            # Pass resources to the entity if it needs to spawn weapons/etc
            if 'resources' not in properties:
                properties['resources'] = self
            return cls(x, y, properties)
        except Exception as e:
            print(f"Failed to spawn {actual_id}: {e}")
            return None

    def get_image(self, item_id):
        # Handle instance properties (e.g., TILE_ID[tint:255,0,0])
        actual_id = item_id.split('[')[0] if '[' in item_id else item_id
        
        if actual_id not in self.registry:
            return None
            
        info = self.registry[actual_id]
        asset_path = info['asset']
        base_img = self.images.get(asset_path) # Pre-scaled base image
        
        if not base_img:
            return None

        # Determine Tint
        tint = info.get('tint') # From registry
        
        # Check for instance-level tint
        if '[' in item_id:
            props_str = item_id.split('[')[1][:-1]
            for pair in props_str.replace(';', '&').split('&'):
                if ':' in pair:
                    k, v = pair.split(':')
                    if k == 'tint':
                        try:
                            tint = [int(c) for c in v.split(',')]
                        except:
                            pass

        if not tint:
            return base_img

        # Create/Cache Tinted Version
        tint_key = f"{asset_path}_{tuple(tint)}"
        if tint_key not in self.tinted_images:
            # IMPORTANT: Recolor the ORIGINAL asset first for perfect pixel matching
            orig_surf = self.base_assets.get(asset_path)
            if not orig_surf:
                # Fallback if original somehow missing
                orig_surf = base_img 
                
            tinted_surf = orig_surf.copy()
            
            # 1. Define the Target Greens (Precise Hexes from User)
            # Light Greens
            target_light_1 = (157, 249, 228) # #9df9e4
            target_light_2 = (157, 248, 228) # #9df8e4
            
            # Medium Green
            target_med     = (123, 216, 196) # #7bd8c4
            
            # Dark Greens
            target_dark_1  = (98, 184, 167)  # #62b8a7
            target_dark_2  = (103, 188, 170) # #67bcaa
            
            # 2. Derive replacement shades
            base_col = pygame.Color(*tint)
            repl_med = base_col
            repl_light = pygame.Color(min(255, int(base_col.r * 1.2)), min(255, int(base_col.g * 1.2)), min(255, int(base_col.b * 1.2)))
            repl_dark  = pygame.Color(int(base_col.r * 0.8), int(base_col.g * 0.8), int(base_col.b * 0.8))

            pixels = pygame.PixelArray(tinted_surf)
            # Replace all variants of Light, Medium, and Dark greens
            pixels.replace(target_light_1, repl_light)
            pixels.replace(target_light_2, repl_light)
            pixels.replace(target_med, repl_med)
            pixels.replace(target_dark_1, repl_dark)
            pixels.replace(target_dark_2, repl_dark)
            del pixels
            
            # 4. NOW scale the perfectly recolored asset
            final_surf = pygame.transform.scale(tinted_surf, (self.tile_size, self.tile_size))
            self.tinted_images[tint_key] = final_surf
            
        return self.tinted_images[tint_key]

