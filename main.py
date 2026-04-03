import pygame
import sys
import random
import os
import time

# Initialize pygame
pygame.init()

# Setup Display for FULLSCREEN
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
pygame.display.set_caption("Candies for All - Barbie's Interactive Merge Sort")

# Beautiful Barbie Style Color Palette
WHITE = (255, 255, 255)
BLACK = (50, 30, 40)       # Softer dark color instead of raw black
GREEN = (60, 220, 100)     # Minty Green
PINK = (255, 105, 180)     # Barbie Pink
ROSE_PINK = (255, 50, 120) # Bright neon pink for errors and splits
PURPLE = (180, 100, 255)   # Magical Violet
BROWN = (139, 69, 19)      # Classic Chocolate
BLUE_GLOW = (80, 180, 255) # Light Blue

# Fonts changed entirely back to soft rounded styles
font_title = pygame.font.SysFont('comicsansms', int(HEIGHT * 0.06), bold=True)
font_large = pygame.font.SysFont('comicsansms', int(HEIGHT * 0.035), bold=True)
font_med = pygame.font.SysFont('comicsansms', int(HEIGHT * 0.025))
font_small = pygame.font.SysFont('comicsansms', int(HEIGHT * 0.02), italic=True)
font_tiny = pygame.font.SysFont('comicsansms', int(HEIGHT * 0.016), bold=True) # Girly indexing font

def load_img(path, size=None):
    try:
        img = pygame.image.load(os.path.join("assets", path)).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        s = pygame.Surface(size if size else (100, 100), pygame.SRCALPHA)
        pygame.draw.rect(s, (255, 200, 220, 150), s.get_rect(), border_radius=10)
        return s

bg_title = load_img("candy_land.png", (WIDTH, HEIGHT))
bg_game = load_img("candy_runway.png", (WIDTH, HEIGHT))
bg_end = load_img("candy_levelup.png", (WIDTH, HEIGHT))
img_purse = load_img("candy_purse.png", (int(HEIGHT*0.25), int(HEIGHT*0.25)))
img_btn = load_img("start.png", (240, 96))

PRELOADED_CANDIES = [
    {"name": "Sour Candy", "count": 2, "surf": load_img("sour candy.png", (40, 40))},
    {"name": "Lollipop", "count": 3, "surf": load_img("lollipop.png", (40, 40))},
    {"name": "Milk Chocolate", "count": 5, "surf": load_img("chocolate.png", (40, 40))},
    {"name": "Toffee", "count": 6, "surf": load_img("toffee.png", (40, 40))}
]

CANDY_TYPES = {}
candy_imgs = {}
initial_bag = []

# -----------------------------------------------
# Logic Animation Tracking
# -----------------------------------------------
class CandyAnimation:
    def __init__(self, value, start_pos, target_pos, target_node):
        self.value = value
        self.x, self.y = start_pos
        self.target_x, self.target_y = target_pos
        self.target_node = target_node
        self.speed = int(HEIGHT * 0.02)
        self.done = False

    def update(self):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist < self.speed:
            self.x, self.y = self.target_x, self.target_y
            self.done = True
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, surface):
        surface.blit(candy_imgs[self.value], (self.x, self.y))

