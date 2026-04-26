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
        self.base_tile_size = 36
        self.current_tile_size = 36
        self.zoom_level = 1.0
        self.resources = ResourceManager(self.base_tile_size)
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
        self.active_input = "search" # "search", "name", "width", "height"
        
        # Caret (Cursor) Logic
        self.caret_visible = True
        self.caret_timer = pygame.time.get_ticks()
        self.caret_index = 0
        
        # Editing State
        self.categories = ["Tiles", "Players", "Enemies", "Weapons", "Props"]
        self.selected_category = "Tiles"
        self.selected_item = "1"
        self.current_tool = "stamp" # "stamp" or "erase"
        self.undo_stack = []
        self.max_undo = 50
        
        self.menu_scroll_y = 0
        self.edit_scroll_y = 0
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
        else: self.levels_list = []

    def save_state_for_undo(self):
        state = [row[:] for row in self.grid]
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo: self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.grid = self.undo_stack.pop()

    def zoom(self, amount, center_pos=None):
        old_zoom = self.zoom_level
        self.zoom_level = max(0.2, min(3.0, self.zoom_level + amount))
        self.current_tile_size = int(self.base_tile_size * self.zoom_level)
        if center_pos:
            mouse_world_pos = (center_pos - self.camera_offset) / (self.base_tile_size * old_zoom)
            self.camera_offset = center_pos - mouse_world_pos * self.current_tile_size

    def recenter(self):
        self.zoom_level = 1.0
        self.current_tile_size = self.base_tile_size
        self.camera_offset = pygame.Vector2(UI_WIDTH + 20, 50)

    def handle_text_input(self, text, event):
        if event.key == pygame.K_BACKSPACE:
            if self.caret_index > 0:
                text = text[:self.caret_index - 1] + text[self.caret_index:]
                self.caret_index -= 1
        elif event.key == pygame.K_DELETE:
            if self.caret_index < len(text): text = text[:self.caret_index] + text[self.caret_index + 1:]
        elif event.key == pygame.K_LEFT: self.caret_index = max(0, self.caret_index - 1)
        elif event.key == pygame.K_RIGHT: self.caret_index = min(len(text), self.caret_index + 1)
        elif event.unicode and event.unicode.isprintable():
            text = text[:self.caret_index] + event.unicode + text[self.caret_index:]
            self.caret_index += 1
        return text

    def get_caret_from_mouse(self, mouse_x, input_rect_x, text):
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
            w, h = int(self.new_level_width), int(self.new_level_height)
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
            if self.grid:
                self.rows, self.cols = len(self.grid), len(self.grid[0])

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.camera_offset.x + c * self.current_tile_size
                y = self.camera_offset.y + r * self.current_tile_size
                if x < UI_WIDTH - self.current_tile_size or x > SCREEN_WIDTH or y < -self.current_tile_size or y > SCREEN_HEIGHT: continue
                rect = pygame.Rect(x, y, self.current_tile_size, self.current_tile_size)
                pygame.draw.rect(self.screen, (60, 60, 60), rect, 1)
                val = self.grid[r][c]
                if val != '-1':
                    img = self.resources.get_image(val)
                    if img: self.screen.blit(pygame.transform.scale(img, (self.current_tile_size, self.current_tile_size)), (x, y))

    def draw_menu(self):
        self.screen.fill(DARK_GRAY)
        if pygame.time.get_ticks() - self.caret_timer > 500:
            self.caret_visible = not self.caret_visible
            self.caret_timer = pygame.time.get_ticks()
        title = self.header_font.render("THETREESENTINAL LEVEL LAUNCHER", True, ACCENT)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        search_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, 130, 400, 40)
        pygame.draw.rect(self.screen, INPUT_BG, search_rect, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.active_input == "search" else GRAY, search_rect, 1, border_radius=5)
        search_label = self.font.render("Search: " + self.search_query, True, WHITE)
        self.screen.blit(search_label, (search_rect.x + 10, search_rect.y + 10))
        if self.active_input == "search" and self.caret_visible:
            w, _ = self.font.size(self.search_query[:self.caret_index])
            cx = search_rect.x + 10 + self.font.size("Search: ")[0] + w
            pygame.draw.line(self.screen, WHITE, (cx, search_rect.y + 10), (cx, search_rect.y + 30), 2)
        list_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, 200, 500, 400)
        pygame.draw.rect(self.screen, BLACK, list_rect, border_radius=10)
        filtered = [f for f in self.levels_list if self.search_query.lower() in f.lower()]
        item_h = 50
        list_surf = pygame.Surface((list_rect.width - 20, max(list_rect.height, len(filtered) * item_h)))
        list_surf.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        for i, level_name in enumerate(filtered):
            y = i * item_h
            r = pygame.Rect(0, y, list_surf.get_width(), item_h - 5)
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
        conf_rect, back_rect = pygame.Rect(SCREEN_WIDTH//2 - 210, 650, 200, 50), pygame.Rect(SCREEN_WIDTH//2 + 10, 650, 200, 50)
        pygame.draw.rect(self.screen, (0, 150, 0), conf_rect, border_radius=10); pygame.draw.rect(self.screen, (150, 0, 0), back_rect, border_radius=10)
        self.screen.blit(self.font.render("CONFIRM", True, WHITE), self.font.render("CONFIRM", True, WHITE).get_rect(center=conf_rect.center))
        self.screen.blit(self.font.render("BACK", True, WHITE), self.font.render("BACK", True, WHITE).get_rect(center=back_rect.center))

    def draw_editing_ui(self):
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, UI_WIDTH, SCREEN_HEIGHT))
        lvl_name = os.path.basename(self.current_level_path)
        self.screen.blit(self.bold_font.render(lvl_name.upper(), True, ACCENT), (20, 15))
        btn_save, btn_menu = pygame.Rect(10, 50, UI_WIDTH//2 - 15, 30), pygame.Rect(UI_WIDTH//2 + 5, 50, UI_WIDTH//2 - 15, 30)
        pygame.draw.rect(self.screen, LIGHT_GRAY, btn_save, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, btn_menu, border_radius=5)
        self.screen.blit(self.small_font.render("SAVE", True, WHITE), self.small_font.render("SAVE", True, WHITE).get_rect(center=btn_save.center))
        self.screen.blit(self.small_font.render("MENU", True, WHITE), self.small_font.render("MENU", True, WHITE).get_rect(center=btn_menu.center))
        mx, my = pygame.mouse.get_pos()
        m_clicked = pygame.mouse.get_pressed()[0]
        if m_clicked:
            if btn_save.collidepoint(mx, my): self.save_scene(self.current_level_path); pygame.time.wait(200)
            if btn_menu.collidepoint(mx, my): self.state = STATE_MENU; self.refresh_levels(); pygame.time.wait(200)
        tool_y = 95
        self.screen.blit(self.small_font.render("TOOL:", True, GRAY), (20, tool_y))
        stamp_btn, erase_btn = pygame.Rect(70, tool_y - 5, 60, 25), pygame.Rect(140, tool_y - 5, 60, 25)
        pygame.draw.rect(self.screen, ACCENT if self.current_tool == "stamp" else LIGHT_GRAY, stamp_btn, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.current_tool == "erase" else LIGHT_GRAY, erase_btn, border_radius=5)
        self.screen.blit(self.small_font.render("STAMP", True, WHITE), self.small_font.render("STAMP", True, WHITE).get_rect(center=stamp_btn.center))
        self.screen.blit(self.small_font.render("ERASE", True, WHITE), self.small_font.render("ERASE", True, WHITE).get_rect(center=erase_btn.center))
        if m_clicked:
            if stamp_btn.collidepoint(mx, my): self.current_tool = "stamp"
            if erase_btn.collidepoint(mx, my): self.current_tool = "erase"
        zoom_y = 135
        self.screen.blit(self.small_font.render(f"ZOOM: {int(self.zoom_level * 100)}%", True, WHITE), (20, zoom_y))
        plus_rect, minus_rect, reset_rect = pygame.Rect(20, zoom_y+20, 30, 25), pygame.Rect(60, zoom_y+20, 30, 25), pygame.Rect(100, zoom_y+20, 80, 25)
        pygame.draw.rect(self.screen, LIGHT_GRAY, plus_rect, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, minus_rect, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, reset_rect, border_radius=5)
        self.screen.blit(self.font.render("+", True, WHITE), self.font.render("+", True, WHITE).get_rect(center=plus_rect.center)); self.screen.blit(self.font.render("-", True, WHITE), self.font.render("-", True, WHITE).get_rect(center=minus_rect.center)); self.screen.blit(self.small_font.render("RESET", True, WHITE), self.small_font.render("RESET", True, WHITE).get_rect(center=reset_rect.center))
        if m_clicked:
            if plus_rect.collidepoint(mx, my): self.zoom(0.02)
            if minus_rect.collidepoint(mx, my): self.zoom(-0.02)
            if reset_rect.collidepoint(mx, my): self.recenter()
        cat_start_y = 195
        for i, cat in enumerate(self.categories):
            rect = pygame.Rect(10, cat_start_y + i * 35, UI_WIDTH - 20, 30)
            color = GRAY if self.selected_category == cat else BLACK
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            text_surf = self.small_font.render(cat, True, BLACK if self.selected_category == cat else WHITE)
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            if rect.collidepoint(mx, my) and m_clicked: self.selected_category, self.edit_scroll_y = cat, 0
        item_start_y, items = 380, [k for k, v in self.resources.registry.items() if v['category'] == self.selected_category]
        cols, padding = 4, 10
        box_size = (UI_WIDTH - (cols + 1) * padding) // cols
        for i, item_id in enumerate(items):
            col, row = i % cols, i // cols
            x, y = padding + col * (box_size + padding), item_start_y + row * (box_size + padding) - self.edit_scroll_y
            if y < item_start_y - box_size or y > SCREEN_HEIGHT - 120: continue
            rect = pygame.Rect(x, y, box_size, box_size)
            if self.selected_item == item_id: pygame.draw.rect(self.screen, HIGHLIGHT, rect.inflate(6, 6), 2, border_radius=5)
            self.screen.blit(pygame.transform.scale(self.resources.get_image(item_id), (box_size, box_size)), (x, y))
            if rect.collidepoint(mx, my) and m_clicked: self.selected_item = item_id
        play_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, UI_WIDTH - 40, 35)
        pygame.draw.rect(self.screen, (0, 150, 0), play_rect, border_radius=8)
        self.screen.blit(self.font.render("PLAY SCENE", True, WHITE), self.font.render("PLAY SCENE", True, WHITE).get_rect(center=play_rect.center))
        if play_rect.collidepoint(mx, my) and m_clicked:
            self.save_scene(self.current_level_path); subprocess.Popen([sys.executable, "main.py", self.current_level_path]); pygame.time.wait(200)

    def handle_editing_input(self):
        mx, my = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()
        if mx > UI_WIDTH:
            gx, gy = int((mx - self.camera_offset.x) // self.current_tile_size), int((my - self.camera_offset.y) // self.current_tile_size)
            if 0 <= gx < self.cols and 0 <= gy < self.rows:
                if m_keys[0]:
                    target = self.selected_item if self.current_tool == "stamp" else "-1"
                    if self.grid[gy][gx] != target: self.save_state_for_undo(); self.grid[gy][gx] = target
                if m_keys[2]:
                    if self.grid[gy][gx] != "-1": self.save_state_for_undo(); self.grid[gy][gx] = "-1"
        if m_keys[1]:
            if not self.is_panning: self.is_panning, self.last_mouse_pos = True, (mx, my)
            else: self.camera_offset += pygame.Vector2(mx - self.last_mouse_pos[0], my - self.last_mouse_pos[1]); self.last_mouse_pos = (mx, my)
        else: self.is_panning = False

    def run(self):
        while True:
            self.screen.fill(SKY_BLUE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if self.state == STATE_MENU:
                        if pygame.Rect(SCREEN_WIDTH//2-200, 130, 400, 40).collidepoint(mx, my): self.active_input, self.caret_index = "search", self.get_caret_from_mouse(mx, SCREEN_WIDTH//2-200+self.font.size("Search: ")[0], self.search_query)
                        if pygame.Rect(SCREEN_WIDTH//2-100, 630, 200, 50).collidepoint(mx, my): self.state, self.active_input = STATE_CREATE, "name"; self.caret_index = len(self.new_level_name)
                        lr = pygame.Rect(SCREEN_WIDTH//2-250, 200, 500, 400)
                        if lr.collidepoint(mx, my):
                            filtered = [f for f in self.levels_list if self.search_query.lower() in f.lower()]
                            idx = (my - lr.y - 10 + self.menu_scroll_y) // 50
                            if 0 <= idx < len(filtered): self.load_level_from_menu(filtered[idx])
                    elif self.state == STATE_CREATE:
                        for i, (label, val, key) in enumerate([("name", self.new_level_name, "name"), ("width", self.new_level_width, "width"), ("height", self.new_level_height, "height")]):
                            if pygame.Rect(SCREEN_WIDTH//2-150, 250+i*120+40, 300, 45).collidepoint(mx, my): self.active_input, self.caret_index = key, self.get_caret_from_mouse(mx, SCREEN_WIDTH//2-150, val)
                        if pygame.Rect(SCREEN_WIDTH//2-210, 650, 200, 50).collidepoint(mx, my): self.create_new_level()
                        if pygame.Rect(SCREEN_WIDTH//2+10, 650, 200, 50).collidepoint(mx, my): self.state = STATE_MENU
                if event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    if self.state == STATE_MENU and self.active_input == "search": self.search_query = self.handle_text_input(self.search_query, event)
                    elif self.state == STATE_CREATE:
                        if event.key == pygame.K_TAB: order = ["name", "width", "height"]; self.active_input = order[(order.index(self.active_input)+1)%3]; self.caret_index = len(getattr(self, f"new_level_{self.active_input}"))
                        else: attr = f"new_level_{self.active_input}"; setattr(self, attr, self.handle_text_input(getattr(self, attr), event))
                    elif self.state == STATE_EDITING:
                        if mods & pygame.KMOD_CTRL:
                            if event.key == pygame.K_s: self.save_scene(self.current_level_path)
                            if event.key == pygame.K_z: self.undo()
                        if event.key == pygame.K_m: self.state = STATE_MENU; self.refresh_levels()
                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    if self.state == STATE_EDITING and (pygame.key.get_mods() & pygame.KMOD_CTRL): self.zoom(event.y * 0.1, pygame.Vector2(mx, my))
                    elif self.state == STATE_MENU: self.menu_scroll_y = max(0, self.menu_scroll_y - event.y * 30)
                    elif self.state == STATE_EDITING and mx < UI_WIDTH: self.edit_scroll_y = max(0, self.edit_scroll_y - event.y * 30)
            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_CREATE: self.draw_create_screen()
            elif self.state == STATE_EDITING: self.handle_editing_input(); self.draw_grid(); self.draw_editing_ui()
            pygame.display.flip(); self.clock.tick(FPS)
if __name__ == "__main__":
    LevelEditor().run()
