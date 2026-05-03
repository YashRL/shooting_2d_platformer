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
STATE_SETTINGS = "settings"

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TheTreeSentinal Engine by Yash - Level Editor")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont("Segoe UI", 18)
        self.small_font = pygame.font.SysFont("Segoe UI", 14)
        self.bold_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.header_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        
        self.base_tile_size = 36
        self.current_tile_size = 36
        self.zoom_level = 1.0
        self.resources = ResourceManager(self.base_tile_size)
        self.levels_dir = os.path.join(os.getcwd(), "levels")
        os.makedirs(self.levels_dir, exist_ok=True)
        
        self.state = STATE_MENU
        self.levels_list = []
        self.search_query = ""
        self.refresh_levels()
        
        self.new_level_name = "new_level"
        self.new_level_width = "50"
        self.new_level_height = "25"
        self.active_input = "search"
        self.caret_visible = True
        self.caret_timer = pygame.time.get_ticks()
        self.caret_index = 0
        
        # Multi-Layer Editing State
        self.main_categories = ["Tiles", "Props", "Players", "Enemies", "Weapons", "Platforms", "Characters", "Barrels", "Traps"]
        self.tile_sub_categories = ["Concrete", "Foundation", "Green Grass", "Purple Grass", "Purple Grass v2", "Danger", "Ice", "Mud", "Pipes", "Trampoline"]
        self.selected_category = "Tiles"
        self.selected_sub_category = "Concrete"
        self.selected_item = None
        
        # Trap State
        self.selected_direction = "UP"
        
        # Level Settings
        self.available_themes = [d for d in os.listdir("Assets/PNG/Backgrounds") if os.path.isdir(os.path.join("Assets/PNG/Backgrounds", d))]
        self.current_theme = "nature_1"
        self.parallax_intensity = 1.0
        self.parallax_y_offset = 0
        
        self.current_tool = "stamp"
        self.selection_start = None
        self.selection_end = None
        self.clipboard = None
        
        self.undo_stack = []
        self.max_undo = 50
        self.mouse_debounce = False
        
        self.menu_scroll_y = 0
        self.edit_scroll_y = 0
        
        # Grid layers: 0=World(Tiles), 1=Entities(Props, Players, etc)
        self.grid_world = []
        self.grid_entities = []
        self.rows = 0
        self.cols = 0
        
        self.current_level_path = ""
        self.camera_offset = pygame.Vector2(UI_WIDTH + 20, 50)
        self.is_panning = False
        self.last_mouse_pos = (0,0)
        
        # Moving Platform Node Placement
        self.node_buffer = []
        self.placing_nodes_for = None # (gx, gy)
        self.platform_speed = "2.0"
        self.platform_loop = True

    def refresh_levels(self):
        if os.path.exists(self.levels_dir):
            self.levels_list = [f for f in os.listdir(self.levels_dir) if f.endswith('.csv')]
        else: self.levels_list = []

    def enter_editing_state(self):
        self.state = STATE_EDITING
        self.mouse_debounce = True
        self.selected_item = None

    def save_state_for_undo(self):
        state = ([row[:] for row in self.grid_world], [row[:] for row in self.grid_entities])
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo: self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.grid_world, self.grid_entities = self.undo_stack.pop()

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
            if diff < min_diff: min_diff, best_index = diff, i
        return best_index

    def create_new_level(self):
        try:
            w, h = int(self.new_level_width), int(self.new_level_height)
            name = self.new_level_name if self.new_level_name.endswith('.csv') else self.new_level_name + ".csv"
            self.cols, self.rows = w, h
            self.grid_world = [['-1' for _ in range(w)] for _ in range(h)]
            self.grid_entities = [['-1' for _ in range(w)] for _ in range(h)]
            self.current_level_path = os.path.join(self.levels_dir, name)
            self.save_scene(self.current_level_path)
            self.enter_editing_state()
        except: pass

    def resize_level(self, new_cols, new_rows):
        # Preservation logic: Create new grids and copy old data
        new_world = [['-1' for _ in range(new_cols)] for _ in range(new_rows)]
        new_entities = [['-1' for _ in range(new_cols)] for _ in range(new_rows)]
        
        for r in range(min(self.rows, new_rows)):
            for c in range(min(self.cols, new_cols)):
                new_world[r][c] = self.grid_world[r][c]
                new_entities[r][c] = self.grid_entities[r][c]
        
        self.save_state_for_undo()
        self.grid_world = new_world
        self.grid_entities = new_entities
        self.rows = new_rows
        self.cols = new_cols
        print(f"Level Resized to {new_cols}x{new_rows}")

    def load_level_from_menu(self, filename):
        path = os.path.join(self.levels_dir, filename)
        self.load_scene(path)
        self.current_level_path = path
        self.enter_editing_state()

    def save_scene(self, path):
        # Save as Composite: TILE;ENTITY
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            combined = []
            for r in range(self.rows):
                row = []
                for c in range(self.cols):
                    row.append(f"{self.grid_world[r][c]};{self.grid_entities[r][c]}")
                combined.append(row)
            writer.writerows(combined)
        
        # Save Metadata
        meta_path = path.replace('.csv', '.json')
        meta = {
            "theme": self.current_theme,
            "parallax_intensity": self.parallax_intensity,
            "parallax_y_offset": self.parallax_y_offset,
            "width": self.cols,
            "height": self.rows
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        print(f"Saved: {path} and Metadata")

    def load_scene(self, path):
        if not os.path.exists(path): return
        
        # Load Metadata first
        meta_path = path.replace('.csv', '.json')
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                self.current_theme = meta.get("theme", "nature_1")
                self.parallax_intensity = meta.get("parallax_intensity", 1.0)
                self.parallax_y_offset = meta.get("parallax_y_offset", 0)

        with open(path, "r") as f:
            reader = csv.reader(f)
            data = list(reader)
            if not data: return
            self.rows, self.cols = len(data), len(data[0])
            self.new_level_width, self.new_level_height = str(self.cols), str(self.rows)
            self.grid_world = [['-1' for _ in range(self.cols)] for _ in range(self.rows)]
            self.grid_entities = [['-1' for _ in range(self.cols)] for _ in range(self.rows)]
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = data[r][c]
                    if ';' in cell:
                        w, e = cell.split(';', 1)
                        self.grid_world[r][c] = w
                        self.grid_entities[r][c] = e
                    else:
                        # Legacy support
                        self.grid_world[r][c] = cell

    def draw_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.camera_offset.x + c * self.current_tile_size
                y = self.camera_offset.y + r * self.current_tile_size
                if x < UI_WIDTH - self.current_tile_size or x > SCREEN_WIDTH or y < -self.current_tile_size or y > SCREEN_HEIGHT: continue
                
                rect = pygame.Rect(x, y, self.current_tile_size, self.current_tile_size)
                pygame.draw.rect(self.screen, (60, 60, 60), rect, 1)
                
                # Render Layers
                val_w = self.grid_world[r][c]
                val_e = self.grid_entities[r][c]
                
                if val_w != '-1':
                    info = self.resources.registry.get(val_w)
                    factor = info.get('parallax_factor', 1.0) if info else 1.0
                    # For editor, we might want to toggle parallax or just show it 1:1.
                    # Let's show it 1:1 for precise placement, but I'll add the factor logic for consistency if desired.
                    # Actually, in editor, 1:1 is better for placement. 
                    img = self.resources.get_image(val_w)
                    if img: self.screen.blit(pygame.transform.scale(img, (self.current_tile_size, self.current_tile_size)), (x, y))
                
                if val_e != '-1':
                    actual_id = val_e.split('[')[0] if '[' in val_e else val_e
                    info = self.resources.registry.get(actual_id)
                    img = self.resources.get_image(val_e)
                    if img:
                        w_scale = self.current_tile_size
                        if actual_id == "MOVING_PLATFORM":
                            # Draw 2 tiles wide
                            w_scale = self.current_tile_size * 2
                            # Also optionally draw nodes if it's the selected item or always?
                            # For "careful" implementation, let's always show a hint of path if selected.
                        
                        self.screen.blit(pygame.transform.scale(img, (w_scale, self.current_tile_size)), (x, y))
                        
                        # Extra visual for Moving Platform nodes
                        if actual_id == "MOVING_PLATFORM" and '[' in val_e:
                            props_str = val_e.split('[')[1][:-1]
                            # Robust split: handles legacy ';' and new '&'
                            pairs = props_str.replace(';', '&').split('&')
                            for pair in pairs:
                                if pair.startswith('nodes:'):
                                    nodes_raw = pair.split(':')[1]
                                    for node_raw in nodes_raw.split('|'):
                                        if ',' in node_raw:
                                            nx, ny = map(int, node_raw.split(','))
                                            snx = self.camera_offset.x + (nx / TILE_SIZE) * self.current_tile_size
                                            sny = self.camera_offset.y + (ny / TILE_SIZE) * self.current_tile_size
                                            pygame.draw.circle(self.screen, ACCENT, (int(snx), int(sny)), 3)

        # Draw Selection Box
        if self.selection_start and self.selection_end:
            x1, x2 = min(self.selection_start[0], self.selection_end[0]), max(self.selection_start[0], self.selection_end[0])
            y1, y2 = min(self.selection_start[1], self.selection_end[1]), max(self.selection_start[1], self.selection_end[1])
            
            sel_rect = pygame.Rect(
                self.camera_offset.x + x1 * self.current_tile_size,
                self.camera_offset.y + y1 * self.current_tile_size,
                (x2 - x1 + 1) * self.current_tile_size,
                (y2 - y1 + 1) * self.current_tile_size
            )
            s = pygame.Surface((sel_rect.width, sel_rect.height), pygame.SRCALPHA)
            s.fill((0, 255, 0, 100)) # Semi-transparent green
            self.screen.blit(s, (sel_rect.x, sel_rect.y))
            pygame.draw.rect(self.screen, HIGHLIGHT, sel_rect, 2)

        # Draw Node Placement Feedback
        if self.placing_nodes_for:
            for i, node in enumerate(self.node_buffer):
                nx, ny = node
                screen_x = self.camera_offset.x + (nx / TILE_SIZE) * self.current_tile_size
                screen_y = self.camera_offset.y + (ny / TILE_SIZE) * self.current_tile_size
                pygame.draw.circle(self.screen, ACCENT, (int(screen_x), int(screen_y)), 5)
                self.screen.blit(self.small_font.render(f"Node {i+1}", True, WHITE), (screen_x + 10, screen_y - 10))
            
            # Draw line to current mouse position for next node
            if self.node_buffer:
                mx, my = pygame.mouse.get_pos()
                last_node = self.node_buffer[-1]
                last_x = self.camera_offset.x + (last_node[0] / TILE_SIZE) * self.current_tile_size
                last_y = self.camera_offset.y + (last_node[1] / TILE_SIZE) * self.current_tile_size
                pygame.draw.line(self.screen, ACCENT, (last_x, last_y), (mx, my), 1)

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
        
        btn_save, btn_menu, btn_settings = pygame.Rect(10, 50, UI_WIDTH//3 - 10, 30), pygame.Rect(UI_WIDTH//3 + 5, 50, UI_WIDTH//3 - 10, 30), pygame.Rect(2*UI_WIDTH//3 + 5, 50, UI_WIDTH//3 - 15, 30)
        pygame.draw.rect(self.screen, LIGHT_GRAY, btn_save, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, btn_menu, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, btn_settings, border_radius=5)
        self.screen.blit(self.small_font.render("SAVE", True, WHITE), self.small_font.render("SAVE", True, WHITE).get_rect(center=btn_save.center))
        self.screen.blit(self.small_font.render("MENU", True, WHITE), self.small_font.render("MENU", True, WHITE).get_rect(center=btn_menu.center))
        self.screen.blit(self.small_font.render("SET", True, WHITE), self.small_font.render("SET", True, WHITE).get_rect(center=btn_settings.center))
        
        mx, my = pygame.mouse.get_pos()
        m_clicked = pygame.mouse.get_pressed()[0]
        if m_clicked and not self.mouse_debounce:
            if btn_save.collidepoint(mx, my): self.save_scene(self.current_level_path); pygame.time.wait(200)
            if btn_menu.collidepoint(mx, my): self.state = STATE_MENU; self.refresh_levels(); pygame.time.wait(200)
            if btn_settings.collidepoint(mx, my): self.state = STATE_SETTINGS; pygame.time.wait(200)
        
        tool_y = 95
        stamp_btn, erase_btn, select_btn = pygame.Rect(10, tool_y, UI_WIDTH//3-12, 25), pygame.Rect(UI_WIDTH//3+5, tool_y, UI_WIDTH//3-12, 25), pygame.Rect(2*UI_WIDTH//3+5, tool_y, UI_WIDTH//3-15, 25)
        pygame.draw.rect(self.screen, ACCENT if self.current_tool == "stamp" else LIGHT_GRAY, stamp_btn, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.current_tool == "erase" else LIGHT_GRAY, erase_btn, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.current_tool == "select" else LIGHT_GRAY, select_btn, border_radius=5)
        self.screen.blit(self.small_font.render("STAMP", True, WHITE), self.small_font.render("STAMP", True, WHITE).get_rect(center=stamp_btn.center))
        self.screen.blit(self.small_font.render("ERASE", True, WHITE), self.small_font.render("ERASE", True, WHITE).get_rect(center=erase_btn.center))
        self.screen.blit(self.small_font.render("SELECT", True, WHITE), self.small_font.render("SELECT", True, WHITE).get_rect(center=select_btn.center))
        if m_clicked and not self.mouse_debounce:
            if stamp_btn.collidepoint(mx, my): self.current_tool = "stamp"; self.selection_start = self.selection_end = None
            if erase_btn.collidepoint(mx, my): self.current_tool = "erase"; self.selection_start = self.selection_end = None
            if select_btn.collidepoint(mx, my): self.current_tool = "select"

        zoom_y = 135
        plus, minus, reset = pygame.Rect(20, zoom_y, 40, 25), pygame.Rect(70, zoom_y, 40, 25), pygame.Rect(120, zoom_y, 110, 25)
        pygame.draw.rect(self.screen, LIGHT_GRAY, plus, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, minus, border_radius=5); pygame.draw.rect(self.screen, LIGHT_GRAY, reset, border_radius=5)
        self.screen.blit(self.small_font.render("+", True, WHITE), self.small_font.render("+", True, WHITE).get_rect(center=plus.center))
        self.screen.blit(self.small_font.render("-", True, WHITE), self.small_font.render("-", True, WHITE).get_rect(center=minus.center))
        self.screen.blit(self.small_font.render(f"RESET ({int(self.zoom_level*100)}%)", True, WHITE), self.small_font.render(f"RESET ({int(self.zoom_level*100)}%)", True, WHITE).get_rect(center=reset.center))
        if m_clicked and not self.mouse_debounce:
            if plus.collidepoint(mx, my): self.zoom(0.02)
            if minus.collidepoint(mx, my): self.zoom(-0.02)
            if reset.collidepoint(mx, my): self.recenter()

        # Categories Grid
        self.screen.blit(self.small_font.render("CATEGORIES:", True, GRAY), (20, 175))
        cat_y, btn_w = 195, (UI_WIDTH - 30) // 2
        for i, cat in enumerate(self.main_categories):
            col, row = i % 2, i // 2
            r = pygame.Rect(10 + col * (btn_w + 10), cat_y + row * 30, btn_w, 25)
            color = ACCENT if self.selected_category == cat else BLACK
            pygame.draw.rect(self.screen, color, r, border_radius=5)
            self.screen.blit(self.small_font.render(cat, True, WHITE), self.small_font.render(cat, True, WHITE).get_rect(center=r.center))
            if r.collidepoint(mx, my) and m_clicked and not self.mouse_debounce: 
                self.selected_category, self.edit_scroll_y = cat, 0
                self.selected_item = None
                self.placing_nodes_for = None
                self.node_buffer = []
                if cat != "Tiles": self.selected_sub_category = None
                self.mouse_debounce = True

        item_start_y = cat_y + ((len(self.main_categories) + 1) // 2) * 30 + 10
        if self.selected_category == "Tiles":
            self.screen.blit(self.small_font.render("TILE TYPES:", True, GRAY), (20, item_start_y))
            sub_y = item_start_y + 20
            for i, sub in enumerate(self.tile_sub_categories):
                col, row = i % 2, i // 2
                r = pygame.Rect(10 + col * (btn_w + 10), sub_y + row * 30, btn_w, 25)
                color = HIGHLIGHT if self.selected_sub_category == sub else BLACK
                pygame.draw.rect(self.screen, color, r, border_radius=5)
                t_color = BLACK if self.selected_sub_category == sub else WHITE
                self.screen.blit(self.small_font.render(sub, True, t_color), self.small_font.render(sub, True, t_color).get_rect(center=r.center))
                if r.collidepoint(mx, my) and m_clicked and not self.mouse_debounce: 
                    self.selected_sub_category, self.edit_scroll_y = sub, 0
            item_start_y = sub_y + ((len(self.tile_sub_categories) + 1) // 2) * 30 + 10

        target = self.selected_sub_category if self.selected_category == "Tiles" else self.selected_category
        items = [k for k, v in self.resources.registry.items() if v['category'] == target] if target else []
        cols, padding = 4, 10
        box_size = (UI_WIDTH - (cols + 1) * padding) // cols
        for i, item_id in enumerate(items):
            col, row = i % cols, i // cols
            x, y = padding + col * (box_size + padding), item_start_y + row * (box_size + padding) - self.edit_scroll_y
            if y < item_start_y or y > SCREEN_HEIGHT - 60: continue
            r = pygame.Rect(x, y, box_size, box_size)
            
            # Draw Item Image
            img = self.resources.get_image(item_id)
            if img:
                actual_id = item_id.split('[')[0] if '[' in item_id else item_id
                w_disp = box_size
                if actual_id == "MOVING_PLATFORM":
                    w_disp = box_size * 1.8 # Show it wider but slightly smaller than 2x to fit nicely
                
                self.screen.blit(pygame.transform.scale(img, (int(w_disp), box_size)), (x, y))

            if self.selected_item == item_id: pygame.draw.rect(self.screen, HIGHLIGHT, r.inflate(6, 6), 2, border_radius=5)
            if r.collidepoint(mx, my) and m_clicked and not self.mouse_debounce: self.selected_item = item_id

        # Moving Platform Speed Input
        if self.selected_item == "MOVING_PLATFORM":
            speed_y = item_start_y + ((len(items) + cols - 1) // cols) * (box_size + padding) + 10
            self.screen.blit(self.small_font.render("PLATFORM SPEED:", True, GRAY), (20, speed_y))
            r = pygame.Rect(20, speed_y + 20, UI_WIDTH - 40, 25)
            pygame.draw.rect(self.screen, INPUT_BG, r, border_radius=5)
            pygame.draw.rect(self.screen, ACCENT if self.active_input == "speed" else LIGHT_GRAY, r, 1, border_radius=5)
            self.screen.blit(self.small_font.render(self.platform_speed, True, WHITE), (r.x + 10, r.y + 5))
            if r.collidepoint(mx, my) and m_clicked: self.active_input, self.caret_index = "speed", len(self.platform_speed)

            # Loop Toggle
            loop_y = speed_y + 55
            self.screen.blit(self.small_font.render("LOOP CONTINUOUSLY:", True, GRAY), (20, loop_y))
            checkbox_rect = pygame.Rect(UI_WIDTH - 40, loop_y - 2, 20, 20)
            pygame.draw.rect(self.screen, INPUT_BG, checkbox_rect, border_radius=4)
            pygame.draw.rect(self.screen, ACCENT if self.platform_loop else LIGHT_GRAY, checkbox_rect, 1, border_radius=4)
            if self.platform_loop:
                pygame.draw.rect(self.screen, ACCENT, checkbox_rect.inflate(-8, -8), border_radius=2)
            if checkbox_rect.collidepoint(mx, my) and m_clicked and not self.mouse_debounce:
                self.platform_loop = not self.platform_loop
                self.mouse_debounce = True

        # Trap Direction Selection
        if self.selected_category == "Traps":
            dir_y = item_start_y + ((len(items) + cols - 1) // cols) * (box_size + padding) + 10
            self.screen.blit(self.small_font.render("TRAP DIRECTION:", True, GRAY), (20, dir_y))
            dirs = ["UP", "DOWN", "LEFT", "RIGHT"]
            for i, d in enumerate(dirs):
                col, row = i % 2, i // 2
                r = pygame.Rect(10 + col * (btn_w + 10), dir_y + 20 + row * 30, btn_w, 25)
                color = ACCENT if self.selected_direction == d else BLACK
                pygame.draw.rect(self.screen, color, r, border_radius=5)
                self.screen.blit(self.small_font.render(d, True, WHITE), self.small_font.render(d, True, WHITE).get_rect(center=r.center))
                if r.collidepoint(mx, my) and m_clicked and not self.mouse_debounce:
                    self.selected_direction = d
                    self.mouse_debounce = True

        play_rect = pygame.Rect(20, SCREEN_HEIGHT - 50, UI_WIDTH - 40, 35)
        pygame.draw.rect(self.screen, (0, 150, 0), play_rect, border_radius=8)
        self.screen.blit(self.font.render("PLAY SCENE", True, WHITE), self.font.render("PLAY SCENE", True, WHITE).get_rect(center=play_rect.center))
        if play_rect.collidepoint(mx, my) and m_clicked and not self.mouse_debounce:
            self.save_scene(self.current_level_path); subprocess.Popen([sys.executable, "main.py", self.current_level_path]); pygame.time.wait(200)

    def copy_selection(self):
        if self.selection_start and self.selection_end:
            x1, x2 = min(self.selection_start[0], self.selection_end[0]), max(self.selection_start[0], self.selection_end[0])
            y1, y2 = min(self.selection_start[1], self.selection_end[1]), max(self.selection_start[1], self.selection_end[1])
            
            self.clipboard = {
                'world': [[self.grid_world[y][x] for x in range(x1, x2 + 1)] for y in range(y1, y2 + 1)],
                'entities': [[self.grid_entities[y][x] for x in range(x1, x2 + 1)] for y in range(y1, y2 + 1)]
            }
            print(f"Selection copied: {len(self.clipboard['world'][0])}x{len(self.clipboard['world'])}")

    def paste_selection(self, gx, gy):
        if self.clipboard:
            self.save_state_for_undo()
            for r, row in enumerate(self.clipboard['world']):
                for c, val in enumerate(row):
                    tr, tc = gy + r, gx + c
                    if 0 <= tr < self.rows and 0 <= tc < self.cols:
                        self.grid_world[tr][tc] = val
                        self.grid_entities[tr][tc] = self.clipboard['entities'][r][c]
            print("Selection pasted.")

    def handle_editing_input(self):
        mx, my = pygame.mouse.get_pos()
        m_keys = pygame.mouse.get_pressed()
        if not any(m_keys): self.mouse_debounce = False
        if self.mouse_debounce: return
        
        if mx > UI_WIDTH:
            gx, gy = int((mx - self.camera_offset.x) // self.current_tile_size), int((my - self.camera_offset.y) // self.current_tile_size)
            if 0 <= gx < self.cols and 0 <= gy < self.rows:
                if m_keys[0]: # Left Click
                    if self.current_tool == "stamp":
                        if self.selected_item:
                            if self.selected_item == "MOVING_PLATFORM":
                                if self.placing_nodes_for is None:
                                    self.placing_nodes_for = (gx, gy)
                                    self.node_buffer = [(gx * TILE_SIZE, gy * TILE_SIZE)]
                                    self.mouse_debounce = True
                                elif len(self.node_buffer) < 3:
                                    self.node_buffer.append((gx * TILE_SIZE, gy * TILE_SIZE))
                                    self.mouse_debounce = True
                                    if len(self.node_buffer) == 3:
                                        # Finished placing nodes
                                        px, py = self.placing_nodes_for
                                        nodes_str = "|".join([f"{nx},{ny}" for nx, ny in self.node_buffer])
                                        loop_str = "true" if self.platform_loop else "false"
                                        entity_data = f"MOVING_PLATFORM[nodes:{nodes_str}&speed:{self.platform_speed}&loop:{loop_str}]"
                                        self.save_state_for_undo()
                                        self.grid_entities[py][px] = entity_data
                                        self.placing_nodes_for = None
                                        self.node_buffer = []
                                return

                            info = self.resources.registry[self.selected_item]
                            if info['type'] == 'static':
                                if self.grid_world[gy][gx] != self.selected_item:
                                    self.save_state_for_undo(); self.grid_world[gy][gx] = self.selected_item
                            else:
                                item_to_place = self.selected_item
                                if info['category'] == "Traps":
                                    item_to_place = f"{self.selected_item}[direction:{self.selected_direction}]"
                                
                                if self.grid_entities[gy][gx] != item_to_place:
                                    self.save_state_for_undo(); self.grid_entities[gy][gx] = item_to_place
                                    self.mouse_debounce = True # Prevent entity spam
                    elif self.current_tool == "erase":
                        # FIX: Eraser now clears both layers regardless of selected category.
                        # This ensures 'saved entities' or props can be erased even if a Tile category is active.
                        if self.grid_world[gy][gx] != "-1" or self.grid_entities[gy][gx] != "-1":
                            self.save_state_for_undo()
                            self.grid_world[gy][gx] = "-1"
                            self.grid_entities[gy][gx] = "-1"
                    elif self.current_tool == "select":
                        if not self.selection_start: self.selection_start = (gx, gy)
                        self.selection_end = (gx, gy)
                
                if m_keys[2]: # Right Click always erases both (Fast clear)
                    if self.grid_world[gy][gx] != "-1" or self.grid_entities[gy][gx] != "-1":
                        self.save_state_for_undo()
                        self.grid_world[gy][gx] = "-1"
                        self.grid_entities[gy][gx] = "-1"

        if m_keys[1]:
            if not self.is_panning: self.is_panning, self.last_mouse_pos = True, (mx, my)
            else: self.camera_offset += pygame.Vector2(mx - self.last_mouse_pos[0], my - self.last_mouse_pos[1]); self.last_mouse_pos = (mx, my)
        else: self.is_panning = False

    def draw_settings_screen(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 350, 600, 700)
        pygame.draw.rect(self.screen, DARK_GRAY, panel_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT, panel_rect, 2, border_radius=15)
        
        self.screen.blit(self.header_font.render("LEVEL SETTINGS", True, WHITE), (panel_rect.x + 30, panel_rect.y + 30))
        
        # Level Dimensions
        self.screen.blit(self.bold_font.render("DIMENSIONS (COLS x ROWS)", True, GRAY), (panel_rect.x + 30, panel_rect.y + 90))
        dim_w_rect = pygame.Rect(panel_rect.x + 30, panel_rect.y + 130, 100, 35)
        dim_h_rect = pygame.Rect(panel_rect.x + 150, panel_rect.y + 130, 100, 35)
        
        pygame.draw.rect(self.screen, INPUT_BG, dim_w_rect, border_radius=5)
        pygame.draw.rect(self.screen, INPUT_BG, dim_h_rect, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.active_input == "edit_width" else LIGHT_GRAY, dim_w_rect, 1, border_radius=5)
        pygame.draw.rect(self.screen, ACCENT if self.active_input == "edit_height" else LIGHT_GRAY, dim_h_rect, 1, border_radius=5)
        
        self.screen.blit(self.font.render(str(self.new_level_width), True, WHITE), (dim_w_rect.x + 15, dim_w_rect.y + 5))
        self.screen.blit(self.font.render(str(self.new_level_height), True, WHITE), (dim_h_rect.x + 15, dim_h_rect.y + 5))
        self.screen.blit(self.font.render("x", True, GRAY), (dim_w_rect.right + 5, dim_w_rect.y + 5))

        # Theme Selection
        self.screen.blit(self.bold_font.render("BACKGROUND THEME", True, GRAY), (panel_rect.x + 30, panel_rect.y + 190))
        mx, my = pygame.mouse.get_pos()
        m_clicked = pygame.mouse.get_pressed()[0]
        
        if m_clicked and not self.mouse_debounce:
            if dim_w_rect.collidepoint(mx, my): 
                self.active_input = "edit_width"
                self.caret_index = self.get_caret_from_mouse(mx, dim_w_rect.x, str(self.new_level_width))
                self.mouse_debounce = True
            if dim_h_rect.collidepoint(mx, my): 
                self.active_input = "edit_height"
                self.caret_index = self.get_caret_from_mouse(mx, dim_h_rect.x, str(self.new_level_height))
                self.mouse_debounce = True

        # Draw Carets
        if pygame.time.get_ticks() - self.caret_timer > 500:
            self.caret_visible = not self.caret_visible
            self.caret_timer = pygame.time.get_ticks()

        if self.caret_visible:
            if self.active_input == "edit_width":
                w, _ = self.font.size(str(self.new_level_width)[:self.caret_index])
                pygame.draw.line(self.screen, WHITE, (dim_w_rect.x + 15 + w, dim_w_rect.y + 5), (dim_w_rect.x + 15 + w, dim_w_rect.y + 30), 2)
            elif self.active_input == "edit_height":
                w, _ = self.font.size(str(self.new_level_height)[:self.caret_index])
                pygame.draw.line(self.screen, WHITE, (dim_h_rect.x + 15 + w, dim_h_rect.y + 5), (dim_h_rect.x + 15 + w, dim_h_rect.y + 30), 2)

        for i, theme in enumerate(self.available_themes):
            col, row = i % 4, i // 4
            r = pygame.Rect(panel_rect.x + 30 + col * 135, panel_rect.y + 230 + row * 40, 120, 30)
            color = ACCENT if self.current_theme == theme else LIGHT_GRAY
            pygame.draw.rect(self.screen, color, r, border_radius=5)
            self.screen.blit(self.small_font.render(theme.upper(), True, WHITE), self.small_font.render(theme.upper(), True, WHITE).get_rect(center=r.center))
            if r.collidepoint(mx, my) and m_clicked and not self.mouse_debounce:
                self.current_theme = theme
                self.mouse_debounce = True

        # Parallax Intensity
        self.screen.blit(self.bold_font.render(f"PARALLAX INTENSITY: {self.parallax_intensity:.1f}", True, GRAY), (panel_rect.x + 30, panel_rect.y + 350))
        slider_rect = pygame.Rect(panel_rect.x + 30, panel_rect.y + 390, 540, 10)
        pygame.draw.rect(self.screen, BLACK, slider_rect, border_radius=5)
        handle_x = slider_rect.x + (self.parallax_intensity / 2.0) * slider_rect.width
        handle_rect = pygame.Rect(handle_x - 10, slider_rect.y - 10, 20, 30)
        pygame.draw.rect(self.screen, ACCENT, handle_rect, border_radius=5)
        
        if slider_rect.inflate(0, 40).collidepoint(mx, my) and m_clicked:
            self.parallax_intensity = max(0.0, min(2.0, (mx - slider_rect.x) / slider_rect.width * 2.0))

        # Vertical Offset
        self.screen.blit(self.bold_font.render(f"VERTICAL OFFSET: {int(self.parallax_y_offset)}px", True, GRAY), (panel_rect.x + 30, panel_rect.y + 440))
        v_slider_rect = pygame.Rect(panel_rect.x + 30, panel_rect.y + 480, 540, 10)
        pygame.draw.rect(self.screen, BLACK, v_slider_rect, border_radius=5)
        # Map -300 to 300 into the slider
        v_handle_x = v_slider_rect.x + ((self.parallax_y_offset + 300) / 600.0) * v_slider_rect.width
        v_handle_rect = pygame.Rect(v_handle_x - 10, v_slider_rect.y - 10, 20, 30)
        pygame.draw.rect(self.screen, ACCENT, v_handle_rect, border_radius=5)
        
        if v_slider_rect.inflate(0, 40).collidepoint(mx, my) and m_clicked:
            self.parallax_y_offset = ((mx - v_slider_rect.x) / v_slider_rect.width * 600.0) - 300

        # Buttons: APPLY and CANCEL
        apply_btn = pygame.Rect(panel_rect.centerx - 210, panel_rect.bottom - 70, 200, 45)
        cancel_btn = pygame.Rect(panel_rect.centerx + 10, panel_rect.bottom - 70, 200, 45)
        
        pygame.draw.rect(self.screen, (0, 150, 0), apply_btn, border_radius=10)
        pygame.draw.rect(self.screen, (150, 0, 0), cancel_btn, border_radius=10)
        
        self.screen.blit(self.bold_font.render("APPLY", True, WHITE), self.bold_font.render("APPLY", True, WHITE).get_rect(center=apply_btn.center))
        self.screen.blit(self.bold_font.render("CANCEL", True, WHITE), self.bold_font.render("CANCEL", True, WHITE).get_rect(center=cancel_btn.center))
        
        if m_clicked and not self.mouse_debounce:
            if apply_btn.collidepoint(mx, my):
                # Check for Resizing
                try:
                    nw, nh = int(self.new_level_width), int(self.new_level_height)
                    if nw != self.cols or nh != self.rows:
                        self.resize_level(nw, nh)
                except: pass
                # Save All Changes (CSV and Metadata)
                self.save_scene(self.current_level_path)
                self.state = STATE_EDITING
                self.mouse_debounce = True
            
            if cancel_btn.collidepoint(mx, my):
                # Reset dimension inputs to current grid size before exiting
                self.new_level_width, self.new_level_height = str(self.cols), str(self.rows)
                self.state = STATE_EDITING
                self.mouse_debounce = True

    def run(self):
        while True:
            self.screen.fill(SKY_BLUE)
            
            # Global Mouse Debounce Reset
            if not any(pygame.mouse.get_pressed()):
                self.mouse_debounce = False

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
                    elif self.state == STATE_EDITING or self.state == STATE_SETTINGS:
                        if self.active_input == "speed": self.platform_speed = self.handle_text_input(self.platform_speed, event)
                        elif self.active_input == "edit_width": self.new_level_width = self.handle_text_input(str(self.new_level_width), event)
                        elif self.active_input == "edit_height": self.new_level_height = self.handle_text_input(str(self.new_level_height), event)
                        
                        if mods & pygame.KMOD_CTRL:
                            if event.key == pygame.K_s: self.save_scene(self.current_level_path)
                            if event.key == pygame.K_z: self.undo()
                            if event.key == pygame.K_c: self.copy_selection()
                            if event.key == pygame.K_v: 
                                mx, my = pygame.mouse.get_pos()
                                gx, gy = int((mx - self.camera_offset.x) // self.current_tile_size), int((my - self.camera_offset.y) // self.current_tile_size)
                                self.paste_selection(gx, gy)
                        if event.key == pygame.K_m: self.state = STATE_MENU; self.refresh_levels()
                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    if self.state == STATE_EDITING and (pygame.key.get_mods() & pygame.KMOD_CTRL): self.zoom(event.y * 0.1, pygame.Vector2(mx, my))
                    elif self.state == STATE_MENU: self.menu_scroll_y = max(0, self.menu_scroll_y - event.y * 30)
                    elif self.state == STATE_EDITING and mx < UI_WIDTH: self.edit_scroll_y = max(0, self.edit_scroll_y - event.y * 30)
            if self.state == STATE_MENU: self.draw_menu()
            elif self.state == STATE_CREATE: self.draw_create_screen()
            elif self.state == STATE_EDITING: self.handle_editing_input(); self.draw_grid(); self.draw_editing_ui()
            elif self.state == STATE_SETTINGS: self.draw_grid(); self.draw_settings_screen()
            pygame.display.flip(); self.clock.tick(FPS)
if __name__ == "__main__":
    LevelEditor().run()
