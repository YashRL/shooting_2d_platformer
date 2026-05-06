import pygame
import os
import sys

# Mocking parts of the engine to test loader in isolation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine.loader import ResourceManager

def test_loader_tinting():
    pygame.init()
    # Need a display for convert_alpha() to work properly in some pygame versions
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    manager = ResourceManager(tile_size=36)
    
    # Test 1: Registry-level tinting (Danger Grass)
    danger_img = manager.get_image("DANGER_GRASS")
    if danger_img:
        # Check a pixel to see if it's tinted (should have high red)
        # 6.png is grass, usually green.
        color = danger_img.get_at((18, 18))
        print(f"Danger Grass center color: {color}")
        if color.r > color.g:
            print("[SUCCESS] Danger Grass appears tinted red.")
        else:
            print("[FAILURE] Danger Grass does not appear tinted red.")
    else:
        print("[FAILURE] Could not get DANGER_GRASS image.")

    # Test 2: Instance-level tinting (Dynamic Blue Tint)
    # Using Green_Grass_6 as blueprint
    blue_instance_id = "Green_Grass_6[tint:0,0,255]"
    blue_img = manager.get_image(blue_instance_id)
    if blue_img:
        color = blue_img.get_at((18, 18))
        print(f"Blue Instance center color: {color}")
        if color.b > color.g:
            print("[SUCCESS] Blue Instance appears tinted blue.")
        else:
            print("[FAILURE] Blue Instance does not appear tinted blue.")
    else:
        print("[FAILURE] Could not get blue instance image.")

    # Test 3: Normal Image (No Tint)
    normal_img = manager.get_image("Green_Grass_6")
    if normal_img:
        color = normal_img.get_at((18, 18))
        print(f"Normal Grass center color: {color}")
        if color.g >= color.r and color.g >= color.b:
            print("[SUCCESS] Normal Grass appears green.")
        else:
            print("[FAILURE] Normal Grass does not appear green.")

    pygame.quit()

if __name__ == "__main__":
    test_loader_tinting()
