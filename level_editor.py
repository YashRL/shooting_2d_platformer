import pygame
import sys
import os
import csv

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCALED_TILE_SIZE = 36 # Scale by 2
GRID_COLS = (SCREEN_WIDTH - 200) // SCALED_TILE_SIZE
GRID_ROWS = SCREEN_HEIGHT // SCALED_TILE_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
SKY_BLUE = (135, 206, 235)

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Level Designer")
        self.clock = pygame.time.Clock()
        
        self.tiles = self.load_tiles()
        self.selected_tile_index = 0
        self.grid = [[-1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        
        self.scroll_y = 0
        self.palette_width = 200
        
    def load_tiles(self):
        # We now expect tiles to be named 1.png, 2.png, etc.
        tiles = {}
        path = os.path.join("Assets", "PNG", "Tiles", "Tiles")
        
        # Find all .png files that are just numbers
        files = [f for f in os.listdir(path) if f.endswith('.png')]
        indices = []
        for f in files:
            try:
                idx = int(f.replace('.png', ''))
                indices.append(idx)
            except:
                continue
        
        if indices:
            max_idx = max(indices)
            for i in range(1, max_idx + 1):
                tile_path = os.path.join(path, f"{i}.png")
                if os.path.exists(tile_path):
                    img = pygame.image.load(tile_path).convert_alpha()
                    img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
                    tiles[i] = img
        
        # Load Special Items
        pistol_path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "pistol.png")
        if os.path.exists(pistol_path):
            img = pygame.image.load(pistol_path).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            tiles['P'] = img
            
        insect_path = os.path.join("Assets", "PNG", "Enemies", "Tiles", "Insect", "walk1.png")
        if os.path.exists(insect_path):
            img = pygame.image.load(insect_path).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            tiles['E_I'] = img
            
        ct_path = os.path.join("Assets", "PNG", "Weapons", "Tiles", "chicago_typwriter.png")
        if os.path.exists(ct_path):
            img = pygame.image.load(ct_path).convert_alpha()
            img = pygame.transform.scale(img, (SCALED_TILE_SIZE, SCALED_TILE_SIZE))
            tiles['CT'] = img
            
        return tiles

    def save_level(self):
        if not os.path.exists('levels'):
            os.makedirs('levels')
        with open('levels/level_0.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.grid)
        print("Level saved to levels/level_0.csv")

    def draw_palette(self):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, self.palette_width, SCREEN_HEIGHT))
        
        cols = 4
        padding = 10
        tile_display_size = (self.palette_width - (cols + 1) * padding) // cols
        
        # Separate numeric tiles and special tiles
        numeric_indices = sorted([k for k in self.tiles.keys() if isinstance(k, int)])
        special_indices = [k for k in self.tiles.keys() if isinstance(k, str)]
        all_indices = special_indices + numeric_indices
        
        for i, idx in enumerate(all_indices):
            tile = self.tiles[idx]
            row = i // cols
            col = i % cols
            x = padding + col * (tile_display_size + padding)
            y = padding + row * (tile_display_size + padding) - self.scroll_y
            
            if -tile_display_size <= y <= SCREEN_HEIGHT:
                # Highlight selected
                if idx == self.selected_tile_index:
                    pygame.draw.rect(self.screen, (255, 255, 0), (x-2, y-2, tile_display_size+4, tile_display_size+4))
                
                scaled_tile = pygame.transform.scale(tile, (tile_display_size, tile_display_size))
                self.screen.blit(scaled_tile, (x, y))
                
                # Label special items
                if isinstance(idx, str):
                    font = pygame.font.SysFont(None, 24)
                    text = font.render(idx, True, WHITE)
                    self.screen.blit(text, (x, y))

    def draw_grid(self):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = self.palette_width + c * SCALED_TILE_SIZE
                y = r * SCALED_TILE_SIZE
                
                rect = pygame.Rect(x, y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
                
                tile_idx = self.grid[r][c]
                if tile_idx != -1 and tile_idx != '-1' and tile_idx in self.tiles:
                    self.screen.blit(self.tiles[tile_idx], (x, y))

    def run(self):
        running = True
        while running:
            self.screen.fill(SKY_BLUE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    
                    # Palette interaction
                    if mx < self.palette_width:
                        if event.button == 4: # Scroll up
                            self.scroll_y = max(0, self.scroll_y - 60)
                        elif event.button == 5: # Scroll down
                            self.scroll_y += 60
                        elif event.button == 1: # Left click select
                            cols = 4
                            padding = 10
                            tile_display_size = (self.palette_width - (cols + 1) * padding) // cols
                            
                            col = (mx - padding) // (tile_display_size + padding)
                            row = (my + self.scroll_y - padding) // (tile_display_size + padding)
                            palette_idx = row * cols + col
                            
                            numeric_indices = sorted([k for k in self.tiles.keys() if isinstance(k, int)])
                            special_indices = [k for k in self.tiles.keys() if isinstance(k, str)]
                            all_indices = special_indices + numeric_indices
                            
                            if 0 <= palette_idx < len(all_indices):
                                self.selected_tile_index = all_indices[palette_idx]
                    
                    # Grid interaction
                    else:
                        grid_x = (mx - self.palette_width) // SCALED_TILE_SIZE
                        grid_y = my // SCALED_TILE_SIZE
                        
                        if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                            if event.button == 1: # Place
                                self.grid[grid_y][grid_x] = self.selected_tile_index
                            elif event.button == 3: # Erase
                                self.grid[grid_y][grid_x] = -1
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_level()

            self.draw_palette()
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
