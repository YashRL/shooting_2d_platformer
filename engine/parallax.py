import pygame
import os

class ParallaxLayer:
    def __init__(self, image, factor, screen_height):
        # Scale image to match screen height while maintaining aspect ratio
        img_rect = image.get_rect()
        scale_ratio = screen_height / img_rect.height
        new_width = int(img_rect.width * scale_ratio)
        self.image = pygame.transform.scale(image, (new_width, screen_height))
        self.base_factor = factor
        self.width = new_width

    def draw(self, screen, camera_x, intensity=1.0):
        # Calculate horizontal offset based on camera position and parallax factor
        offset = (camera_x * (self.base_factor * intensity)) % self.width
        
        # Draw the main image
        screen.blit(self.image, (-offset, 0))
        
        # Draw a second copy to handle the loop
        if offset > 0:
            screen.blit(self.image, (self.width - offset, 0))

class ParallaxManager:
    def __init__(self, theme_path, screen_height, intensity=1.0):
        self.layers = []
        self.screen_height = screen_height
        self.intensity = intensity
        self.load_theme(theme_path)

    def load_theme(self, theme_path):
        if not os.path.exists(theme_path):
            print(f"Warning: Theme path {theme_path} not found.")
            return

        # Explicitly define layers based on the nature structure
        # Background packs usually have these files
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
            layer.draw(screen, camera_x, self.intensity)