# -----------------------------------------------
# Visualization Nodes Core Object
# -----------------------------------------------
class Node:
    def __init__(self, candies, level, index_in_level):
        self.candies = list(candies)
        self.level = level
        self.index_in_level = index_in_level
        self.max_size = len(candies)
        
        self.left = None
        self.right = None
        self.parent = None
        
        self.state = "IDLE"
        if self.max_size == 1:
            self.state = "MERGED" 
            
        tree_start_x = int(WIDTH * 0.23) if WIDTH * 0.23 > 300 else 300
        tree_width = WIDTH - tree_start_x - 20
        
        num_nodes_in_level = 2**level
        section_width = tree_width / num_nodes_in_level
        self.x = int(tree_start_x + (index_in_level + 0.5) * section_width)
        
        self.y = int(HEIGHT * 0.20 + level * ((HEIGHT * 0.65) / 4.0))
        
        self.candy_w = 44 
        self.box_width = self.max_size * self.candy_w + 12
        self.box_height = 80 
        
        self.error_time = 0

    def get_rect(self):
        return pygame.Rect(self.x - self.box_width//2, self.y - self.box_height//2, self.box_width, self.box_height)
        
    def get_candy_rect(self, i):
        start_x = self.x - (self.max_size * self.candy_w) // 2
        x_pos = start_x + (i * self.candy_w) + 8 
        return pygame.Rect(x_pos, self.y - 28, 40, 40)

    def draw(self, surface):
        if self.parent and self.parent.state == "MERGED":
            return

        # Softer vibrant colored connecting lines instead of blocky black
        if self.parent:
            p_rect = self.parent.get_rect()
            my_rect = self.get_rect()
            # Thicker white border layer to pop off the dress background!
            pygame.draw.line(surface, WHITE, (self.x, my_rect.top), (self.parent.x, p_rect.bottom), 7)
            # Vibrant Violet core!
            pygame.draw.line(surface, PURPLE, (self.x, my_rect.top), (self.parent.x, p_rect.bottom), 3)

        rect = self.get_rect()
        
        bg_color = (255, 255, 255, 230)
        border_color = PURPLE
        border_width = 3
        
        if self.state == "IDLE":
            border_color = PINK 
            border_width = 5
        elif self.state == "DIVIDED":
            if self.left.state == "MERGED" and self.right.state == "MERGED":
                bg_color = (230, 255, 230, 240)
                border_color = GREEN
                border_width = 5
            else:
                bg_color = (245, 240, 250, 160)
                border_color = (200, 180, 220)
                
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, bg_color, s.get_rect(), border_radius=12)
        pygame.draw.rect(s, border_color, s.get_rect(), border_width, border_radius=12)
        
        if time.time() - self.error_time < 0.4:
            s.fill((255, 100, 160, 200)) # Rose pink error tint instead of scary red
            
        surface.blit(s, rect.topleft)
        
        for i in range(self.max_size):
            crect = self.get_candy_rect(i)
            # Soft pinkish slot placeholders instead of gray
            pygame.draw.rect(surface, (255, 230, 240, 200), crect, border_radius=8)
            pygame.draw.rect(surface, (255, 180, 210, 200), crect, 2, border_radius=8)
            
            # Bright Barbie-Pink Index rendering!
            idx_txt = font_tiny.render(f"[{i}]", True, PINK)
            surface.blit(idx_txt, idx_txt.get_rect(center=(crect.centerx, crect.bottom + 12)))

        for i, val in enumerate(self.candies):
            crect = self.get_candy_rect(i)
            surface.blit(candy_imgs[val], crect.topleft)
            
        if self.state == "IDLE" and self.max_size > 1:
            mid = self.max_size // 2
            split_x = self.get_candy_rect(mid).left - 2
            
            for dy in range(rect.top + 6, rect.bottom - 6, 12):
                pygame.draw.line(surface, WHITE, (split_x, dy), (split_x, dy + 6), 5)
                # Vibrant Magenta dashed line to show scissor cuts!
                pygame.draw.line(surface, ROSE_PINK, (split_x, dy), (split_x, dy + 6), 3)
            
    def divide(self, all_nodes):
        if self.state == "IDLE" and self.max_size > 1:
            mid = self.max_size // 2
            
            self.left = Node(self.candies[:mid], self.level + 1, self.index_in_level * 2)
            self.left.parent = self
            
            self.right = Node(self.candies[mid:], self.level + 1, self.index_in_level * 2 + 1)
            self.right.parent = self
            
            self.candies = []
            self.state = "DIVIDED"
            
            all_nodes.append(self.left)
            all_nodes.append(self.right)
            return True
        return False

