import os
import pygame

def recolor_folder(src_folder, dst_folder, target_rgb, replacement_rgb, threshold=60):
    """
    Iterates through a folder, identifies pixels close to target_rgb, 
    and swaps them for replacement_rgb while preserving transparency using Pygame.
    """
    pygame.init()
    # Initialize a hidden display to allow certain pygame operations if needed
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
        print(f"Created directory: {dst_folder}")

    for filename in os.listdir(src_folder):
        if filename.lower().endswith(".png"):
            img_path = os.path.join(src_folder, filename)
            try:
                # Load without convert_alpha() to avoid requiring a display, 
                # or use it with the hidden display we just created.
                surface = pygame.image.load(img_path).convert_alpha()
                width, height = surface.get_size()
                
                # Loop through pixels
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = surface.get_at((x, y))
                        
                        if a > 0: # Only check non-transparent pixels
                            # Check if the pixel is 'white' or close to the target color
                            if (abs(r - target_rgb[0]) < threshold and 
                                abs(g - target_rgb[1]) < threshold and 
                                abs(b - target_rgb[2]) < threshold):
                                
                                surface.set_at((x, y), (replacement_rgb[0], replacement_rgb[1], replacement_rgb[2], a))

                out_path = os.path.join(dst_folder, filename)
                pygame.image.save(surface, out_path)
                print(f"Saved: {out_path}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    pygame.quit()

if __name__ == "__main__":
    # Configuration
    SOURCE = "Assets/PNG/Tiles/Tiles/Ice_Tiles"
    DESTINATION = "Assets/PNG/Tiles/Tiles/Purple_grass_v2"
    
    # Target Color: Pure White
    TARGET = (255, 255, 255)
    
    # Replacement Color: A vibrant Purple
    PURPLE = (180, 50, 200) 

    print(f"Starting recolor process (using Pygame) from {SOURCE}...")
    recolor_folder(SOURCE, DESTINATION, TARGET, PURPLE, threshold=60)
    print("\n[SUCCESS] Assets replicated and recolored!")
