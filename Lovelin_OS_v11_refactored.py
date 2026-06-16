import pygame
import os
import datetime
import sys
import time

# --- SYSTEM CONFIG ---
WIDTH, HEIGHT = 1000, 700
PINK = (255, 182, 193)
DARK_PINK = (255, 105, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GUI_ACCENT = (255, 240, 245)
LIGHT_GRAY = (200, 200, 200)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

# --- DIRECTORY SETUP ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
DOCS_PATH = os.path.join(BASE_PATH, "documents")

for path in [DOCS_PATH]:
    os.makedirs(path, exist_ok=True)

# --- FONT CACHING ---
FONT_TITLE = pygame.font.SysFont("Arial", 18, bold=True)
FONT_CONTENT = pygame.font.SysFont("Courier", 16)
FONT_BOOT = pygame.font.SysFont("Courier", 18)
FONT_TIME = pygame.font.SysFont("Courier", 20, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 12)

# --- VERBOSE LOGGING ---
def debug_log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [FOS-KERNEL]: {message}")

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lovelin OS v11.0")
clock = pygame.time.Clock()

def boot_sequence():
    """Simulates a verbose BIOS/Kernel boot screen."""
    boot_logs = [
        "LOVELIN BIOS v9.5.2...",
        "CHECKING RAM... 16384MB OK",
        "INITIALIZING VIRTUAL DISK... OK",
        "LOADING KERNEL.DLL... DONE",
        "ESTABLISHING MOFU-PROTOCOL... ACTIVE",
        "MOUNTING /ASSETS/... OK",
        "MOUNTING /DOCUMENTS/... OK",
        "STARTING GUI ENGINE...",
    ]
    
    # Play boot sound
    sound_path = os.path.join(ASSETS_PATH, "boot.wav")
    if os.path.exists(sound_path):
        try:
            pygame.mixer.Sound(sound_path).play()
            debug_log("Boot sound triggered.")
        except pygame.error as e:
            debug_log(f"Failed to play boot sound: {e}")

    for current_index, line in enumerate(boot_logs):
        screen.fill(BLACK)
        for i in range(current_index + 1):
            txt = FONT_BOOT.render(f"> {boot_logs[i]}", True, (0, 255, 0))
            screen.blit(txt, (50, 50 + (i * 30)))
        
        pygame.display.flip()
        debug_log(line)
        time.sleep(0.4)

# --- BUTTON CLASS ---
class Button:
    def __init__(self, rect, color, text="", action=None):
        self.rect = rect
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.text = text
        self.action = action
        self.hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        if self.text:
            txt = FONT_SMALL.render(self.text, True, WHITE)
            txt_rect = txt.get_rect(center=self.rect.center)
            surface.blit(txt, txt_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.action:
                self.action()
            return True
        return False

# --- WINDOW CLASS ---
class AppWindow:
    HEADER_HEIGHT = 35
    BUTTON_SIZE = 25
    MARGIN = 10
    
    def __init__(self, title, x, y, w, h, resizable=False):
        self.title = title
        self.rect = pygame.Rect(x, y, w, h)
        self.active = False
        self.minimized = False
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.content = "System ready. Write your destiny here..."
        self.scroll_offset = 0
        self.resizable = resizable
        
        # Buttons
        self.close_btn = Button(pygame.Rect(0, 0, self.BUTTON_SIZE, self.BUTTON_SIZE), RED)
        self.minimize_btn = Button(pygame.Rect(0, 0, self.BUTTON_SIZE, self.BUTTON_SIZE), LIGHT_GRAY)
    
    def _get_header_rect(self):
        return pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.HEADER_HEIGHT)
    
    def _update_button_positions(self):
        """Position buttons in header"""
        self.close_btn.rect = pygame.Rect(
            self.rect.right - 30, self.rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE
        )
        self.minimize_btn.rect = pygame.Rect(
            self.rect.right - 65, self.rect.y + 5, self.BUTTON_SIZE, self.BUTTON_SIZE
        )
    
    def draw(self, surface):
        if not self.active or self.minimized:
            return
        
        self._update_button_positions()
        
        # Shadow
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), 
                        border_radius=10)
        
        # Window Body
        pygame.draw.rect(surface, GUI_ACCENT, self.rect, border_radius=10)
        
        # Header
        header_rect = self._get_header_rect()
        pygame.draw.rect(surface, DARK_PINK, header_rect, 
                        border_top_left_radius=10, border_top_right_radius=10)
        
        # Title
        title_surf = FONT_TITLE.render(self.title, True, WHITE)
        surface.blit(title_surf, (self.rect.x + self.MARGIN, self.rect.y + 7))
        
        # Draw buttons
        self.minimize_btn.draw(surface)
        self.close_btn.draw(surface)
        
        # Content area with scrolling
        content_rect = pygame.Rect(
            self.rect.x, 
            self.rect.y + self.HEADER_HEIGHT,
            self.rect.width,
            self.rect.height - self.HEADER_HEIGHT
        )
        pygame.draw.rect(surface, GUI_ACCENT, content_rect)
        
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            y = self.rect.y + self.HEADER_HEIGHT + self.MARGIN + (i * 22) - self.scroll_offset
            if self.rect.y + self.HEADER_HEIGHT <= y <= self.rect.bottom:
                txt = FONT_CONTENT.render(line, True, BLACK)
                surface.blit(txt, (self.rect.x + self.MARGIN, y))

    def handle_event(self, event):
        if not self.active or self.minimized:
            return
        
        header_rect = self._get_header_rect()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if header_rect.collidepoint(event.pos):
                if self.close_btn.handle_event(event):
                    self.active = False
                    debug_log(f"Window closed: {self.title}")
                    return
                elif self.minimize_btn.handle_event(event):
                    self.minimized = True
                    debug_log(f"Window minimized: {self.title}")
                    return
                else:
                    self.dragging = True
                    self.offset_x = self.rect.x - event.pos[0]
                    self.offset_y = self.rect.y - event.pos[1]
                    debug_log(f"Dragging {self.title}")
        
        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                debug_log(f"Dropped {self.title} at {self.rect.topleft}")
            self.dragging = False
        
        if event.type == pygame.MOUSEMOTION:
            self.close_btn.handle_event(event)
            self.minimize_btn.handle_event(event)
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
        
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, self.scroll_offset - event.y * 10)
        
        if event.type == pygame.KEYDOWN:
            if self._handle_keyboard(event):
                return
    
    def _handle_keyboard(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_BACKSPACE:
            self.content = self.content[:-1]
        elif event.key == pygame.K_RETURN:
            self.content += "\n"
        elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.save_file()
        elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.load_file()
        else:
            self.content += event.unicode
        return False

    def save_file(self):
        filename = f"note_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(DOCS_PATH, filename)
        try:
            with open(file_path, "w") as f:
                f.write(self.content)
            debug_log(f"FILE SYSTEM: Saved {filename} to /documents/")
        except IOError as e:
            debug_log(f"FILE SYSTEM ERROR: Failed to save {filename}: {e}")

    def load_file(self):
        """Load the most recent file"""
        try:
            files = [f for f in os.listdir(DOCS_PATH) if f.endswith('.txt')]
            if files:
                latest = max(files, key=lambda f: os.path.getctime(os.path.join(DOCS_PATH, f)))
                with open(os.path.join(DOCS_PATH, latest), 'r') as f:
                    self.content = f.read()
                debug_log(f"FILE SYSTEM: Loaded {latest}")
            else:
                debug_log("FILE SYSTEM: No files to load")
        except IOError as e:
            debug_log(f"FILE SYSTEM ERROR: Failed to load file: {e}")

# --- CALCULATOR WINDOW ---
class Calculator(AppWindow):
    def __init__(self):
        super().__init__("Calculator v1.0", 100, 100, 300, 250)
        self.display = "0"
        self.operation = None
        self.prev_value = None
        self.current_value = ""
        self.buttons = self._create_buttons()
    
    def _create_buttons(self):
        """Create calculator buttons"""
        buttons = {}
        layout = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        x_start = self.rect.x + 10
        y_start = self.rect.y + 80
        btn_width, btn_height = 60, 40
        
        for row_idx, row in enumerate(layout):
            for col_idx, label in enumerate(row):
                x = x_start + col_idx * (btn_width + 5)
                y = y_start + row_idx * (btn_height + 5)
                buttons[label] = Button(pygame.Rect(x, y, btn_width, btn_height), DARK_PINK, label)
        
        return buttons
    
    def draw(self, surface):
        if not self.active or self.minimized:
            return
        
        self._update_button_positions()
        
        # Draw window frame
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), 
                        border_radius=10)
        pygame.draw.rect(surface, GUI_ACCENT, self.rect, border_radius=10)
        
        # Header
        header_rect = self._get_header_rect()
        pygame.draw.rect(surface, DARK_PINK, header_rect, 
                        border_top_left_radius=10, border_top_right_radius=10)
        
        title_surf = FONT_TITLE.render(self.title, True, WHITE)
        surface.blit(title_surf, (self.rect.x + 10, self.rect.y + 7))
        
        self.minimize_btn.draw(surface)
        self.close_btn.draw(surface)
        
        # Display
        display_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 45, self.rect.width - 20, 25)
        pygame.draw.rect(surface, WHITE, display_rect)
        display_text = FONT_CONTENT.render(self.display, True, BLACK)
        surface.blit(display_text, (display_rect.x + 5, display_rect.y + 3))
        
        # Buttons
        for button in self.buttons.values():
            button.draw(surface)
    
    def handle_event(self, event):
        if not self.active or self.minimized:
            return
        
        header_rect = self._get_header_rect()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if header_rect.collidepoint(event.pos):
                if self.close_btn.handle_event(event):
                    self.active = False
                    return
                elif self.minimize_btn.handle_event(event):
                    self.minimized = True
                    return
                else:
                    self.dragging = True
                    self.offset_x = self.rect.x - event.pos[0]
                    self.offset_y = self.rect.y - event.pos[1]
            
            # Check button clicks
            for label, button in self.buttons.items():
                if button.rect.collidepoint(event.pos):
                    self._handle_button_press(label)
        
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons.values():
                button.handle_event(event)
            self.close_btn.handle_event(event)
            self.minimize_btn.handle_event(event)
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
        
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
    
    def _handle_button_press(self, label):
        if label in '0123456789.':
            self.current_value += label
            self.display = self.current_value
        elif label in '+-*/':
            if self.current_value:
                self.prev_value = float(self.current_value)
                self.operation = label
                self.current_value = ""
                self.display = label
        elif label == '=':
            if self.operation and self.current_value and self.prev_value is not None:
                result = self._calculate(self.prev_value, self.operation, float(self.current_value))
                self.display = str(result)
                self.current_value = str(result)
                self.operation = None
                self.prev_value = None
    
    def _calculate(self, a, op, b):
        if op == '+': return a + b
        elif op == '-': return a - b
        elif op == '*': return a * b
        elif op == '/': return a / b if b != 0 else 0
        return 0

