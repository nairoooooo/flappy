import pygame
from pygame.locals import *
import random
import os

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.Font("Jersey10-Regular.ttf", 60)
small_font = pygame.font.Font("Jersey10-Regular.ttf", 40)

#define colours
white = (255, 255, 255)
orange = (255, 102, 0)

# Define theme colors
themes = [
    {"name": "Default", "bg": "img/bg.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (135, 206, 235)},
    {"name": "Night", "bg": "img/bg.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (25, 25, 112)},
    {"name": "Desert", "bg": "img/bg.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (244, 164, 96)},
    {"name": "Forest", "bg": "img/bg.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (34, 139, 34)}
]
current_theme = 0

# Define bird types
bird_types = ["bird", "bat", "butterfly", "rocket"]
current_bird_type = 0

#define game variables
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

# Progressive difficulty variables
difficulty_increase_interval = 5  # Increase difficulty every 5 points
max_scroll_speed = 7
min_pipe_gap = 120

# Load high score from file if it exists
def load_high_score():
    if os.path.exists('high_score.txt'):
        with open('high_score.txt', 'r') as file:
            try:
                return int(file.read())
            except:
                return 0
    return 0

# Save high score to file
def save_high_score(high_score):
    with open('high_score.txt', 'w') as file:
        file.write(str(high_score))

# Load the high score
high_score = load_high_score()
    
# Load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')
mainmenu_img = pygame.image.load('img/mainmenu.png')
start_img = pygame.image.load('img/start.png') if os.path.exists('img/start.png') else button_img 

# Resize the start button to make it smaller (60% of original size)
start_img = pygame.transform.scale(start_img, (int(start_img.get_width() * 0.7), int(start_img.get_height() * 0.5)))

# Force create a visible main menu button
mainmenu_img = pygame.Surface((button_img.get_width(), button_img.get_height()))
mainmenu_img.fill((230, 97, 29))  # Green color
# Add a white border
pygame.draw.rect(mainmenu_img, (255, 255, 255), (0, 0, mainmenu_img.get_width(), mainmenu_img.get_height()), 3)
# Add text
font_menu = pygame.font.SysFont(None, 30) if 'Jersey10-Regular.ttf' not in pygame.font.get_fonts() else pygame.font.Font("Jersey10-Regular.ttf", 25)
menu_text = font_menu.render('MENU', True, (255, 255, 255))
text_rect = menu_text.get_rect(center=(mainmenu_img.get_width()//2, mainmenu_img.get_height()//2))
mainmenu_img.blit(menu_text, text_rect)

try:
    # Load the trophy image
    trophy_img = pygame.image.load('img/trophy.png')
    text_height = 43

    trophy_width = trophy_img.get_width()
    trophy_height = trophy_img.get_height()
    new_height = text_height
    new_width = int((trophy_width / trophy_height) * new_height)
    
    # Resize the trophy image
    trophy_img = pygame.transform.scale(trophy_img, (new_width, new_height))
except:
    # Create a simple trophy if image is missing (now smaller)
    trophy_surface = pygame.Surface((20, 20))  # Smaller size
    trophy_surface.fill((255, 215, 0))  # Gold color
    pygame.draw.polygon(trophy_surface, (255, 255, 255), [(6, 3), (14, 3), (16, 9), (4, 9)])
    pygame.draw.rect(trophy_surface, (255, 255, 255), (9, 9, 2, 8))
    pygame.draw.rect(trophy_surface, (255, 255, 255), (6, 17, 8, 2))
    trophy_img = trophy_surface

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    global score, flying, game_over, scroll_speed, pipe_gap
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flying = False
    game_over = False
    score = 0
    # Reset to starting difficulty
    scroll_speed = 4
    pipe_gap = 180
    return score

def go_to_main_menu():
    global game_started, game_over
    game_started = False
    game_over = False
    reset_game()

def update_difficulty():
    global score, scroll_speed, pipe_gap
    # Calculate difficulty level based on score
    difficulty_level = score // difficulty_increase_interval
    
    # Update scroll speed (game speed)
    new_scroll_speed = min(4 + (difficulty_level * 0.5), max_scroll_speed)
    scroll_speed = new_scroll_speed
    
    # Update pipe gap (smaller gap = harder)
    new_pipe_gap = max(180 - (difficulty_level * 10), min_pipe_gap)
    pipe_gap = int(new_pipe_gap)

def change_bird_type():
    global current_bird_type
    current_bird_type = (current_bird_type + 1) % len(bird_types)
    # Update the bird images
    flappy.load_images(bird_types[current_bird_type])

def change_theme():
    global current_theme, bg
    current_theme = (current_theme + 1) % len(themes)
    theme = themes[current_theme]
    
    # Apply theme changes
    # In a real implementation, you'd load actual themed images
    # For this implementation, we'll just change the sky color
    bg = colorize_surface(bg, theme["sky"])

def colorize_surface(surface, color):
    """Apply a color tint to a surface"""
    colored_surface = surface.copy()
    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return colored_surface

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

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
        if bird_type == "bird":
            self.images = [pygame.image.load(f"img/bird{num}.png") for num in range(1, 4)]
        elif bird_type == "bat":
            # Assuming you have bat images, otherwise use bird images with a color filter
            try:
                self.images = [pygame.image.load(f"img/bat{num}.png") for num in range(1, 4)]
            except:
                self.images = [colorize_surface(pygame.image.load(f"img/bird{num}.png"), (100, 100, 100)) for num in range(1, 4)]
        elif bird_type == "butterfly":
            # Assuming you have butterfly images, otherwise use bird images with a color filter
            try:
                self.images = [pygame.image.load(f"img/butterfly{num}.png") for num in range(1, 4)]
            except:
                self.images = [colorize_surface(pygame.image.load(f"img/bird{num}.png"), (200, 100, 200)) for num in range(1, 4)]
        elif bird_type == "rocket":
            # Assuming you have rocket images, otherwise use bird images with a color filter
            try:
                self.images = [pygame.image.load(f"img/rocket{num}.png") for num in range(1, 4)]
            except:
                self.images = [colorize_surface(pygame.image.load(f"img/bird{num}.png"), (200, 50, 50)) for num in range(1, 4)]
    
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
    
    # Modified to allow for centered positioning
    def set_center(self, x, y):
        self.rect.center = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, self.rect.topleft)
        return action

# Find the draw_game_over function and modify it to include the main menu button
def draw_game_over():
    global high_score, score, game_over
    
    # Update high score if current score is higher
    if score > high_score:
        high_score = score
        save_high_score(high_score)  # Save high score when it's beaten

    # Draw the orange game-over frame
    frame_rect = pygame.Rect(232, 268, 400, 300)
    pygame.draw.rect(screen, orange, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)

    #TROPHY AT GAME OVER FRAME
    screen.blit(trophy_img, (270, 300))  
    
    # Display high score and score
    draw_text(f": {high_score}", font, white, 320, 290)
    draw_text(f"SCORE: {score}", font, white, 260, 350)

    # Bird image in the right side of the game-over frame
    bird_img = flappy.images[0]
    screen.blit(bird_img, (520, 290))

    # Position the buttons side by side in the center
    button_width = button_img.get_width()
    button_spacing = 20
    total_width = button_width * 2 + button_spacing
    start_x = frame_rect.x + (frame_rect.width - total_width) // 2
    
    # Create and draw the restart button on the left
    restart_button = Button(start_x, 450, button_img)
    
    # Create and draw the main menu button on the right
    mainmenu_button = Button(start_x + button_width + button_spacing, 450, mainmenu_img)
    
    # Handle button clicks directly in this function
    if restart_button.draw():
        game_over = False
        reset_game()
    
    if mainmenu_button.draw():
        go_to_main_menu()

def draw_main_menu():
    # Draw background
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    
    # Draw the main menu frame
    frame_rect = pygame.Rect(232, 250, 400, 350)
    pygame.draw.rect(screen, orange, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)
    
    # Draw title
    draw_text("   SNAPPY BIRD", font, white, 270, 280)
    
    # Draw high score with trophy image
    screen.blit(trophy_img, (280, 350))
    draw_text(f": {high_score}", small_font, white, 330, 355)
    
    # Draw bird image
    screen.blit(flappy.images[0], (500, 350))
    
    # Make start button even smaller (40% of original size instead of 60%)
    smaller_start_img = pygame.transform.scale(start_img, 
                                              (int(start_img.get_width() * 0.4), 
                                               int(start_img.get_height() * 0.4)))
    
    # Create "Change Bird" button (replaces "EASY")
    bird_button_img = pygame.Surface((140, 60))
    bird_button_img.fill((50, 150, 200))  # Blue color
    pygame.draw.rect(bird_button_img, white, (0, 0, 140, 60), 3)  # White border
    bird_font = pygame.font.SysFont(None, 20)
    bird_text = bird_font.render('CHANGE BIRD', True, white)
    bird_text_rect = bird_text.get_rect(center=(70, 30))
    bird_button_img.blit(bird_text, bird_text_rect)
    
    # Create "Change Theme" button (replaces "HARD")
    theme_button_img = pygame.Surface((140, 60))
    theme_button_img.fill((150, 100, 200))  # Purple color
    pygame.draw.rect(theme_button_img, white, (0, 0, 140, 60), 3)  # White border
    theme_font = pygame.font.SysFont(None, 20)
    theme_text = theme_font.render('CHANGE THEME', True, white)
    theme_text_rect = theme_text.get_rect(center=(70, 30))
    theme_button_img.blit(theme_text, theme_text_rect)
    
    # Position the buttons
    frame_center_x = frame_rect.x + frame_rect.width // 2
    
    # Start button at lower center
    start_button = Button(0, 0, smaller_start_img)
    start_button.set_center(frame_center_x, 550)  # Move lower
    
    # Left button position (upper left of start button)
    bird_button = Button(0, 0, bird_button_img)
    bird_button.set_center(frame_center_x - 100, 450)
    
    # Right button position (upper right of start button)
    theme_button = Button(0, 0, theme_button_img)
    theme_button.set_center(frame_center_x + 100, 450)
    
    # Draw all buttons and check for clicks
    bird_clicked = bird_button.draw()
    theme_clicked = theme_button.draw()
    start_clicked = start_button.draw()
    
    # Handle button clicks
    if bird_clicked:
        change_bird_type()
    
    if theme_clicked:
        change_theme()
    
    if start_clicked:
        return True
    
    return False

def draw_difficulty_indicator():
    # Show current difficulty on screen during gameplay
    if score > 0:
        difficulty_level = score // difficulty_increase_interval + 1
        max_level = (max_scroll_speed - 4) / 0.5 + 1
        
        # Draw difficulty indicator
        draw_text(f"Level: {difficulty_level}", small_font, white, 20, 60)
        
        # Optionally show current pipe gap and speed
        draw_text(f"Gap: {pipe_gap}", small_font, white, 20, 100)
        draw_text(f"Speed: {scroll_speed:.1f}", small_font, white, 20, 140)

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Main game loop
run = True
while run:
    clock.tick(fps)
    
    # Draw background
    screen.blit(bg, (0, 0))
    
    # Check if game has started
    if game_started:
        # Draw pipes and bird
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
        
        # Draw ground
        screen.blit(ground_img, (ground_scroll, 768))

        # Check if bird has passed pipe
        if len(pipe_group) > 0:
            if (bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and 
                bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and 
                not pass_pipe):
                pass_pipe = True
            if pass_pipe and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
                # Update difficulty when score increases
                update_difficulty()

        # Draw score
        draw_text(str(score), font, white, int(screen_width / 2), 20)
        
        # Draw difficulty indicator
        draw_difficulty_indicator()

        # Check for collision with pipes or ceiling
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        
        # Check for collision with ground
        if flappy.rect.bottom >= 768:
            game_over = True
            flying = False

        # Game logic when flying
        if flying and not game_over:
            # Generate new pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(btm_pipe, top_pipe)
                last_pipe = time_now
            
            # Update pipes and scroll ground
            pipe_group.update()
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0

        # Handle game over state
        if game_over:
            draw_game_over()
    else:
        # Show main menu
        if draw_main_menu():
            game_started = True
            reset_game()
        
        # Scroll ground on main menu too
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save high score before quitting
            save_high_score(high_score)
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_started and not flying and not game_over:
            flying = True
    
    pygame.display.update()

pygame.quit()