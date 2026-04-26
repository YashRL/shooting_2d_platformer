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
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (60, 60, 60)
HIGHLIGHT = (0, 255, 0)
ACCENT = (255, 100, 0)
INPUT_BG = (50, 50, 50)

# States
STATE_MENU = "menu"
STATE_CREATE = "create"
STATE_EDITING = "editing"

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Gemini Engine Framework - Level Editor")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.small_font = pygame.font.SysFont("Segoe UI", 14)
        self.bold_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.header_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        
        # Initialize Engine Systems
        self.resources = ResourceManager(TILE_SIZE)
        self.levels_dir = os.path.join(os.getcwd(), "levels")
        os.makedirs(self.levels_dir, exist_ok=True)
        
        # Editor State
        self.state = STATE_MENU
        
        # Menu State
        self.levels_list = []
        self.search_query = ""
        self.refresh_levels()
        
        # Create State
        self.new_level_name = "new_level"
        self.new_level_width = "50"
        self.new_level_height = "25"
        self.active_input = "name" # "name", "width", "height"
        
        # Caret (Cursor) Logic
        self.caret_visible = True
        self.caret_timer = pygame.time.get_ticks()
        self.caret_index = 0
        
        # State scroll management
        self.menu_scroll_y = 0
        self.edit_scroll_y = 0
        
        # Editing State
        self.categories = ["Tiles", "Players", "Enemies", "Weapons", "Props"]
        self.selected_category = "Tiles"
        self.selected_item = "1"
        self.grid = []
        self.rows = 0
        self.cols = 0
        self.current_level_path = ""
        self.camera_offset = pygame.Vector2(UI_WIDTH + 20, 50)
        self.is_panning = False
        self.last_mouse_pos = (0,0)

    def refresh_levels(self):
        if os.path.exists(self.levels_dir):
            self.levels_list = [f for f in os.listdir(self.levels_dir) if f.endswith('.csv')]
        else:
            self.levels_list = []

    def handle_text_input(self, text, event):
        if event.key == pygame.K_BACKSPACE:
            if self.caret_index > 0:
                text = text[:self.caret_index - 1] + text[self.caret_index:]
                self.caret_index -= 1
        elif event.key == pygame.K_DELETE:
            if self.caret_index < len(text):
                text = text[:self.caret_index] + text[self.caret_index + 1:]
        elif event.key == pygame.K_LEFT:
            self.caret_index = max(0, self.caret_index - 1)
        elif event.key == pygame.K_RIGHT:
            self.caret_index = min(len(text), self.caret_index + 1)
        elif event.key == pygame.K_HOME:
            self.caret_index = 0
        elif event.key == pygame.K_END:
            self.caret_index = len(text)
        elif event.unicode and event.unicode.isprintable():
            text = text[:self.caret_index] + event.unicode + text[self.caret_index:]
            self.caret_index += 1
        return text

    def get_caret_from_mouse(self, mouse_x, input_rect_x, text):
        # Estimate caret position based on where user clicked
        relative_x = mouse_x - input_rect_x - 15
        best_index = 0
        min_diff = float('inf')
        for i in range(len(text) + 1):
            w, _ = self.font.size(text[:i])
            diff = abs(relative_x - w)
            if diff < min_diff:
                min_diff = diff
                best_index = i
        return best_index

    def create_new_level(self):
        try:
            w = int(self.new_level_width)
            h = int(self.new_level_height)
            name = self.new_level_name if self.new_level_name.endswith('.csv') else self.new_level_name + ".csv"
            self.cols, self.rows = w, h
            self.grid = [['-1' for _ in range(w)] for _ in range(h)]
            self.current_level_path = os.path.join(self.levels_dir, name)
            self.save_scene(self.current_level_path)
            self.state = STATE_EDITING
        except: pass

    def load_level_from_menu(self, filename):
        path = os.path.join(self.levels_dir, filename)
        self.load_scene(path)
        self.current_level_path = path
        self.state = STATE_EDITING

    def save_scene(self, path):
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(self.grid)

    def load_scene(self, path):
        if not os.path.exists(path): return
        with open(path, "r") as f:
            reader = csv.reader(f)
            self.grid = list(reader)
            self.rows, self.cols = len(self.grid), len(self.grid[0])

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.camera_offset.x + c * TILE_SIZE
                y = self.camera_offset.y + r * TILE_SIZE
                
                # Culling: Don't draw if outside screen (leaving room for UI)
                if x < UI_WIDTH - TILE_SIZE or x > SCREEN_WIDTH or y < -TILE_SIZE or y > SCREEN_HEIGHT: 
                    continue
                
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, (60, 60, 60), rect, 1)
                
                val = self.grid[r][c]
                if val != '-1':
                    img = self.resources.get_image(val)
                    if img: self.screen.blit(img, (x, y))

    def draw_menu(self):
        self.screen.fill(DARK_GRAY)
        if pygame.time.get_ticks() - self.caret_timer > 500:
            self.caret_visible = not self.caret_visible
            self.caret_timer = pygame.time.get_ticks()

        title = self.header_font.render("GEMINI LEVEL LAUNCHER", True, ACCENT)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        # Search Bar
        search_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 130, 400, 40)
        pygame.draw.rect(self.screen, INPUT_BG, search_rect, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.active_input == "search" else GRAY, search_rect, 1, border_radius=5)
        
        search_label = self.font.render("Search: " + self.search_query, True, WHITE)
        self.screen.blit(search_label, (search_rect.x + 10, search_rect.y + 10))
        
        if self.active_input == "search" and self.caret_visible:
            w, _ = self.font.size(self.search_query[:self.caret_index])
            cx = search_rect.x + 10 + self.font.size("Search: ")[0] + w
            pygame.draw.line(self.screen, WHITE, (cx, search_rect.y + 10), (cx, search_rect.y + 30), 2)

        # Level List
        list_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 500, 400)
        pygame.draw.rect(self.screen, BLACK, list_rect, border_radius=10)
        filtered = [f for f in self.levels_list if self.search_query.lower() in f.lower()]
        
        item_h = 50
        list_surf = pygame.Surface((list_rect.width - 20, max(list_rect.height, len(filtered) * item_h)))
        list_surf.fill(BLACK)
        for i, level_name in enumerate(filtered):
            y = i * item_h
            r = pygame.Rect(0, y, list_surf.get_width(), item_h - 5)
            mx, my = pygame.mouse.get_pos()
            color = ACCENT if r.collidepoint(mx - list_rect.x - 10, my - list_rect.y - 10 + self.menu_scroll_y) else LIGHT_GRAY
            pygame.draw.rect(list_surf, color, r, border_radius=5)
            list_surf.blit(self.font.render(level_name, True, WHITE), (20, y + 10))
        self.screen.blit(list_surf, (list_rect.x + 10, list_rect.y + 10), area=pygame.Rect(0, self.menu_scroll_y, list_rect.width-20, list_rect.height-20))

        create_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 630, 200, 50)
        pygame.draw.rect(self.screen, (0, 120, 0), create_btn, border_radius=10)
        self.screen.blit(self.bold_font.render("CREATE NEW", True, WHITE), self.bold_font.render("CREATE NEW", True, WHITE).get_rect(center=create_btn.center))

    def draw_create_screen(self):
        self.screen.fill(DARK_GRAY)
        if pygame.time.get_ticks() - self.caret_timer > 500:
            self.caret_visible = not self.caret_visible
            self.caret_timer = pygame.time.get_ticks()

        title = self.header_font.render("NEW LEVEL SPECIFICATIONS", True, ACCENT)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        fields = [("LEVEL NAME", self.new_level_name, "name"), ("WIDTH (COLS)", self.new_level_width, "width"), ("HEIGHT (ROWS)", self.new_level_height, "height")]
        for i, (label, val, key) in enumerate(fields):
            y = 250 + i * 120
            self.screen.blit(self.bold_font.render(label, True, GRAY), (SCREEN_WIDTH//2 - 150, y))
            r = pygame.Rect(SCREEN_WIDTH//2 - 150, y + 40, 300, 45)
            pygame.draw.rect(self.screen, INPUT_BG, r, border_radius=5)
            pygame.draw.rect(self.screen, ACCENT if self.active_input == key else LIGHT_GRAY, r, 2, border_radius=5)
            self.screen.blit(self.font.render(val, True, WHITE), (r.x + 15, r.y + 10))
            if self.active_input == key and self.caret_visible:
                w, _ = self.font.size(val[:self.caret_index])
                cx = r.x + 15 + w
                pygame.draw.line(self.screen, WHITE, (cx, r.y + 10), (cx, r.y + 35), 2)

        conf_rect = pygame.Rect(SCREEN_WIDTH//2 - 210, 650, 200, 50)
        back_rect = pygame.Rect(SCREEN_WIDTH//2 + 10, 650, 200, 50)
        pygame.draw.rect(self.screen, (0, 150, 0), conf_rect, border_radius=10)
        pygame.draw.rect(self.screen, (150, 0, 0), back_rect, border_radius=10)
        self.screen.blit(self.font.render("CONFIRM", True, WHITE), self.font.render("CONFIRM", True, WHITE).get_rect(center=conf_rect.center))
        self.screen.blit(self.font.render("BACK", True, WHITE), self.font.render("BACK", True, WHITE).get_rect(center=back_rect.center))

    def run(self):
        while True:
            self.screen.fill(SKY_BLUE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if self.state == STATE_MENU:
                        search_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 130, 400, 40)
                        if search_rect.collidepoint(mx, my):
                            self.active_input = "search"
                            self.caret_index = self.get_caret_from_mouse(mx, search_rect.x + self.font.size("Search: ")[0], self.search_query)
                        
                        create_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, 630, 200, 50)
                        if create_btn.collidepoint(mx, my): self.state = STATE_CREATE; self.active_input = "name"; self.caret_index = len(self.new_level_name)
                        
                        list_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 500, 400)
                        if list_rect.collidepoint(mx, my):
                            filtered = [f for f in self.levels_list if self.search_query.lower() in f.lower()]
                            idx = (my - list_rect.y - 10 + self.menu_scroll_y) // 50
                            if 0 <= idx < len(filtered): self.load_level_from_menu(filtered[idx])

                    elif self.state == STATE_CREATE:
                        fields_y = [250, 370, 490]
                        keys = ["name", "width", "height"]
                        vals = [self.new_level_name, self.new_level_width, self.new_level_height]
                        for y, key, val in zip(fields_y, keys, vals):
                            r = pygame.Rect(SCREEN_WIDTH//2 - 150, y + 40, 300, 45)
                            if r.collidepoint(mx, my):
                                self.active_input = key
                                self.caret_index = self.get_caret_from_mouse(mx, r.x, val)
                        
                        conf_rect = pygame.Rect(SCREEN_WIDTH//2 - 210, 650, 200, 50)
                        if conf_rect.collidepoint(mx, my): self.create_new_level()
                        if pygame.Rect(SCREEN_WIDTH//2 + 10, 650, 200, 50).collidepoint(mx, my): self.state = STATE_MENU

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_MENU and self.active_input == "search":
                        self.search_query = self.handle_text_input(self.search_query, event)
                    elif self.state == STATE_CREATE:
                        if event.key == pygame.K_TAB:
                            order = ["name", "width", "height"]
                            self.active_input = order[(order.index(self.active_input) + 1) % 3]
                            self.caret_index = len(getattr(self, f"new_level_{self.active_input}"))
                        else:
                            attr = f"new_level_{self.active_input}"
                            setattr(self, attr, self.handle_text_input(getattr(self, attr), event))
                    elif self.state == STATE_EDITING:
                        if event.key == pygame.K_s: self.save_scene(self.current_level_path)
                        if event.key == pygame.K_m: self.state = STATE_MENU; self.refresh_levels()

                if event.type == pygame.MOUSEWHEEL:
                    if self.state == STATE_MENU: self.menu_scroll_y = max(0, self.menu_scroll_y - event.y * 30)
                    elif self.state == STATE_EDITING and pygame.mouse.get_pos()[0] < UI_WIDTH: self.edit_scroll_y = max(0, self.edit_scroll_y - event.y * 30)

            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_CREATE: self.draw_create_screen()
            elif self.state == STATE_EDITING:
                # [Previous editing logic remains...]
                mx, my = pygame.mouse.get_pos()
                m_keys = pygame.mouse.get_pressed()
                if mx > UI_WIDTH:
                    gx, gy = int((mx - self.camera_offset.x) // TILE_SIZE), int((my - self.camera_offset.y) // TILE_SIZE)
                    if 0 <= gx < self.cols and 0 <= gy < self.rows:
                        if m_keys[0]: self.grid[gy][gx] = self.selected_item
                        if m_keys[2]: self.grid[gy][gx] = '-1'
                if m_keys[1]:
                    if not self.is_panning: self.is_panning, self.last_mouse_pos = True, (mx, my)
                    else: self.camera_offset += pygame.Vector2(mx - self.last_mouse_pos[0], my - self.last_mouse_pos[1]); self.last_mouse_pos = (mx, my)
                else: self.is_panning = False
                self.draw_grid()
                # Draw editing UI sidebar
                pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, UI_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(self.bold_font.render(os.path.basename(self.current_level_path).upper(), True, ACCENT), (20, 20))
                for i, cat in enumerate(self.categories):
                    rect = pygame.Rect(10, 70 + i * 35, UI_WIDTH - 20, 30)
                    color = GRAY if self.selected_category == cat else BLACK
                    pygame.draw.rect(self.screen, color, rect, border_radius=5)
                    self.screen.blit(self.small_font.render(cat, True, BLACK if self.selected_category == cat else WHITE), self.small_font.render(cat, True, BLACK if self.selected_category == cat else WHITE).get_rect(center=rect.center))
                    if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]: self.selected_category, self.edit_scroll_y = cat, 0
                start_y, items = 260, [k for k, v in self.resources.registry.items() if v['category'] == self.selected_category]
                cols, padding = 4, 10
                box_size = (UI_WIDTH - (cols + 1) * padding) // cols
                for i, item_id in enumerate(items):
                    col, row = i % cols, i // cols
                    x, y = padding + col * (box_size + padding), start_y + row * (box_size + padding) - self.edit_scroll_y
                    if y < start_y - box_size or y > SCREEN_HEIGHT - 120: continue
                    rect = pygame.Rect(x, y, box_size, box_size)
                    if self.selected_item == item_id: pygame.draw.rect(self.screen, HIGHLIGHT, rect.inflate(6, 6), 2, border_radius=5)
                    self.screen.blit(pygame.transform.scale(self.resources.get_image(item_id), (box_size, box_size)), (x, y))
                    if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]: self.selected_item = item_id
                info = ["S: Save", "M: Main Menu", "Middle Click: Pan"]
                for i, text in enumerate(info): self.screen.blit(self.small_font.render(text, True, GRAY), (20, SCREEN_HEIGHT - 110 + i * 20))
                play_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, UI_WIDTH - 40, 35)
                pygame.draw.rect(self.screen, (0, 150, 0), play_rect, border_radius=8)
                self.screen.blit(self.font.render("PLAY SCENE", True, WHITE), self.font.render("PLAY SCENE", True, WHITE).get_rect(center=play_rect.center))
                if play_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    self.save_scene(self.current_level_path)
                    subprocess.Popen([sys.executable, "main.py", self.current_level_path])
                    pygame.time.wait(200)

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    LevelEditor().run()
