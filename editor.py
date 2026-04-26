import pygame
import sys
import os
import json
import csv
import subprocess
from engine.loader import ResourceManager

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 36
UI_WIDTH = 250
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (40, 40, 40)
HIGHLIGHT = (0, 255, 0)
ACCENT = (255, 100, 0)

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gemini Engine Framework - Level Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 16)
        self.bold_font = pygame.font.SysFont("Segoe UI", 16, bold=True)
        
        # Initialize Engine Systems
        self.resources = ResourceManager(TILE_SIZE)
        
        # UI State
        self.categories = ["Tiles", "Players", "Enemies", "Weapons", "Props"]
        self.selected_category = "Tiles"
        self.selected_item = "1"
        self.scroll_y = 0
        
        # Grid State
        self.cols = 50
        self.rows = 25
        self.grid = [['-1' for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Camera / Navigation
        self.camera_offset = pygame.Vector2(UI_WIDTH + 20, 50)
        self.is_panning = False
        self.last_mouse_pos = (0,0)
        
    def save_scene(self, path="levels/editor_test.csv"):
        os.makedirs("levels", exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.grid)
        print(f"Scene saved to {path}")

    def load_scene(self, path="levels/editor_test.csv"):
        if not os.path.exists(path): return
        with open(path, "r") as f:
            reader = csv.reader(f)
            self.grid = list(reader)
            self.rows = len(self.grid)
            self.cols = len(self.grid[0])
            
    def play_scene(self):
        self.save_scene("levels/editor_test.csv")
        # Launch main game in a separate process
        print("Launching Scene...")
        subprocess.Popen([sys.executable, "main.py", "levels/editor_test.csv"])

    def draw_ui(self):
        # Sidebar
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, UI_WIDTH, SCREEN_HEIGHT))
        
        # Title
        title = self.bold_font.render("GEMINI ENGINE", True, ACCENT)
        self.screen.blit(title, (20, 10))
        
        # Categories
        for i, cat in enumerate(self.categories):
            rect = pygame.Rect(10, 40 + i * 35, UI_WIDTH - 20, 30)
            color = GRAY if self.selected_category == cat else BLACK
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            text = self.font.render(cat, True, BLACK if self.selected_category == cat else WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))
            
            if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.selected_category = cat
                self.scroll_y = 0

        # Items
        start_y = 250
        items = [k for k, v in self.resources.registry.items() if v['category'] == self.selected_category]
        cols = 4
        padding = 10
        box_size = (UI_WIDTH - (cols + 1) * padding) // cols
        
        for i, item_id in enumerate(items):
            col = i % cols
            row = i // cols
            x = padding + col * (box_size + padding)
            y = start_y + row * (box_size + padding) - self.scroll_y
            
            if y < start_y - box_size or y > SCREEN_HEIGHT - 100: continue
            
            rect = pygame.Rect(x, y, box_size, box_size)
            if self.selected_item == item_id:
                pygame.draw.rect(self.screen, HIGHLIGHT, rect.inflate(6, 6), 2, border_radius=5)
            
            img = self.resources.get_image(item_id)
            scaled = pygame.transform.scale(img, (box_size, box_size))
            self.screen.blit(scaled, (x, y))
            
            if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.selected_item = item_id

        # Play Button
        play_rect = pygame.Rect(20, SCREEN_HEIGHT - 60, UI_WIDTH - 40, 40)
        pygame.draw.rect(self.screen, (0, 150, 0), play_rect, border_radius=10)
        play_text = self.bold_font.render("PLAY SCENE", True, WHITE)
        self.screen.blit(play_text, play_text.get_rect(center=play_rect.center))
        if play_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.play_scene()
            pygame.time.wait(200) # Simple debounce

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.camera_offset.x + c * TILE_SIZE
                y = self.camera_offset.y + r * TILE_SIZE
                
                if x < UI_WIDTH - TILE_SIZE or x > SCREEN_WIDTH or y < -TILE_SIZE or y > SCREEN_HEIGHT: continue
                
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                
                val = self.grid[r][c]
                if val != '-1':
                    img = self.resources.get_image(val)
                    if img: self.screen.blit(img, (x, y))

    def handle_input(self):
        mx, my = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()
        
        if mx > UI_WIDTH:
            gx = int((mx - self.camera_offset.x) // TILE_SIZE)
            gy = int((my - self.camera_offset.y) // TILE_SIZE)
            
            if 0 <= gx < self.cols and 0 <= gy < self.rows:
                if m_keys[0]: self.grid[gy][gx] = self.selected_item
                if m_keys[2]: self.grid[gy][gx] = '-1'
        
        if m_keys[1]: # Middle click pan
            if not self.is_panning:
                self.is_panning = True
                self.last_mouse_pos = (mx, my)
            else:
                self.camera_offset += pygame.Vector2(mx - self.last_mouse_pos[0], my - self.last_mouse_pos[1])
                self.last_mouse_pos = (mx, my)
        else:
            self.is_panning = False

    def run(self):
        while True:
            self.screen.fill(SKY_BLUE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEWHEEL:
                    if pygame.mouse.get_pos()[0] < UI_WIDTH:
                        self.scroll_y = max(0, self.scroll_y - event.y * 30)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s: self.save_scene()
                    if event.key == pygame.K_l: self.load_scene()
            
            self.handle_input()
            self.draw_grid()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
