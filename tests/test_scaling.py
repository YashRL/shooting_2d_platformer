import pygame
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engine.core.ResourceManager import ResourceManager

def test_full_blueprint_scaling():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    manager = ResourceManager(tile_size=36)
    
    # Check how many Danger tiles we have now
    danger_tiles = [k for k in manager.registry.keys() if k.startswith("DANGER_")]
    print(f"Total Danger Tiles generated: {len(danger_tiles)}")
    
    if len(danger_tiles) > 1:
        print("[SUCCESS] Multiple Danger tiles generated from blueprint.")
        # Check a specific one (e.g., DANGER_24)
        if "DANGER_24" in manager.registry:
            img = manager.get_image("DANGER_24")
            color = img.get_at((18, 18))
            print(f"DANGER_24 color: {color}")
            if color.r > color.g:
                 print("[SUCCESS] DANGER_24 is tinted red.")
    else:
        print("[FAILURE] Only one or zero Danger tiles found.")

    # Check Ice tiles
    ice_tiles = [k for k in manager.registry.keys() if k.startswith("ICE_")]
    print(f"Total Ice Tiles generated: {len(ice_tiles)}")
    
    # Check Mud tiles
    mud_tiles = [k for k in manager.registry.keys() if k.startswith("MUD_")]
    print(f"Total Mud Tiles generated: {len(mud_tiles)}")

    pygame.quit()

if __name__ == "__main__":
    test_full_blueprint_scaling()
