import pygame
import os

def test_tints():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Tint Test")
    
    img_path = "Assets/PNG/Tiles/Tiles/Green_Grass/6.png"
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    base_img = pygame.image.load(img_path).convert_alpha()
    base_img = pygame.transform.scale(base_img, (100, 100))
    
    # Red Tint (Danger)
    red_tinted = base_img.copy()
    red_tinted.fill((255, 50, 50, 255), special_flags=pygame.BLEND_RGBA_MULT)
    
    # Blue Tint (Ice)
    blue_tinted = base_img.copy()
    blue_tinted.fill((100, 150, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
    
    # Brown/Mud Tint
    mud_tinted = base_img.copy()
    mud_tinted.fill((150, 100, 50, 255), special_flags=pygame.BLEND_RGBA_MULT)

    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((50, 50, 50))
        
        screen.blit(base_img, (50, 50))
        screen.blit(red_tinted, (200, 50))
        screen.blit(blue_tinted, (50, 200))
        screen.blit(mud_tinted, (200, 200))
        
        pygame.display.flip()
        clock.tick(60)
        
        # Take a screenshot and exit
        pygame.image.save(screen, "tint_result.png")
        print("Screenshot saved to tint_result.png")
        running = False

    pygame.quit()

if __name__ == "__main__":
    test_tints()