def draw_text(surface, text, font, color, x, y, center=True, bg=None):
    if bg:
        rend = font.render(text, True, color, bg)
    else:
        rend = font.render(text, True, color)
    rect = rend.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rend, rect)

def setup_new_game():
    global CANDY_TYPES, candy_imgs, initial_bag, current_array, root, nodes, active_animations, game_message, game_message_color
    
    bases = list(PRELOADED_CANDIES)
    random.shuffle(bases)
    
    CANDY_TYPES.clear()
    candy_imgs.clear()
    initial_bag.clear()
    
    for i, base in enumerate(bases):
        val = i + 1 
        CANDY_TYPES[val] = {"name": base["name"], "count": base["count"]}
        candy_imgs[val] = base["surf"]
        for _ in range(base["count"]):
            initial_bag.append(val)
            
    current_array = list(initial_bag)
    random.shuffle(current_array)
    
    root = Node(current_array, 0, 0)
    root.merge_phase_started = False
    nodes = [root]
    active_animations = []
    
    game_message = "DIVIDE PHASE: Click on the pink outlined boxes to divide the arrays!"
    game_message_color = PINK

# Main Game Configs
STATE_TITLE = 0
STATE_STORY = 1
STATE_GAME = 2
STATE_END = 3

state = STATE_TITLE
start_rect = img_btn.get_rect(center=(WIDTH//2, HEIGHT - HEIGHT//5))

root = None
nodes = []
clock = pygame.time.Clock()
last_update = time.time()
active_animations = []
game_message = ""
game_message_color = PINK

running = True
while running:
    if state == STATE_TITLE:
        screen.blit(bg_title, (0, 0))
    elif state == STATE_GAME:
        screen.blit(bg_game, (0, 0))
    elif state == STATE_END:
        screen.blit(bg_end, (0, 0))
    else:
        screen.fill((255, 230, 240)) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            
            if state == STATE_TITLE:
                if start_rect.collidepoint(pos):
                    state = STATE_STORY
                    
            elif state == STATE_STORY:
                setup_new_game()
                state = STATE_GAME
                
            elif state == STATE_GAME:
                # DIVIDE
                clicked_divide = False
                for node in nodes:
                    if node.state == "IDLE" and node.get_rect().collidepoint(pos):
                        node.divide(nodes)
                        clicked_divide = True
                        game_message = "Divided the array into two smaller halves!"
                        game_message_color = BLUE_GLOW
                        break
                        
                if not any(n.state == "IDLE" for n in nodes):
                    if getattr(root, 'merge_phase_started', False) == False:
                        root.merge_phase_started = True
                        game_message = "MERGE PHASE: Everything is divided. Click the smaller candy to merge!"
                        game_message_color = GREEN
                        
                # MERGE
                if not clicked_divide:
                    for node in nodes:
                        if node.state == "DIVIDED" and node.left.state == "MERGED" and node.right.state == "MERGED":
                            left_clicked = node.left.candies and node.left.get_candy_rect(0).collidepoint(pos)
                            right_clicked = node.right.candies and node.right.get_candy_rect(0).collidepoint(pos)
                                
                            if left_clicked or right_clicked:
                                c1 = node.left.candies[0] if node.left.candies else None
                                c2 = node.right.candies[0] if node.right.candies else None
                                
                                c1_val = c1 if c1 is not None else float('inf')
                                c2_val = c2 if c2 is not None else float('inf')
                                
                                if left_clicked:
                                    if c1_val <= c2_val:
                                        val = node.left.candies.pop(0)
                                        if c2 is not None:
                                            game_message = f"Correct! {CANDY_TYPES[val]['name']} ({val}) is <= {CANDY_TYPES[c2]['name']} ({c2})."
                                        else:
                                            game_message = f"Correct! Right tray is empty, {CANDY_TYPES[val]['name']} goes in."
                                        game_message_color = GREEN
                                        
                                        start_rect_anim = node.left.get_candy_rect(0)
                                        pending = sum(1 for a in active_animations if a.target_node == node)
                                        target_rect_anim = node.get_candy_rect(len(node.candies) + pending)
                                        active_animations.append(CandyAnimation(val, start_rect_anim.topleft, target_rect_anim.topleft, node))
                                        
                                    else:
                                        node.left.error_time = time.time()
                                        game_message = f"Oops! {CANDY_TYPES[c1]['name']} > {CANDY_TYPES[c2]['name']}. Pick the smaller one!"
                                        game_message_color = ROSE_PINK
                                        
                                elif right_clicked:
                                    if c2_val <= c1_val:
                                        val = node.right.candies.pop(0)
                                        if c1 is not None:
                                            game_message = f"Correct! {CANDY_TYPES[val]['name']} ({val}) is <= {CANDY_TYPES[c1]['name']} ({c1})."
                                        else:
                                            game_message = f"Correct! Left tray is empty, {CANDY_TYPES[val]['name']} goes in."
                                        game_message_color = GREEN
                                        
                                        start_rect_anim = node.right.get_candy_rect(0)
                                        pending = sum(1 for a in active_animations if a.target_node == node)
                                        target_rect_anim = node.get_candy_rect(len(node.candies) + pending)
                                        active_animations.append(CandyAnimation(val, start_rect_anim.topleft, target_rect_anim.topleft, node))
                                        
                                    else:
                                        node.right.error_time = time.time()
                                        game_message = f"Oops! {CANDY_TYPES[c2]['name']} > {CANDY_TYPES[c1]['name']}. Pick the smaller one!"
                                        game_message_color = ROSE_PINK
                                        
                                break
                                
            elif state == STATE_END:
                if start_rect.collidepoint(pos):
                    state = STATE_TITLE

    # Draw Layers
    if state == STATE_TITLE:
        box_w, box_h = int(WIDTH * 0.7), int(HEIGHT * 0.35)
        s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        s.fill((255, 255, 255, 220))
        
        t1 = font_title.render("Candies for All!", True, PINK)
        s.blit(t1, t1.get_rect(center=(box_w//2, box_h * 0.25)))
        t2 = font_large.render("Interactive Fashion Show Merge Sort", True, BROWN)
        s.blit(t2, t2.get_rect(center=(box_w//2, box_h * 0.65)))
        
        screen.blit(s, (WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2 - int(HEIGHT*0.05)))
        screen.blit(img_btn, start_rect.topleft)
        draw_text(screen, "[Press ESC at any time to Exit Fullscreen]", font_small, BLACK, WIDTH//2, HEIGHT - 30)

    elif state == STATE_STORY:
        # Scale purse dynamically
        screen.blit(img_purse, (WIDTH//2 - int(HEIGHT*0.125), int(HEIGHT*0.05)))
        
        story = [
            "Barbie's magical purse has jumbled up all 16 candies!",
            "Instead of just using default sorting...",
            "YOU will help her sort exactly like a CSE Engineer!",
            "",
            "INTERACTIVE HOW-TO:",
            "• DIVIDE PHASE: Click on the Pink boxes to split them",
            "in half until every candy sits in its own tiny box.",
            "• MERGE PHASE: Green boxes are ready to merge.",
            "Click on the SMALLER of the two front candies in the children",
            "to bring it to the parent correctly. Follow the Merge Sort rules!",
            "",
            "Click anywhere to begin sorting!"
        ]
        y_offset = int(HEIGHT*0.35)
        for line in story:
            draw_text(screen, line, font_med, BLACK, WIDTH//2, y_offset)
            y_offset += int(HEIGHT * 0.045)

    elif state == STATE_GAME:
        for level in reversed(range(6)):
            for node in nodes:
                if node.level == level:
                    node.draw(screen)
                    
        for anim in active_animations[:]:
            anim.update()
            anim.draw(screen)
            if anim.done:
                anim.target_node.candies.append(anim.value)
                active_animations.remove(anim)
                
                if not anim.target_node.left.candies and not anim.target_node.right.candies:
                    if not any(a.target_node == anim.target_node for a in active_animations):
                        anim.target_node.state = "MERGED"
                        game_message = "Sub-array sorted and merged!"
                        game_message_color = BLUE_GLOW
                        
                        if anim.target_node == root:
                            last_update = time.time()
                            
        # Centralized Message Surface Render Method avoiding trailing overlapping entirely
        box_w = min(1400, WIDTH - 40)
        box_h = int(HEIGHT * 0.08)
        s_msg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(s_msg, (255, 255, 255, 240), s_msg.get_rect(), border_radius=12)
        pygame.draw.rect(s_msg, game_message_color, s_msg.get_rect(), 4, border_radius=12)
        text_rend = font_large.render(game_message, True, game_message_color)
        s_msg.blit(text_rend, text_rend.get_rect(center=(box_w//2, box_h//2)))
        screen.blit(s_msg, (WIDTH//2 - box_w//2, int(HEIGHT * 0.02)))
        
        # Self-bounds constrained Legend Overlay
        legend_w = int(WIDTH * 0.20)  if int(WIDTH * 0.20) > 280 else 280
        legend_h = int(HEIGHT * 0.28) if int(HEIGHT * 0.28) > 240 else 240
        legend_x = int(WIDTH * 0.015)
        legend_y = int(HEIGHT * 0.12)
        
        s_leg = pygame.Surface((legend_w, legend_h), pygame.SRCALPHA)
        pygame.draw.rect(s_leg, (255, 230, 240, 240), s_leg.get_rect(), border_radius=15)
        pygame.draw.rect(s_leg, PINK, s_leg.get_rect(), 4, border_radius=15)
        
        title_rend = font_large.render("Runway Order", True, BROWN)
        s_leg.blit(title_rend, title_rend.get_rect(center=(legend_w//2, int(HEIGHT * 0.035))))
        
        y_offset_leg = int(HEIGHT * 0.085)
        for val in sorted(CANDY_TYPES.keys()):
            s_leg.blit(candy_imgs[val], (20, y_offset_leg))
            txt = f"{val}. {CANDY_TYPES[val]['name']}"
            txt_rend = font_med.render(txt, True, BLACK)
            s_leg.blit(txt_rend, (75, y_offset_leg + 5))
            y_offset_leg += int(HEIGHT * 0.045)
            
        screen.blit(s_leg, (legend_x, legend_y))
        
        # Check Win state constraints
        if root and root.state == "MERGED":
            draw_text(screen, "Perfectly Sorted! Heading to Runway...", font_large, GREEN, WIDTH//2, HEIGHT - int(HEIGHT * 0.08), bg=(255, 255, 255, 200))
            if time.time() - last_update > 4:
                state = STATE_END
                
    elif state == STATE_END:
        box_w, box_h = int(WIDTH * 0.7), int(HEIGHT * 0.4)
        s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        s.fill((255, 255, 255, 220))
        
        t1 = font_title.render("Success!", True, PINK)
        s.blit(t1, t1.get_rect(center=(box_w//2, box_h * 0.2)))
        t2 = font_large.render("Everybody received their perfectly matched candy.", True, BROWN)
        s.blit(t2, t2.get_rect(center=(box_w//2, box_h * 0.6)))
        
        screen.blit(s, (WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2 - int(HEIGHT*0.05)))
        screen.blit(img_btn, start_rect.topleft)
        draw_text(screen, "Click anywhere on the Start Button to Play Again with New Items!", font_small, BLACK, WIDTH//2, HEIGHT//2 + int(HEIGHT*0.35))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()