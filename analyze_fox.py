import pygame
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

def analyze():
    pygame.init()
    pygame.display.set_mode((1, 1))
    path = 'Assets/PNG/Players/Tiles/fox/jump.png'
    img = pygame.image.load(path).convert_alpha()
    
    print(f"Analyzing {path} - Size: {img.get_size()}")
    
    # We look for the outermost non-transparent pixels that are white-ish
    # Sticker borders are usually (255, 255, 255) or slightly off-white (240, 240, 240)
    colors = {}
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            c = img.get_at((x, y))
            if c.a > 0:
                # Store frequency of bright colors
                if c.r > 200 and c.g > 200 and c.b > 200:
                    rgb = (c.r, c.g, c.b, c.a)
                    colors[rgb] = colors.get(rgb, 0) + 1
    
    # Sort by frequency
    sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
    for color, freq in sorted_colors[:5]:
        print(f"Color {color}: found {freq} times")

    pygame.quit()

if __name__ == "__main__":
    analyze()
