import pygame
import os

# Set dummy video driver
os.environ['SDL_VIDEODRIVER'] = 'dummy'

def apply_outline(image, color):
    """Adds a 1-pixel outline to the image."""
    mask = pygame.mask.from_surface(image)
    outline_surf = pygame.Surface((image.get_width() + 2, image.get_height() + 2), pygame.SRCALPHA)
    
    # Draw outline by offsetting the mask
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        for x, y in mask.outline():
            outline_surf.set_at((x + dx + 1, y + dy + 1), color)
            
    # Re-draw original image on top
    outline_surf.blit(image, (1, 1))
    return outline_surf

def process_frames():
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    input_dir = "Assets/PNG/Characters/Merchant/frames/base_idle"
    output_dir = "Assets/PNG/Characters/Merchant/frames/base_idle_styled"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Processing frames with Smart Eye-Split from {input_dir}...")
    
    BORDER_COLOR = (255, 255, 255, 255) # Pure white sticker border
    
    for i in range(1, 9):
        img_path = os.path.join(input_dir, f"{i}.png")
        if not os.path.exists(img_path):
            continue
            
        # 1. Load original (32x32)
        orig = pygame.image.load(img_path).convert_alpha()
        
        # 2. Downscale to 14x14
        small = pygame.transform.scale(orig, (14, 14))
        
        # 3. SMART EYE SPLIT & CLEANUP
        eye_pixels = []
        for x in range(small.get_width()):
            for y in range(small.get_height()):
                r, g, b, a = small.get_at((x, y))
                # Identify any bright pixel that is part of the "merged" eyes
                if a > 100 and r > 130 and g > 130 and b > 130:
                    eye_pixels.append((x, y))
                # Ensure the face/cloak stays dark
                elif a > 100 and r < 80 and g < 80 and b < 80:
                    small.set_at((x, y), (0, 0, 0, 255))
        
        if eye_pixels:
            # Clear all blurred eye pixels
            for px, py in eye_pixels:
                small.set_at((px, py), (0, 0, 0, 255))
            
            # Find the average center of where the eyes were
            avg_x = sum(p[0] for p in eye_pixels) // len(eye_pixels)
            avg_y = sum(p[1] for p in eye_pixels) // len(eye_pixels)
            
            # Place two distinct eyes with a 1-pixel gap in between (. .)
            # We offset by 1 pixel from the center
            small.set_at((avg_x - 1, avg_y), (255, 255, 255, 255))
            small.set_at((avg_x + 1, avg_y), (255, 255, 255, 255))
        
        # 4. Apply Outline (Result will be 16x16)
        styled = apply_outline(small, BORDER_COLOR)
        
        # 5. Upscale back to 32x32 (Nearest Neighbor)
        final = pygame.transform.scale(styled, (32, 32))
        
        save_path = os.path.join(output_dir, f"{i}.png")
        pygame.image.save(final, save_path)
        print(f"Saved styled frame with split eyes: {save_path}")

    pygame.quit()

if __name__ == "__main__":
    process_frames()
