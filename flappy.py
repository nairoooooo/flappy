import pygame
from pygame.locals import *
import random
import os
import json

pygame.init()

clock = pygame.time.Clock()
fps = 60
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height)) 
pygame.display.set_caption('Flappy Bird')
font = pygame.font.Font("Jersey10-Regular.ttf", 60)
small_font = pygame.font.Font("Jersey10-Regular.ttf", 40)
smaller_font = pygame.font.Font("Jersey10-Regular.ttf", 30)
tiny_font = pygame.font.Font("Jersey10-Regular.ttf", 25)
white = (255, 255, 255)
orange = (255, 102, 0)
dark_green = (34, 139, 34)
light_gray = (211, 211, 211)
black = (0, 0, 0)
themes = [
    {"name": "Default", "bg": "img/bg.svg", "ground": "img/ground.svg", "pipe": "img/pipe.svg", "sky": (135, 206, 235)},
    {"name": "Dark", "bg": "img/nightmode.svg", "ground": "img/ground.svg", "pipe": "img/pipe.svg", "sky": (25, 25, 112)}
]


# User Management Variables
current_user = ""
users_data = {}
showing_user_page = False
create_user_active = False
new_username = ""
keyboard_active = False
selected_user_index = 0
mouse_released = True

current_theme = 0
bird_types = ["bird", "rocket"]
current_bird_type = 0

ground_scroll = 0
scroll_speed = 4  # Starting speed
flying = False
game_over = False
pipe_gap = 180  # Starting with easier gap
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
game_started = False  # New variable to track if game has started
welcome_screen = True  # New variable for welcome screen

showing_bird_selection = False
showing_theme_selection = False
difficulty_increase_interval = 5  # Increase difficulty every 5 points
max_scroll_speed = 7
min_pipe_gap = 120

high_score_updated = False

current_bird_frame = 0  # Track the current bird animation frame
bird_frames = ["img/bird_up.svg", "img/bird_mid.svg", "img/bird_down.svg"]  # Bird animation frames
selected_bird_index = 0  # To allow bird selection/changing
show_game_manual = True  # Show game manual at start
game_over_screen = False  # Track if game over screen is showing

theme_previews = []
for theme in themes:
    try:
        img = pygame.image.load(theme["bg"]).convert_alpha()
        img = pygame.transform.smoothscale(img, (230, 80))
    except Exception:
        img = pygame.Surface((230, 80))
        img.fill(theme["sky"])
    theme_previews.append(img)
    
# Load User Data
def load_users_data():
    if os.path.exists('users_data.json'):
        with open('users_data.json', 'r') as file:
            try:
                return json.load(file)
            except:
                return {}
    return {}

def load_font(size):
    try:
        return pygame.font.Font("Jersey10-Regular.ttf", size)
    except FileNotFoundError:
        return pygame.font.SysFont('arial', size)

# Replace the font declarations
font = load_font(60)
small_font = load_font(40)
smaller_font = load_font(30)
tiny_font = load_font(25)

# Save User Data
def save_users_data():
    with open('users_data.json', 'w') as file:
        json.dump(users_data, file)

# Update User's High Score
def update_high_score(score):
    global users_data, current_user
    if current_user and current_user in users_data:
        if score > users_data[current_user]["high_score"]:
            users_data[current_user]["high_score"] = score
            save_users_data()
            return True
    return False

def load_high_score():
    if os.path.exists('high_score.txt'):
        with open('high_score.txt', 'r') as file:
            try:
                return int(file.read())
            except:
                return 0
    return 0

def save_high_score(high_score):
    with open('high_score.txt', 'w') as file:
        file.write(str(high_score))

high_score = load_high_score()

def load_theme_images():
    global bg, ground_img, pipe_img

    try:
        bg = pygame.image.load(themes[current_theme]["bg"]).convert_alpha()
    except (pygame.error, FileNotFoundError):
        bg = pygame.Surface((screen_width, screen_height))
        bg.fill(themes[current_theme]["sky"])  # Use the sky color from the theme
    

    try:
        ground_img = pygame.image.load(themes[current_theme]["ground"]).convert_alpha()
    except (pygame.error, FileNotFoundError):
        ground_img = pygame.Surface((screen_width, 168))
        ground_img.fill((139, 69, 19))  # Brown
    try:
        pipe_img = pygame.image.load(themes[current_theme]["pipe"]).convert_alpha()
    except (pygame.error, FileNotFoundError):
        pipe_img = pygame.Surface((80, 500))
        pipe_img.fill((0, 128, 0))  # Green
    
    return bg, ground_img, pipe_img
