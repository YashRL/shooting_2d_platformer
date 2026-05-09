import pygame
import os
from src.engine.graphics.ParallaxLayer import ParallaxLayer

class ParallaxManager:
    def __init__(self, theme_path, screen_height, intensity=1.0, y_offset=0):
        self.layers = []
        self.screen_height = screen_height
        self.intensity = intensity
        self.y_offset = y_offset
        self.load_theme(theme_path)

    def load_theme(self, theme_path):
        if not os.path.exists(theme_path):
            print(f"Warning: Theme path {theme_path} not found.")
            return

        # Explicitly define layers based on the nature structure
        layer_files = ['1.png', '2.png', '3.png', '5.png', '6.png', '7.png', '8.png', '10.png']
        
        base_factor = 0.05
        for i, filename in enumerate(layer_files):
            path = os.path.join(theme_path, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                factor = 0 if i == 0 else base_factor * i
                self.layers.append(ParallaxLayer(img, factor, self.screen_height))

    def draw(self, screen, camera_x):
        for layer in self.layers:
            layer.draw(screen, camera_x, self.intensity, self.y_offset)
