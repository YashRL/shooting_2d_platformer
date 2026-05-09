import pygame

class ParallaxLayer:
    def __init__(self, image, factor, screen_height):
        # Scale image to match screen height while maintaining aspect ratio
        img_rect = image.get_rect()
        scale_ratio = screen_height / img_rect.height
        new_width = int(img_rect.width * scale_ratio)
        self.image = pygame.transform.scale(image, (new_width, screen_height))
        self.base_factor = factor
        self.width = new_width

    def draw(self, screen, camera_x, intensity=1.0, y_offset=0):
        # Calculate horizontal offset based on camera position and parallax factor
        offset = (camera_x * (self.base_factor * intensity)) % self.width
        
        # Draw the main image with y_offset
        screen.blit(self.image, (-offset, y_offset))
        
        # Draw a second copy to handle the loop
        if offset > 0:
            screen.blit(self.image, (self.width - offset, y_offset))