bg, ground_img, pipe_img = load_theme_images()

def load_button_image(path, fallback_text, width, height, bg_color, text_color, border_color, font_size):
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (width, height))
    except Exception:
        img = pygame.Surface((width, height), pygame.SRCALPHA)
        img.fill(bg_color)
        pygame.draw.rect(img, border_color, (0, 0, width, height), 3)
        font_btn = pygame.font.SysFont(None, font_size)
        text = font_btn.render(fallback_text, True, text_color)
        text_rect = text.get_rect(center=(width // 2, height // 2))
        img.blit(text, text_rect)
    return img

button_img = load_button_image(
    'img/restart.svg', 'RESTART', 120, 50,
    (230, 97, 29), white, white, 32
)

mainmenu_img = load_button_image(
    'img/mainmenu.svg', 'MAIN MENU', 300, 80,
    (0, 102, 204), white, white, 40
)
    
back_img = pygame.Surface((80, 40))
back_img.fill((100, 100, 100))  # Gray color
pygame.draw.rect(back_img, white, (0, 0, 80, 40), 3)
font_back = pygame.font.SysFont(None, 28)
back_text = font_back.render('BACK', True, white)
text_rect = back_text.get_rect(center=(40, 20))
back_img.blit(back_text, text_rect)

try:
    start_img = pygame.image.load('img/start.svg').convert_alpha()
    start_img = pygame.transform.scale(start_img, (int(start_img.get_width() * 0.7), int(start_img.get_height() * 0.5)))
except pygame.error:
    start_img = pygame.Surface((100, 50))
    start_img.fill((0, 128, 0))  # Green
    pygame.draw.rect(start_img, white, (0, 0, 100, 50), 3)
    font_start = pygame.font.SysFont(None, 30)
    start_text = font_start.render('START', True, white)
    start_img.blit(start_text, ((100 - start_text.get_width())//2, (50 - start_text.get_height())//2))

try:
    trophy_img = pygame.image.load('img/trophy.svg').convert_alpha()
    text_height = 43

    trophy_width = trophy_img.get_width()
    trophy_height = trophy_img.get_height()
    new_height = text_height
    new_width = int((trophy_width / trophy_height) * new_height)
    trophy_img = pygame.transform.scale(trophy_img, (new_width, new_height))
except:
    trophy_surface = pygame.Surface((20, 20))  # Smaller size
    trophy_surface.fill((255, 215, 0))  # Gold color
    pygame.draw.polygon(trophy_surface, (255, 255, 255), [(6, 3), (14, 3), (16, 9), (4, 9)])
    pygame.draw.rect(trophy_surface, (255, 255, 255), (9, 9, 2, 8))
    pygame.draw.rect(trophy_surface, (255, 255, 255), (6, 17, 8, 2))
    trophy_img = trophy_surface

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_centered_text(text, font, text_col, y):
    img = font.render(text, True, text_col)
    width = img.get_width()
    x = (screen_width - width) // 2
    screen.blit(img, (x, y))

def reset_game():
    global score, flying, game_over, scroll_speed, pipe_gap, high_score_updated, pass_pipe
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flying = False
    game_over = False
    score = 0
    scroll_speed = 4
    pipe_gap = 180
    high_score_updated = False
    pass_pipe = False
    return score

def go_to_main_menu():
    global game_started, game_over, welcome_screen, showing_user_page
    game_started = False
    game_over = False
    welcome_screen = False
    showing_user_page = False
    reset_game()

def update_difficulty():
    global score, scroll_speed, pipe_gap
    difficulty_level = score // difficulty_increase_interval
    new_scroll_speed = min(4 + (difficulty_level * 0.5), max_scroll_speed)
    scroll_speed = new_scroll_speed
    new_pipe_gap = max(180 - (difficulty_level * 10), min_pipe_gap)
    pipe_gap = int(new_pipe_gap)

def change_bird_type(new_type=None):
    global current_bird_type, flappy
    if new_type is not None:
        current_bird_type = new_type
    else:
        current_bird_type = (current_bird_type + 1) % len(bird_types)
    flappy.load_images(bird_types[current_bird_type])
    flappy.index = 0
    flappy.counter = 0
    flappy.image = flappy.images[0]

def change_theme(new_theme=None):
    global current_theme, bg, ground_img, pipe_img
    if new_theme is not None:
        current_theme = new_theme
    else:
        current_theme = (current_theme + 1) % len(themes)
    bg, ground_img, pipe_img = load_theme_images()  # <-- Always reload images!
    for pipe in pipe_group:
        pipe.update_image(pipe_img)

def colorize_surface(surface, color):
    """Apply a color tint to a surface"""
    colored_surface = surface.copy()
    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return colored_surface

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pipe_img.copy()
        self.position = position
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update_image(self, new_image):
        """Update pipe image when theme changes"""
        self.image = new_image.copy()
        if self.position == 1:
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.load_images(bird_types[current_bird_type])
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
    def load_images(self, bird_type):
        self.images = []
        
        if bird_type == "bird":
            # Load the bird SVG images
            try:
                for num in range(1, 4):
                    img = pygame.image.load(f"img/bird{num}.svg").convert_alpha()
                    self.images.append(img)
            except pygame.error:
                bird_img = pygame.Surface((34, 24))
                bird_img.fill((255, 255, 0))  # Yellow
                pygame.draw.ellipse(bird_img, (255, 255, 0), (0, 0, 34, 24))
                pygame.draw.circle(bird_img, (0, 0, 0), (28, 10), 3)  # Eye
                self.images.append(bird_img)
            
        elif bird_type == "rocket":
            try:
                rocket_img = pygame.image.load("img/rocket.svg").convert_alpha()
                for i in range(3):
                    rotated = pygame.transform.rotate(rocket_img, i * 5 - 5)
                    self.images.append(rotated)
            except pygame.error:
                for i in range(3):
                    rocket_img = pygame.Surface((40, 20))
                    rocket_img.fill((200, 50, 50))  # Red
                    pygame.draw.polygon(rocket_img, (220, 220, 220), 
                                      [(0, 10), (30, 0), (30, 20)])  # Rocket body
                    pygame.draw.rect(rocket_img, (220, 220, 220), (30, 3, 10, 14))  # Rocket tail
                    fire_length = 10 + i * 5
                    pygame.draw.polygon(rocket_img, (255, 165, 0), 
                                       [(0, 8), (0, 12), (-fire_length, 10)])  # Fire
                    self.images.append(rocket_img)
        
        # Fallback if no images were loaded
        if len(self.images) == 0:
            for i in range(3):
                fallback = pygame.Surface((34, 24))
                fallback.fill((255, 0, 0))  # Red
                pygame.draw.circle(fallback, (255, 255, 255), (20, 12), 10)
                self.images.append(fallback)
    
    def update(self):
        global flying, game_over
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
        
        if not game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            
            self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)
                self.image = self.images[self.index]
            
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False  # Add clicked state

    def set_center(self, x, y):
        self.rect.center = (x, y)
        
    def draw(self):
        global mouse_released
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked and mouse_released:
                self.clicked = True
                action = True
                mouse_released = False  # Block further clicks until released
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        screen.blit(self.image, self.rect.topleft)
        return action
    
# In the main game loop, modify the event handling:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if welcome_screen:
                    welcome_screen = False
                    showing_user_page = True
                elif not flying and not game_over and game_started:
                    flying = True

def draw_welcome_screen():
    # Create a pulsating effect for the message
    pulse_value = abs(pygame.time.get_ticks() % 1000 - 500) / 500  # Value between 0 and 1
    pulse_size = 25 + int(pulse_value * 5)  # Font size between 25 and 30
    pulse_font = pygame.font.Font("Jersey10-Regular.ttf", pulse_size)
    
    # Background with parallax effect
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    
    # Create a semi-transparent overlay for better text readability
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Draw the game title
    draw_centered_text("SNAPPY BIRD", font, white, 200)
    
    # Draw the bird animation
    bird_img = flappy.images[flappy.index]
    bird_x = (screen_width - bird_img.get_width()) // 2
    bird_y = 350
    screen.blit(bird_img, (bird_x, bird_y))
    
    # Animate the bird
    flappy.counter += 1
    if flappy.counter > 5:
        flappy.counter = 0
        flappy.index = (flappy.index + 1) % len(flappy.images)
    
    # Draw pulsating "Click to continue" message at the bottom
    draw_centered_text("Click to continue", pulse_font, white, 700)
    
    # Draw the version info
    version_text = "v1.0"
    draw_text(version_text, tiny_font, white, 10, screen_height - 40)


# User Page Drawing Function
def draw_user_page(events):
    global showing_user_page, create_user_active, new_username, keyboard_active, selected_user_index, current_user
    
    # Background
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    
    # Dark overlay for better visibility
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # User selection frame
    frame_width = 500
    frame_height = 400
    frame_x = (screen_width - frame_width) // 2
    frame_y = (screen_height - frame_height) // 2
    frame_rect = pygame.Rect(frame_x, frame_y, frame_width, frame_height)
    pygame.draw.rect(screen, dark_green, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 5)
    
    draw_centered_text("WELCOME TO SNAPPY BIRD !", smaller_font, white, frame_y + 40)
    
    # High score table
    table_rect = pygame.Rect(frame_x + 50, frame_y + 90, frame_width - 100, 200)
    pygame.draw.rect(screen, (20, 70, 70), table_rect)
    pygame.draw.rect(screen, white, table_rect, 2)
    
    # Header
    draw_text("Highest Score", small_font, white, table_rect.right - 200, table_rect.y - 40)
    
    # List users and their high scores
    user_list = list(users_data.items())
    start_idx = max(0, min(selected_user_index, len(user_list) - 3))
    
    for i in range(start_idx, min(start_idx + 3, len(user_list))):
        username, data = user_list[i]
        row_color = light_gray if i == selected_user_index else white
        row_rect = pygame.Rect(table_rect.x + 5, table_rect.y + 5 + ((i - start_idx) * 60), table_rect.width - 10, 50)
        pygame.draw.rect(screen, row_color, row_rect)
        
        # Username
        draw_text(username, smaller_font, black, row_rect.x + 10, row_rect.y + 10)
        
        # Score
        score_text = str(data["high_score"])
        draw_text(score_text, smaller_font, black, row_rect.right - 50, row_rect.y + 10)
    
    # Create User Button
    create_button_rect = pygame.Rect(frame_x + frame_width - 180, frame_y + frame_height - 60, 160, 40)
    pygame.draw.rect(screen, orange, create_button_rect)
    pygame.draw.rect(screen, white, create_button_rect, 2)
    draw_text("CREATE A USER", tiny_font, white, create_button_rect.x + 10, create_button_rect.y + 10)
    
    # Draw Create User Interface if active
    if create_user_active:
        create_user_interface(events)
        return False
    
    # Return True if user clicked on a name to select it
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Check if Create User button was clicked
            if create_button_rect.collidepoint(mouse_pos):
                create_user_active = True
                keyboard_active = True
                new_username = ""
                return False
            # Check if a user was selected from the list
            for i in range(start_idx, min(start_idx + 3, len(user_list))):
                username, _ = user_list[i]
                row_rect = pygame.Rect(table_rect.x + 5, table_rect.y + 5 + ((i - start_idx) * 60), table_rect.width - 10, 50)
                if row_rect.collidepoint(mouse_pos):
                    current_user = username
                    selected_user_index = i
                    return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not create_user_active:
                selected_user_index = max(0, selected_user_index - 1)
            elif event.key == pygame.K_DOWN and not create_user_active:
                selected_user_index = min(len(user_list) - 1, selected_user_index + 1)
            elif event.key == pygame.K_RETURN and not create_user_active and user_list:
                current_user = user_list[selected_user_index][0]
                return True
    return False

def create_user_interface(events):
    global new_username, keyboard_active, create_user_active, users_data, current_user

    
    # Draw a modal dialog
    modal_width = 400
    modal_height = 200
    modal_x = (screen_width - modal_width) // 2
    modal_y = (screen_height - modal_height) // 2
    
    # Semi-transparent background
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Darker overlay for modal
    screen.blit(overlay, (0, 0))
    
    # Modal window
    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
    pygame.draw.rect(screen, dark_green, modal_rect)
    pygame.draw.rect(screen, white, modal_rect, 3)
    
    # Title
    draw_centered_text("Enter Username", small_font, white, modal_y + 30)
    
    # Text input field
    input_rect = pygame.Rect(modal_x + 50, modal_y + 80, modal_width - 100, 40)
    pygame.draw.rect(screen, white, input_rect)
    pygame.draw.rect(screen, black, input_rect, 2)
    
    # Display the entered text
    display_text = new_username
    if len(display_text) > 15:  # Limit display length
        display_text = display_text[:15]
    
    text_surface = smaller_font.render(display_text, True, black)
    screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 5))
    
    # Create button
    create_btn_rect = pygame.Rect(modal_x + modal_width - 150, modal_y + modal_height - 50, 100, 30)
    pygame.draw.rect(screen, orange, create_btn_rect)
    pygame.draw.rect(screen, white, create_btn_rect, 2)
    draw_text("Create", tiny_font, white, create_btn_rect.x + 20, create_btn_rect.y + 5)
    
    # Cancel button
    cancel_btn_rect = pygame.Rect(modal_x + 50, modal_y + modal_height - 50, 100, 30)
    pygame.draw.rect(screen, (100, 100, 100), cancel_btn_rect)
    pygame.draw.rect(screen, white, cancel_btn_rect, 2)
    draw_text("Cancel", tiny_font, white, cancel_btn_rect.x + 20, cancel_btn_rect.y + 5)
    
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and keyboard_active:
            if event.key == pygame.K_BACKSPACE:
                new_username = new_username[:-1]
            elif event.key == pygame.K_RETURN:
                if len(new_username) > 0 and new_username not in users_data:
                    users_data[new_username] = {"high_score": 0}
                    save_users_data()
                    current_user = new_username
                    create_user_active = False
                    keyboard_active = False
            elif event.unicode.isprintable() and len(new_username) < 20:
                new_username += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if create_btn_rect.collidepoint(mouse_pos) and len(new_username) > 0 and new_username not in users_data:
                users_data[new_username] = {"high_score": 0}
                save_users_data()
                current_user = new_username
                create_user_active = False
                keyboard_active = False
                pygame.event.clear()
                return True
            elif cancel_btn_rect.collidepoint(mouse_pos):
                create_user_active = False
                keyboard_active = False
                pygame.event.clear()
    return False

# Modify draw_game_over function to handle user high scores
def draw_game_over():
    global high_score, score, game_over, users_data, current_user
    
    # Update the user's high score
    is_new_high_score = update_high_score(score)
    
    # Get the high score to display (user's high score or global high score)
    display_high_score = users_data[current_user]["high_score"] if current_user in users_data else high_score
    
    frame_color = orange if current_theme == 0 else (50, 50, 100)
    
    frame_rect = pygame.Rect(232, 268, 400, 300)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)

    screen.blit(trophy_img, (270, 300))  
    draw_text(f": {display_high_score}", font, white, 320, 290)
    
    # Show username above high score
    if current_user:
        draw_text(f"Player: {current_user}", smaller_font, white, 260, 250)
    
    draw_text(f"SCORE: {score}", font, white, 260, 350)
    bird_img = flappy.images[0]
    bird_box = pygame.Rect(520, 290, bird_img.get_width() + 10, bird_img.get_height() + 10)
    pygame.draw.rect(screen, white, bird_box)

    screen.blit(bird_img, (520, 290))

    restart_button = Button(320, 450, button_img)
    mainmenu_button = Button(420, 450, mainmenu_img)
    
    mouse_pos = pygame.mouse.get_pos()

    if restart_button.draw():
        reset_game()
        # Do NOT set game_started = False here!
        return True
    
    if mainmenu_button.draw():
        go_to_main_menu()
        return True
    
    return False