# --- TASKBAR CLASS ---
class Taskbar:
    def __init__(self):
        self.apps = []
        self.rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    
    def add_app(self, app_window):
        self.apps.append(app_window)
    
    def draw(self, surface):
        pygame.draw.rect(surface, DARK_PINK, self.rect)
        
        # Draw app icons
        for i, app in enumerate(self.apps):
            icon_x = 10 + i * 55
            icon_rect = pygame.Rect(icon_x, HEIGHT - 45, 40, 40)
            color = GREEN if app.active else (100, 100, 100)
            pygame.draw.rect(surface, color, icon_rect, border_radius=5)
            
            # App label
            label = FONT_SMALL.render(app.title.split()[0], True, WHITE)
            surface.blit(label, (icon_x + 5, HEIGHT - 20))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, app in enumerate(self.apps):
                icon_x = 10 + i * 55
                icon_rect = pygame.Rect(icon_x, HEIGHT - 45, 40, 40)
                if icon_rect.collidepoint(event.pos):
                    if app.minimized:
                        app.minimized = False
                    else:
                        app.active = not app.active
                    debug_log(f"Taskbar: Toggle {app.title} ({app.active})")

# --- MAIN OS CLASS ---
class LovelinOS:
    def __init__(self):
        self.windows = []
        self.taskbar = Taskbar()
        self.running = True
        self.bg_img = self._load_wallpaper()
    
    def _load_wallpaper(self):
        """Load wallpaper if available"""
        wallpaper_path = os.path.join(ASSETS_PATH, "wallpaper.png")
        if os.path.exists(wallpaper_path):
            try:
                bg = pygame.transform.scale(pygame.image.load(wallpaper_path), (WIDTH, HEIGHT))
                debug_log("Wallpaper loaded successfully.")
                return bg
            except pygame.error as e:
                debug_log(f"Failed to load wallpaper: {e}")
        return None
    
    def add_window(self, window):
        """Add window to OS and taskbar"""
        self.windows.append(window)
        self.taskbar.add_app(window)
    
    def run(self):
        """Main OS loop"""
        boot_sequence()
        
        while self.running:
            self._handle_events()
            self._draw()
            clock.tick(60)
        
        self._shutdown()
    
    def _handle_events(self):
        """Process all events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            self.taskbar.handle_event(event)
            
            # Route events to windows (in reverse order for proper layering)
            for window in reversed(self.windows):
                window.handle_event(event)
    
    def _draw(self):
        """Render everything"""
        # Background
        if self.bg_img:
            screen.blit(self.bg_img, (0, 0))
        else:
            screen.fill(PINK)
        
        # Draw windows
        for window in self.windows:
            window.draw(screen)
        
        # Taskbar
        self.taskbar.draw(screen)
        
        # Clock
        curr_time = datetime.datetime.now().strftime("%H:%M:%S")
        time_surf = FONT_TIME.render(curr_time, True, WHITE)
        screen.blit(time_surf, (WIDTH - 110, HEIGHT - 35))
        
        pygame.display.flip()
    
    def _shutdown(self):
        """Clean shutdown"""
        debug_log("Shutdown sequence initiated.")
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

# --- MAIN ---
if __name__ == "__main__":
    os_instance = LovelinOS()
    
    # Create applications
    notepad = AppWindow("Notepad v1.0", 250, 150, 500, 350)
    notepad.active = True
    
    calculator = Calculator()
    
    # Add to OS
    os_instance.add_window(notepad)
    os_instance.add_window(calculator)
    
    # Run
    os_instance.run()
