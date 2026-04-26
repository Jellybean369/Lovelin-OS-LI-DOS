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

# --- DIRECTORY SETUP ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
DOCS_PATH = os.path.join(BASE_PATH, "documents")

if not os.path.exists(DOCS_PATH):
    os.makedirs(DOCS_PATH)

# --- VERBOSE LOGGING ---
def debug_log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [FOS-KERNEL]: {message}")

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lovelie FOS v10.0")
clock = pygame.time.Clock()

def boot_sequence():
    """Simulates a verbose BIOS/Kernel boot screen."""
    font = pygame.font.SysFont("Courier", 18)
    boot_logs = [
        "LOVELIE BIOS v9.5.2...",
        "CHECKING RAM... 16384MB OK",
        "INITIALIZING VIRTUAL DISK... OK",
        "LOADING KERNEL.DLL... DONE",
        "ESTABLISHING MOFU-PROTOCOL... ACTIVE",
        "MOUNTING /ASSETS/... OK",
        "MOUNTING /DOCUMENTS/... OK",
        "STARTING GUI ENGINE...",
    ]
    
    # Play boot sound early if possible
    sound_path = os.path.join(ASSETS_PATH, "boot.wav")
    if os.path.exists(sound_path):
        try:
            pygame.mixer.Sound(sound_path).play()
            debug_log("Boot sound triggered.")
        except: pass

    y_offset = 50
    for line in boot_logs:
        screen.fill(BLACK)
        # Draw current lines
        current_index = boot_logs.index(line)
        for i in range(current_index + 1):
            txt = font.render(f"> {boot_logs[i]}", True, (0, 255, 0))
            screen.blit(txt, (50, 50 + (i * 30)))
        
        pygame.display.flip()
        debug_log(line)
        time.sleep(0.4) # Pause to make it readable

# --- WINDOW CLASS ---
class AppWindow:
    def __init__(self, title, x, y, w, h):
        self.title = title
        self.rect = pygame.Rect(x, y, w, h)
        self.active = False
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.content = "System ready. Write your destiny here..."
        
    def draw(self, surface):
        if not self.active: return
        
        # Shadow
        pygame.draw.rect(surface, (50, 50, 50), (self.rect.x+4, self.rect.y+4, self.rect.width, self.rect.height), border_radius=10)
        # Window Body
        pygame.draw.rect(surface, GUI_ACCENT, self.rect, border_radius=10)
        # Header
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
        pygame.draw.rect(surface, DARK_PINK, header_rect, border_top_left_radius=10, border_top_right_radius=10)
        
        # Title
        font = pygame.font.SysFont("Arial", 18, bold=True)
        title_surf = font.render(self.title, True, WHITE)
        surface.blit(title_surf, (self.rect.x + 10, self.rect.y + 7))
        
        # Close Button
        close_btn = pygame.Rect(self.rect.right - 30, self.rect.y + 5, 25, 25)
        pygame.draw.rect(surface, (200, 50, 50), close_btn, border_radius=5)
        
        # Content
        c_font = pygame.font.SysFont("Courier", 18)
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            txt = c_font.render(line, True, BLACK)
            surface.blit(txt, (self.rect.x + 10, self.rect.y + 45 + (i * 22)))

    def handle_event(self, event):
        if not self.active: return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Header collision for dragging
            header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 35)
            if header_rect.collidepoint(event.pos):
                # Check for close button first
                if event.pos[0] > self.rect.right - 30:
                    self.active = False
                    debug_log(f"Window closed: {self.title}")
                else:
                    self.dragging = True
                    self.offset_x = self.rect.x - event.pos[0]
                    self.offset_y = self.rect.y - event.pos[1]
                    debug_log(f"Dragging {self.title}")

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                debug_log(f"Dropped {self.title} at {self.rect.topleft}")
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.rect.x = event.pos[0] + self.offset_x
            self.rect.y = event.pos[1] + self.offset_y

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.content = self.content[:-1]
            elif event.key == pygame.K_RETURN:
                self.content += "\n"
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_file()
            else:
                self.content += event.unicode

    def save_file(self):
        filename = f"note_{datetime.datetime.now().strftime('%H%M%S')}.txt"
        file_path = os.path.join(DOCS_PATH, filename)
        with open(file_path, "w") as f:
            f.write(self.content)
        debug_log(f"FILE SYSTEM: Saved {filename} to /documents/")

# --- SETUP ---
boot_sequence()
notepad = AppWindow("Notepad v1.0", 250, 150, 500, 350)
running = True

# Load Wallpaper
wallpaper_path = os.path.join(ASSETS_PATH, "wallpaper.png")
bg_img = None
if os.path.exists(wallpaper_path):
    bg_img = pygame.transform.scale(pygame.image.load(wallpaper_path), (WIDTH, HEIGHT))
    debug_log("Wallpaper loaded successfully.")

# --- MAIN LOOP ---
while running:
    # 1. DRAWING
    if bg_img:
        screen.blit(bg_img, (0, 0))
    else:
        screen.fill(PINK)
        
    # Taskbar
    pygame.draw.rect(screen, DARK_PINK, (0, HEIGHT-50, WIDTH, 50))
    # Start Icon
    start_icon = pygame.Rect(10, HEIGHT-45, 40, 40)
    pygame.draw.rect(screen, WHITE, start_icon, border_radius=5)
    
    # 2. EVENT HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_icon.collidepoint(event.pos):
                notepad.active = not notepad.active
                debug_log(f"Start Menu Action: Toggle Notepad ({notepad.active})")
        
        notepad.handle_event(event)

    notepad.draw(screen)
    
    # Time
    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
    time_surf = pygame.font.SysFont("Courier", 20, bold=True).render(curr_time, True, WHITE)
    screen.blit(time_surf, (WIDTH - 110, HEIGHT - 35))

    pygame.display.flip()
    clock.tick(60)

debug_log("Shutdown sequence initiated.")
pygame.mixer.quit()
pygame.quit()
sys.exit()