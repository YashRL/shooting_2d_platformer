import pygame

# Constants
UI_BG = (30, 30, 30)
UI_ACCENT = (255, 100, 0)
UI_HIGHLIGHT = (0, 255, 0)
UI_TEXT = (255, 255, 255)
UI_GRAY = (60, 60, 60)
UI_INPUT_BG = (50, 50, 50)

class UIComponent:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.visible = True

    def handle_event(self, event):
        return False

    def draw(self, screen):
        pass

class Button(UIComponent):
    def __init__(self, rect, text, callback, font=None, color=UI_GRAY):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.font = font or pygame.font.SysFont("Segoe UI", 16)
        self.color = color
        self.hovered = False

    def handle_event(self, event):
        if not self.visible: return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def draw(self, screen):
        if not self.visible: return
        color = UI_ACCENT if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, UI_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Label(UIComponent):
    def __init__(self, x, y, text, font=None, color=UI_TEXT):
        super().__init__((x, y, 0, 0))
        self.text = text
        self.font = font or pygame.font.SysFont("Segoe UI", 16)
        self.color = color

    def draw(self, screen):
        if not self.visible: return
        text_surf = self.font.render(self.text, True, self.color)
        screen.blit(text_surf, self.rect.topleft)

class InputBox(UIComponent):
    def __init__(self, rect, initial_text="", label="", font=None):
        super().__init__(rect)
        self.text = str(initial_text)
        self.label = label
        self.font = font or pygame.font.SysFont("Segoe UI", 16)
        self.active = False
        self.caret_index = len(self.text)
        self.caret_visible = True
        self.caret_timer = pygame.time.get_ticks()

    def handle_event(self, event):
        if not self.visible: return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                # Position caret based on click
                relative_x = event.pos[0] - self.rect.x - 10
                best_idx = 0
                min_diff = float('inf')
                for i in range(len(self.text) + 1):
                    w, _ = self.font.size(self.text[:i])
                    if abs(relative_x - w) < min_diff:
                        min_diff = abs(relative_x - w)
                        best_idx = i
                self.caret_index = best_idx
            else:
                self.active = False
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.caret_index > 0:
                    self.text = self.text[:self.caret_index-1] + self.text[self.caret_index:]
                    self.caret_index -= 1
            elif event.key == pygame.K_DELETE:
                if self.caret_index < len(self.text):
                    self.text = self.text[:self.caret_index] + self.text[self.caret_index+1:]
            elif event.key == pygame.K_LEFT:
                self.caret_index = max(0, self.caret_index - 1)
            elif event.key == pygame.K_RIGHT:
                self.caret_index = min(len(self.text), self.caret_index + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.active = False
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.caret_index] + event.unicode + self.text[self.caret_index:]
                self.caret_index += 1
            return True
        return False

    def draw(self, screen):
        if not self.visible: return
        
        if self.label:
            lbl = self.font.render(self.label, True, (200, 200, 200))
            screen.blit(lbl, (self.rect.x, self.rect.y - 20))

        pygame.draw.rect(screen, UI_INPUT_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, UI_ACCENT if self.active else UI_GRAY, self.rect, 1, border_radius=5)
        
        text_surf = self.font.render(self.text, True, UI_TEXT)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))

        if self.active:
            if pygame.time.get_ticks() - self.caret_timer > 500:
                self.caret_visible = not self.caret_visible
                self.caret_timer = pygame.time.get_ticks()
            
            if self.caret_visible:
                w, _ = self.font.size(self.text[:self.caret_index])
                cx = self.rect.x + 10 + w
                pygame.draw.line(screen, UI_TEXT, (cx, self.rect.y + 5), (cx, self.rect.bottom - 5), 2)

class Panel(UIComponent):
    def __init__(self, rect, color=UI_BG):
        super().__init__(rect)
        self.color = color
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def handle_event(self, event):
        if not self.visible: return False
        
        # Dispatch to children in reverse order (topmost first)
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        
        # Consume mouse events inside panel
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        if not self.visible: return
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.line(screen, UI_GRAY, self.rect.topright, self.rect.bottomright, 1)
        for child in self.children:
            child.draw(screen)