# Update the main game loop to include the user page
users_data = load_users_data()

def draw_main_menu():
    global showing_bird_selection, showing_theme_selection, mouse_released
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    frame_color = orange if current_theme == 0 else (50, 50, 100)
    frame_rect = pygame.Rect(232, 250, 400, 350)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)
    draw_text("   SNAPPY BIRD", font, white, 270, 280)
    screen.blit(trophy_img, (280, 350))
    draw_text(f": {high_score}", small_font, white, 330, 355)
    bird_img = flappy.images[0]
    bird_box = pygame.Rect(500, 350, bird_img.get_width() + 10, bird_img.get_height() + 10)
    pygame.draw.rect(screen, white, bird_box)
    screen.blit(flappy.images[0], (500, 350))
    smaller_start_img = pygame.transform.scale(start_img, 
                                              (int(start_img.get_width() * 0.7), 
                                               int(start_img.get_height() * 0.7)))
    bird_button_img = pygame.Surface((140, 60))
    bird_button_img.fill((50, 150, 200))  # Blue color
    pygame.draw.rect(bird_button_img, white, (0, 0, 140, 60), 3)  # White border
    bird_font = pygame.font.SysFont(None, 20)
    bird_text = bird_font.render(f'BIRD: {bird_types[current_bird_type].upper()}', True, white)
    bird_text_rect = bird_text.get_rect(center=(70, 30))
    bird_button_img.blit(bird_text, bird_text_rect)
    theme_button_img = pygame.Surface((140, 60))
    theme_button_img.fill((150, 100, 200))  # Purple color
    pygame.draw.rect(theme_button_img, white, (0, 0, 140, 60), 3)  # White border
    theme_font = pygame.font.SysFont(None, 20)
    theme_text = theme_font.render(f'THEME: {themes[current_theme]["name"]}', True, white)
    theme_text_rect = theme_text.get_rect(center=(70, 30))
    theme_button_img.blit(theme_text, theme_text_rect)
    frame_center_x = frame_rect.x + frame_rect.width // 2
    start_button = Button(0, 0, smaller_start_img)
    start_button.set_center(frame_center_x, 550)
    bird_button = Button(0, 0, bird_button_img)
    bird_button.set_center(frame_center_x - 100, 450)
    theme_button = Button(0, 0, theme_button_img)
    theme_button.set_center(frame_center_x + 100, 450)
    
    
    bird_clicked = bird_button.draw()
    theme_clicked = theme_button.draw()
    start_clicked = start_button.draw()
    
    if bird_clicked:
        showing_bird_selection = True
        mouse_released = False

    if theme_clicked:
        showing_theme_selection = True
        mouse_released = False
    
    if start_clicked:
        return True
    
    return False

