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
        
        # Load Bullet Icon for HUD
        bullet_path = os.path.join(base_path, "Bullets_UI", "bullet.png")
        if os.path.exists(bullet_path):
            self.bullet_icon = pygame.image.load(bullet_path).convert_alpha()
            self.bullet_icon = pygame.transform.scale(self.bullet_icon, (32, 32))
        else:
            self.bullet_icon = pygame.Surface((32, 32))
            self.bullet_icon.fill((255, 255, 0)) # Yellow fallback

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

    def draw_ammo(self, screen, x, y, current, maximum):
        """Draws ammo icon followed by current/max count."""
        # Draw Icon
        screen.blit(self.bullet_icon, (x, y))
        
        # Draw Text
        font = pygame.font.SysFont("Arial", 24, bold=True)
        text = font.render(f"{current} / {maximum}", True, (255, 255, 255))
        screen.blit(text, (x + 40, y + 2))

    def _draw_bar_base(self, surface, x, y, bar_type, middle_count):
        segment_w = 36
        # Start
        surface.blit(self.assets[bar_type]['start'], (x, y))
        # Middle
        for i in range(middle_count):
            surface.blit(self.assets[bar_type]['middle'], (x + (i + 1) * segment_w, y))
        # End
        surface.blit(self.assets[bar_type]['end'], (x + (middle_count + 1) * segment_w, y))
