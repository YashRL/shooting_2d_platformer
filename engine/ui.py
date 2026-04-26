import pygame
import os

class UIManager:
    def __init__(self, tile_size=36):
        self.tile_size = tile_size
        self.assets = {}
        self.load_assets()

    def load_assets(self):
        base_path = os.path.join("Assets", "PNG", "Interface", "Tiles")
        
        # Load Health Bar Segments
        types = ['HealthBar', 'EmptyBar']
        segments = ['start', 'middle', 'end']
        
        for t in types:
            self.assets[t] = {}
            for s in segments:
                path = os.path.join(base_path, t, f"{s}.png")
                img = pygame.image.load(path).convert_alpha()
                # Scale to Engine Standard 36x36
                img = pygame.transform.scale(img, (36, 36))
                self.assets[t][s] = img

    def draw_health_bar(self, screen, x, y, current, maximum, width_in_segments=5):
        """
        Draws a segmented health bar.
        width_in_segments: total number of 'middle' segments + start and end.
        """
        pct = max(0, min(1.0, current / maximum))
        
        # 1. Draw Background (Empty Bar)
        self._draw_bar_base(screen, x, y, 'EmptyBar', width_in_segments)
        
        # 2. Draw Foreground (Health Bar) with Clipping
        segment_w = 36
        total_pixel_width = (width_in_segments + 2) * segment_w
        filled_width = int(total_pixel_width * pct)
        
        if filled_width > 0:
            bar_surf = pygame.Surface((total_pixel_width, 36), pygame.SRCALPHA)
            self._draw_bar_base(bar_surf, 0, 0, 'HealthBar', width_in_segments)
            screen.blit(bar_surf, (x, y), area=pygame.Rect(0, 0, filled_width, 36))

    def _draw_bar_base(self, surface, x, y, bar_type, middle_count):
        segment_w = 36
        # Start
        surface.blit(self.assets[bar_type]['start'], (x, y))
        # Middle
        for i in range(middle_count):
            surface.blit(self.assets[bar_type]['middle'], (x + (i + 1) * segment_w, y))
        # End
        surface.blit(self.assets[bar_type]['end'], (x + (middle_count + 1) * segment_w, y))
