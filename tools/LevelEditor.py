import pygame
import sys
import os

# Add project root to sys.path to allow absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

import json
import subprocess
from src.engine.core.ResourceManager import ResourceManager
from tools.editor.Camera import EditorCamera
from tools.editor.CommandStack import CommandStack, PlaceTileCommand, PlaceEntityCommand
from tools.editor.UIComponents import Panel, Button, Label, InputBox, UI_ACCENT, UI_HIGHLIGHT, UI_GRAY

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 36
UI_WIDTH = 250
FPS = 60
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# States
STATE_MENU = "menu"
STATE_EDITING = "editing"
STATE_SETTINGS = "settings"

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TheTreeSentinal Engine - Modular Editor")
        self.clock = pygame.time.Clock()
        
        self.resources = ResourceManager(TILE_SIZE)
        self.camera = EditorCamera(UI_WIDTH + 20, 50, TILE_SIZE)
        self.command_stack = CommandStack()
        
        # State
        self.state = STATE_MENU
        self.level_data = {
            "metadata": {"theme": "nature_1", "parallax_intensity": 1.0, "parallax_y_offset": 0},
            "layers": {"main": [], "entities": []}
        }
        self.current_level_name = "new_level"
        self.rows = 25
        self.cols = 50
        
        self.selected_tile = "Concrete_platform_tile_0000"
        self.selected_category = "Tiles"
        self.selected_sub_category = "Concrete"
        self.selected_layer = "BACK" # BACK, FRONT
        self.current_tool = "stamp" # stamp, erase
        
        self.item_grid_y = 310
        self.setup_menu_ui()
        self.setup_ui()
        self.setup_settings_ui()

    def setup_menu_ui(self):
        self.menu_panel = Panel((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), color=(20, 20, 30))
        center_x = SCREEN_WIDTH // 2
        self.menu_panel.add_child(Label(center_x - 150, 80, "LEVEL EDITOR", font=pygame.font.SysFont("Segoe UI", 48, bold=True), color=UI_ACCENT))
        
        # Create New
        self.menu_panel.add_child(Label(center_x - 400, 220, "CREATE NEW LEVEL", font=pygame.font.SysFont("Segoe UI", 24, bold=True), color=WHITE))
        self.name_input = InputBox((center_x - 400, 280, 300, 40), "new_level", "Level Name:")
        self.width_input = InputBox((center_x - 400, 360, 140, 40), "50", "Width (Tiles):")
        self.height_input = InputBox((center_x - 240, 360, 140, 40), "25", "Height (Tiles):")
        self.menu_panel.add_child(self.name_input)
        self.menu_panel.add_child(self.width_input)
        self.menu_panel.add_child(self.height_input)
        self.menu_panel.add_child(Button((center_x - 400, 440, 300, 50), "CREATE LEVEL", self.create_new_level, color=UI_ACCENT))
        
        # Load Existing
        self.menu_panel.add_child(Label(center_x + 50, 220, "LOAD RECENT LEVELS", font=pygame.font.SysFont("Segoe UI", 24, bold=True), color=WHITE))
        levels = sorted([f[:-5] for f in os.listdir("levels") if f.endswith(".json")]) if os.path.exists("levels") else []
        for i, lvl in enumerate(levels[:10]):
            col, row = i // 5, i % 5
            btn = Button((center_x + 50 + col * 210, 280 + row * 45, 200, 35), lvl.upper(), lambda l=lvl: self.load_level_from_menu(l))
            self.menu_panel.add_child(btn)

    def setup_ui(self):
        self.sidebar = Panel((0, 0, UI_WIDTH, SCREEN_HEIGHT))
        self.sidebar.add_child(Label(20, 20, "EDITOR", font=pygame.font.SysFont("Segoe UI", 24, bold=True), color=UI_ACCENT))
        self.name_label = Label(20, 55, f"Level: {self.current_level_name}", color=GRAY)
        self.sidebar.add_child(self.name_label)

        # Actions
        self.sidebar.add_child(Button((10, 80, 50, 30), "SAVE", self.save_level))
        self.sidebar.add_child(Button((65, 80, 50, 30), "SET", self.open_settings))
        self.sidebar.add_child(Button((120, 80, 50, 30), "MENU", self.back_to_menu, color=(100, 50, 50)))
        self.sidebar.add_child(Button((175, 80, 50, 30), "PLAY", self.play_level, color=(0, 150, 0)))
        
        # Tools
        self.sidebar.add_child(Label(20, 125, "TOOLS:", font=pygame.font.SysFont("Segoe UI", 14, bold=True), color=GRAY))
        self.sidebar.add_child(Button((10, 145, 70, 25), "STAMP", lambda: self.set_tool("stamp"), color=UI_ACCENT if self.current_tool == "stamp" else UI_GRAY))
        self.sidebar.add_child(Button((90, 145, 70, 25), "ERASE", lambda: self.set_tool("erase"), color=UI_ACCENT if self.current_tool == "erase" else UI_GRAY))
        self.sidebar.add_child(Button((170, 145, 70, 25), "SELECT", lambda: self.set_tool("select"), color=UI_ACCENT if self.current_tool == "select" else UI_GRAY))

        # Layers
        self.sidebar.add_child(Label(20, 180, "LAYERS:", font=pygame.font.SysFont("Segoe UI", 14, bold=True), color=GRAY))
        self.sidebar.add_child(Button((10, 200, 100, 25), "BACK", lambda: self.set_layer("BACK"), color=UI_ACCENT if self.selected_layer == "BACK" else UI_GRAY))
        self.sidebar.add_child(Button((120, 200, 100, 25), "FRONT", lambda: self.set_layer("FRONT"), color=UI_ACCENT if self.selected_layer == "FRONT" else UI_GRAY))

        # Categories
        self.sidebar.add_child(Label(20, 235, "CATEGORIES:", font=pygame.font.SysFont("Segoe UI", 14, bold=True), color=GRAY))
        cats = ["Tiles", "Enemies", "Props", "Weapons"]
        btn_w = (UI_WIDTH - 30) // 2
        for i, cat in enumerate(cats):
            col, row = i % 2, i // 2
            self.sidebar.add_child(Button((10 + col * (btn_w + 10), 255 + row * 35, btn_w, 30), cat.upper(), lambda c=cat: self.set_category(c)))

    def setup_settings_ui(self):
        self.settings_panel = Panel((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), color=(30, 30, 40))
        center_x = SCREEN_WIDTH // 2
        self.settings_panel.add_child(Label(center_x - 150, 50, "LEVEL SETTINGS", font=pygame.font.SysFont("Segoe UI", 36, bold=True), color=UI_ACCENT))
        
        # Themes
        self.settings_panel.add_child(Label(center_x - 400, 150, "SELECT THEME:", font=pygame.font.SysFont("Segoe UI", 20, bold=True), color=WHITE))
        themes = [f"nature_{i}" for i in range(1, 9)]
        for i, t in enumerate(themes):
            col, row = i % 4, i // 4
            self.settings_panel.add_child(Button((center_x - 400 + col * 105, 190 + row * 45, 100, 35), t.upper(), lambda theme=t: self.set_theme(theme)))

        # Config
        self.settings_panel.add_child(Label(center_x + 50, 150, "PARALLAX CONFIG:", font=pygame.font.SysFont("Segoe UI", 20, bold=True), color=WHITE))
        meta = self.level_data["metadata"]
        self.intensity_input = InputBox((center_x + 50, 210, 200, 40), str(meta.get("parallax_intensity", 1.0)), "Intensity:")
        self.offset_input = InputBox((center_x + 50, 290, 200, 40), str(meta.get("parallax_y_offset", 0)), "Y-Offset:")
        self.settings_panel.add_child(self.intensity_input)
        self.settings_panel.add_child(self.offset_input)
        self.settings_panel.add_child(Button((center_x - 100, 500, 200, 50), "APPLY & BACK", self.apply_settings, color=UI_ACCENT))

    def set_tool(self, tool): self.current_tool = tool; self.setup_ui()
    def set_layer(self, layer): self.selected_layer = layer; self.setup_ui()
    def set_theme(self, theme): self.level_data["metadata"]["theme"] = theme; print(f"Theme: {theme}")
    def open_settings(self): self.state = STATE_SETTINGS
    def back_to_menu(self): self.setup_menu_ui(); self.state = STATE_MENU
    
    def apply_settings(self):
        try:
            self.level_data["metadata"]["parallax_intensity"] = float(self.intensity_input.text)
            self.level_data["metadata"]["parallax_y_offset"] = int(self.offset_input.text)
        except: pass
        self.state = STATE_EDITING

    def set_category(self, cat):
        self.selected_category = cat
        if cat == "Tiles": self.selected_sub_category = "Concrete"
        print(f"Category: {cat}")

    def create_new_level(self):
        self.current_level_name = self.name_input.text
        try: self.cols, self.rows = int(self.width_input.text), int(self.height_input.text)
        except: self.cols, self.rows = 50, 25
        self.initialize_empty_level(self.cols, self.rows)
        self.state = STATE_EDITING; self.setup_ui()

    def load_level_from_menu(self, name):
        self.current_level_name = name; self.load_level_dialog(); self.state = STATE_EDITING; self.setup_ui()

    def initialize_empty_level(self, cols, rows):
        self.cols, self.rows = cols, rows
        self.level_data["layers"]["main"] = [["-1" for _ in range(cols)] for _ in range(rows)]
        self.level_data["layers"]["entities"] = []

    def save_level(self):
        path = os.path.join("levels", f"{self.current_level_name}.json")
        os.makedirs("levels", exist_ok=True)
        with open(path, 'w') as f: json.dump(self.level_data, f, indent=4)
        print(f"Saved: {path}")

    def load_level_dialog(self):
        path = os.path.join("levels", f"{self.current_level_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f: self.level_data = json.load(f)
            self.rows = len(self.level_data["layers"]["main"])
            self.cols = len(self.level_data["layers"]["main"][0])

    def draw_item_grid(self):
        items, sub_cats = [], []
        if self.selected_category == "Tiles":
            for k, v in self.resources.registry.items():
                if v.get('type') == 'static' and v.get('category') not in sub_cats: sub_cats.append(v.get('category'))
            sub_cats = sorted(sub_cats)
            btn_w = (UI_WIDTH - 40) // 3
            for i, sc in enumerate(sub_cats):
                col, row = i % 3, i // 3
                rect = pygame.Rect(10 + col * (btn_w + 10), 330 + row * 25, btn_w, 20)
                color = UI_HIGHLIGHT if self.selected_sub_category == sc else UI_GRAY
                pygame.draw.rect(self.screen, color, rect, border_radius=3)
                txt = pygame.font.SysFont("Segoe UI", 10).render(sc.upper()[:10], True, BLACK if color == UI_HIGHLIGHT else WHITE)
                self.screen.blit(txt, txt.get_rect(center=rect.center))
                if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]: self.selected_sub_category = sc
            self.item_grid_y = 330 + ((len(sub_cats) + 2) // 3) * 25 + 10
            for k, v in self.resources.registry.items():
                if v.get('category') == self.selected_sub_category: items.append(k)
        else:
            self.item_grid_y = 330
            for k, v in self.resources.registry.items():
                if v.get('category') == self.selected_category: items.append(k)
        
        items = sorted(list(set(items)))
        cols, padding = 4, 10
        box_size = (UI_WIDTH - (cols + 1) * padding) // cols
        mx, my = pygame.mouse.get_pos()
        m_clicked = pygame.mouse.get_pressed()[0]
        for i, item_id in enumerate(items):
            col, row = i % cols, i // cols
            x, y = padding + col * (box_size + padding), self.item_grid_y + row * (box_size + padding)
            if y > SCREEN_HEIGHT - 60: break
            rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(self.screen, (20, 20, 20), rect, border_radius=3)
            img = self.resources.get_image(item_id)
            if img: self.screen.blit(pygame.transform.scale(img, (box_size, box_size)), (x, y))
            if self.selected_tile == item_id: pygame.draw.rect(self.screen, UI_HIGHLIGHT, rect, 2, border_radius=3)
            if rect.collidepoint(mx, my) and m_clicked: self.selected_tile = item_id

    def play_level(self):
        self.save_level()
        subprocess.Popen(["conda", "run", "-n", "games", "python", "src/main.py", self.current_level_name])

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if self.state == STATE_MENU: self.menu_panel.handle_event(event); continue
            if self.state == STATE_SETTINGS: self.settings_panel.handle_event(event); continue
            if self.sidebar.handle_event(event): continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2: self.camera.start_panning(event.pos)
                if event.button == 1: self.handle_click(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 2: self.camera.stop_panning()
            if event.type == pygame.MOUSEMOTION:
                self.camera.update_panning(event.pos)
                if pygame.mouse.get_pressed()[0]: self.handle_click(event.pos)
            if event.type == pygame.MOUSEWHEEL: self.camera.zoom(event.y * 0.1, pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN and event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL): self.command_stack.undo()

    def handle_click(self, pos):
        if pos[0] < UI_WIDTH: return
        gx, gy = self.camera.get_grid_pos(pos)
        if 0 <= gx < self.cols and 0 <= gy < self.rows:
            grid = self.level_data["layers"]["main"]
            if self.current_tool == "erase":
                old = grid[gy][gx]
                if old != "-1": self.command_stack.push(PlaceTileCommand(grid, gy, gx, old, "-1"))
                return
            info = self.resources.registry.get(self.selected_tile)
            if not info: return
            if info.get('type') in ['static', 'decor']:
                item = self.selected_tile
                if self.selected_layer == "FRONT": item = f"{self.selected_tile}[layer:front]"
                old = grid[gy][gx]
                if old != item: self.command_stack.push(PlaceTileCommand(grid, gy, gx, old, item))
            else:
                exists = any(e['x'] == gx*TILE_SIZE and e['y'] == gy*TILE_SIZE for e in self.level_data["layers"]["entities"])
                if not exists:
                    ent = {"type": self.selected_tile, "x": gx*TILE_SIZE, "y": gy*TILE_SIZE, "properties": {}}
                    self.command_stack.push(PlaceEntityCommand(self.level_data["layers"]["entities"], ent, True))

    def draw(self):
        if self.state == STATE_MENU: self.menu_panel.draw(self.screen); pygame.display.flip(); return
        if self.state == STATE_SETTINGS: self.settings_panel.draw(self.screen); pygame.display.flip(); return
        self.screen.fill((40, 40, 50))
        grid = self.level_data["layers"]["main"]
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                screen_rect = self.camera.apply_rect(rect)
                if not self.screen.get_rect().colliderect(screen_rect): continue
                tid = grid[r][c]
                if tid != "-1":
                    img = self.resources.get_image(tid)
                    if img: self.screen.blit(pygame.transform.scale(img, (screen_rect.width, screen_rect.height)), screen_rect)
                pygame.draw.rect(self.screen, (60, 60, 70), screen_rect, 1)
        for e in self.level_data["layers"]["entities"]:
            pygame.draw.rect(self.screen, UI_HIGHLIGHT, self.camera.apply_rect(pygame.Rect(e['x'], e['y'], TILE_SIZE, TILE_SIZE)), 2)
        self.sidebar.draw(self.screen); self.draw_item_grid(); pygame.display.flip()

    def run(self):
        while True: self.handle_events(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    sys.path.append(os.getcwd()); LevelEditor().run()
