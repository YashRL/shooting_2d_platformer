import pygame

class EditorCamera:
    def __init__(self, x_offset=0, y_offset=0, base_tile_size=36):
        self.offset = pygame.Vector2(x_offset, y_offset)
        self.zoom_level = 1.0
        self.base_tile_size = base_tile_size
        self.current_tile_size = base_tile_size
        self.is_panning = False
        self.last_mouse_pos = (0, 0)

    def zoom(self, amount, center_pos=None):
        old_zoom = self.zoom_level
        self.zoom_level = max(0.2, min(4.0, self.zoom_level + amount))
        self.current_tile_size = int(self.base_tile_size * self.zoom_level)
        
        if center_pos:
            # Adjust offset to keep center_pos fixed in world space
            # mouse_world_pos = (center_pos - self.offset) / (self.base_tile_size * old_zoom)
            # self.offset = center_pos - mouse_world_pos * self.current_tile_size
            
            world_pos = (pygame.Vector2(center_pos) - self.offset) / (self.base_tile_size * old_zoom)
            self.offset = pygame.Vector2(center_pos) - world_pos * self.current_tile_size

    def start_panning(self, mouse_pos):
        self.is_panning = True
        self.last_mouse_pos = mouse_pos

    def update_panning(self, mouse_pos):
        if self.is_panning:
            delta = pygame.Vector2(mouse_pos) - pygame.Vector2(self.last_mouse_pos)
            self.offset += delta
            self.last_mouse_pos = mouse_pos

    def stop_panning(self):
        self.is_panning = False

    def screen_to_world(self, screen_pos):
        return (pygame.Vector2(screen_pos) - self.offset) / self.current_tile_size

    def world_to_screen(self, world_pos):
        return pygame.Vector2(world_pos) * self.current_tile_size + self.offset

    def get_grid_pos(self, screen_pos):
        world_pos = self.screen_to_world(screen_pos)
        return int(world_pos.x), int(world_pos.y)

    def apply_rect(self, rect):
        """Scale and offset a world-space rect to screen-space."""
        return pygame.Rect(
            self.offset.x + rect.x * self.zoom_level,
            self.offset.y + rect.y * self.zoom_level,
            rect.width * self.zoom_level,
            rect.height * self.zoom_level
        )
