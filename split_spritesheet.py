import pygame
import os
import sys

# Set dummy video driver to avoid opening a window if possible
os.environ['SDL_VIDEODRIVER'] = 'dummy'

def split_spritesheet(sheet_path, frame_width, frame_height, output_dir):
    pygame.init()
    # Create a small display to allow convert_alpha to work
    pygame.display.set_mode((1, 1))
    
    try:
        sheet = pygame.image.load(sheet_path).convert_alpha()
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    sheet_width, sheet_height = sheet.get_size()
    cols = sheet_width // frame_width
    rows = sheet_height // frame_height

    print(f"Sheet Size: {sheet_width}x{sheet_height}")
    print(f"Splitting into {cols} columns and {rows} rows (Frame: {frame_width}x{frame_height})")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    count = 0
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), rect)

            # Check if frame is empty
            is_empty = True
            for x in range(frame_width):
                for y in range(frame_height):
                    if frame.get_at((x, y))[3] > 0: # Alpha > 0
                        is_empty = False
                        break
                if not is_empty:
                    break
            
            if not is_empty:
                pygame.image.save(frame, os.path.join(output_dir, f"frame_{count:03d}.png"))
                count += 1

    print(f"Saved {count} frames to {output_dir}")
    pygame.quit()

if __name__ == "__main__":
    # USER: Adjust these values to fit the sprite sheet perfectly
    SHEET_PATH = "Assets/PNG/Characters/Merchant/merchant.png"
    FRAME_W = 32
    FRAME_H = 32
    OUTPUT = "Assets/PNG/Characters/Merchant/frames"

    if len(sys.argv) > 2:
        FRAME_W = int(sys.argv[1])
        FRAME_H = int(sys.argv[2])

    split_spritesheet(SHEET_PATH, FRAME_W, FRAME_H, OUTPUT)