def draw_bird_selection():
    global showing_bird_selection
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    frame_color = orange if current_theme == 0 else (50, 50, 100)
    frame_rect = pygame.Rect(132, 200, 600, 450)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)
    draw_text("SELECT BIRD", font, white, 250, 220)
    back_button = Button(20, 20, back_img)

    button_width = 250
    button_height = 150
    spacing_x = 60
    total_width = len(bird_types) * button_width + (len(bird_types) - 1) * spacing_x
    start_x = frame_rect.centerx - total_width // 2
    y_center = frame_rect.y + 320

    bird_buttons = []
    for i, bird_type in enumerate(bird_types):
        # Prepare button surface
        button_img = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        button_color = (50, 150, 200) if i == current_bird_type else (80, 80, 80)
        button_img.fill(button_color)
        pygame.draw.rect(button_img, white, (0, 0, button_width, button_height), 3)
        btn_font = pygame.font.SysFont(None, 30)
        btn_text = btn_font.render(bird_type.upper(), True, white)
        text_rect = btn_text.get_rect(center=(button_width//2, 30))
        button_img.blit(btn_text, text_rect)

        # Load and center bird image
        try:
            if bird_type == "bird":
                bird_img = pygame.image.load("img/bird1.svg").convert_alpha()
            elif bird_type == "rocket":
                bird_img = pygame.image.load("img/rocket.svg").convert_alpha()
            else:
                bird_img = pygame.Surface((34, 24))
                bird_img.fill((255, 0, 0))
        except Exception:
            bird_img = pygame.Surface((34, 24))
            bird_img.fill((255, 0, 0))
        bird_rect = bird_img.get_rect(center=(button_width//2, button_height//2 + 20))
        button_img.blit(bird_img, bird_rect)

        button = Button(0, 0, button_img)
        button.set_center(start_x + i * (button_width + spacing_x) + button_width // 2, y_center)
        bird_buttons.append(button)

    # Draw and handle bird buttons
    for i, button in enumerate(bird_buttons):
        if button.draw():
            change_bird_type(i)
            showing_bird_selection = False

    if back_button.draw():
        showing_bird_selection = False

def draw_theme_selection():
    global showing_theme_selection, theme_previews
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    frame_color = orange if current_theme == 0 else (50, 50, 100)
    original_theme = current_theme
    frame_rect = pygame.Rect(132, 200, 600, 450)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)
    draw_text("SELECT THEME", font, white, 250, 220)
    back_button = Button(20, 20, back_img)

    button_width = 250
    button_height = 150
    spacing_x = 60
    total_width = len(themes) * button_width + (len(themes) - 1) * spacing_x
    start_x = frame_rect.centerx - total_width // 2
    y_center = frame_rect.y + 320

    theme_buttons = []
    for i, theme in enumerate(themes):
        button_img = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
        button_color = (150, 100, 200) if i == current_theme else (80, 80, 80)
        button_img.fill(button_color)
        pygame.draw.rect(button_img, white, (0, 0, button_width, button_height), 3)
        btn_font = pygame.font.SysFont(None, 30)
        
        btn_text = btn_font.render(theme["name"].upper(), True, white)
        
        text_rect = btn_text.get_rect(center=(button_width//2, 30))
        button_img.blit(btn_text, text_rect)
        
        preview_img = theme_previews[i]
        
        preview_rect = preview_img.get_rect(center=(button_width//2, button_height//2 + 20))
        button_img.blit(preview_img, preview_rect)
        button = Button(0, 0, button_img)
        button.set_center(start_x + i * (button_width + spacing_x) + button_width // 2, y_center)
        theme_buttons.append(button)

        # Draw and handle theme buttons
    for i, button in enumerate(theme_buttons):
        if button.draw():
            change_theme(i)
            showing_theme_selection = False

    if back_button.draw():
        if current_theme != original_theme:
            change_theme(original_theme)
        showing_theme_selection = False

def draw_gameplay_ui():
    draw_text(str(score), font, white, int(screen_width / 2), 20)

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.empty()
bird_group.add(flappy)

run = True

def load_svg(filename):
    return pygame.image.load(filename).convert_alpha()

# Load the SVG assets
game_manual_img = load_svg("img/game.svg")
game_over_img = load_svg("img/gameover.svg")
bird_up_img = load_svg("img/bird_up.svg")
bird_mid_img = load_svg("img/bird_mid.svg")
bird_down_img = load_svg("img/bird_down.svg")

def animate_bird():
    global current_bird_frame
    # Change bird frame every few frames for animation
    if pygame.time.get_ticks() % 10 == 0:
        current_bird_frame = (current_bird_frame + 1) % 3
    return load_svg(bird_frames[current_bird_frame])

def change_bird():
    global selected_bird_index
    selected_bird_index = (selected_bird_index + 1) % 3  # Cycle through birds
    # If you have different bird sets, update bird_frames here

while run:
    clock.tick(fps)
    events = pygame.event.get()  # Only call once per frame

    for event in events:
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_released = True
            
    # --- Show game manual at start ---
    if show_game_manual:
        screen.blit(game_manual_img, (screen_width//2 - game_manual_img.get_width()//2, 
                                  screen_height//2 - game_manual_img.get_height()//2))
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                show_game_manual = False  # <-- Hide manual and proceed
        pygame.display.update()
        continue

    # --- Show welcome screen ---
    if welcome_screen:
        draw_welcome_screen()
        for event in events:
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                welcome_screen = False
                showing_user_page = True
        pygame.display.update()
        continue

    # Main menu and overlays
    if not game_started:
        if showing_bird_selection:
            draw_bird_selection()
        elif showing_theme_selection:
            draw_theme_selection()
        elif showing_user_page:
            if draw_user_page(events):  # User has been selected
                showing_user_page = False
                game_started = False  # Go to main menu after user selection
        else:
            if draw_main_menu():
                flying = True
                game_started = True
        pygame.display.update()
        continue

    # Handle quit and global events
    for event in events:
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                change_bird()

    # Game over screen
    if game_over:
        if not high_score_updated:
            update_high_score(score)
            high_score_updated = True
        draw_game_over()
        pygame.display.update()
        continue

    # Normal game flow
    screen.blit(bg, (0, 0))
    if showing_bird_selection:
        draw_bird_selection()
    elif showing_theme_selection:
        draw_theme_selection()
    elif game_started:
        pipe_group.update()
        pipe_group.draw(screen)
        current_bird_img = animate_bird()
        screen.blit(current_bird_img, (flappy.rect.x, flappy.rect.y))
        bird_group.update()
        screen.blit(ground_img, (ground_scroll, 768))
        if game_over:
            draw_game_over()
        else:
            if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
                game_over = True
                game_over_screen = True
            if flappy.rect.bottom >= 768:
                game_over = True
                flying = False
                game_over_screen = True

            update_difficulty()
            draw_gameplay_ui()
            if len(pipe_group) > 0:
                if (bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and
                    bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and
                    not pass_pipe):
                    pass_pipe = True

                if pass_pipe:
                    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                        score += 1
                        pass_pipe = False

            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0
    else:
        if draw_main_menu():
            flying = True

    pygame.display.update()

pygame.quit()