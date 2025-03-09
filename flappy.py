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

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
game_started = False  # New variable to track if game has started

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
start_img = pygame.image.load('img/start.png') if os.path.exists('img/start.png') else button_img  # Use restart as fallback

# Resize the start button to make it smaller (60% of original size)
start_img = pygame.transform.scale(start_img, (int(start_img.get_width() * 0.6), int(start_img.get_height() * 0.6)))

# Force create a visible main menu button
mainmenu_img = pygame.Surface((button_img.get_width(), button_img.get_height()))
mainmenu_img.fill((50, 200, 50))  # Green color
# Add a white border
pygame.draw.rect(mainmenu_img, (255, 255, 255), (0, 0, mainmenu_img.get_width(), mainmenu_img.get_height()), 3)
# Add text
font_menu = pygame.font.SysFont(None, 30) if 'Jersey10-Regular.ttf' not in pygame.font.get_fonts() else pygame.font.Font("Jersey10-Regular.ttf", 25)
menu_text = font_menu.render('MENU', True, (255, 255, 255))
text_rect = menu_text.get_rect(center=(mainmenu_img.get_width()//2, mainmenu_img.get_height()//2))
mainmenu_img.blit(menu_text, text_rect)

# Then modify the draw_game_over function:
def draw_game_over():
    global high_score, score, game_over
    
   
    if score > high_score:
        high_score = score
        save_high_score(high_score)  

   
    frame_rect = pygame.Rect(232, 268, 400, 300)
    pygame.draw.rect(screen, orange, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10) 

   
    screen.blit(trophy_img, (240, 280))  
    
    # Display high score and score
    draw_text(f": {high_score}", font, white, 320, 290)
    draw_text(f"SCORE: {score}", font, white, 260, 350)

    # Bird image in the right side of the game-over frame
    bird_img = flappy.images[0]
    screen.blit(bird_img, (520, 290))

    # Create and position buttons
    restart_button_x = 280
    mainmenu_button_x = 420
    buttons_y = 450
    
    # Draw the restart button
    restart_button = Button(restart_button_x, buttons_y, button_img)
    
    # Draw the main menu button (force draw the image)
    screen.blit(mainmenu_img, (mainmenu_button_x, buttons_y))
    
    # Handle restart button click
    if restart_button.draw():
        game_over = False
        reset_game()
    
    # Handle main menu button click manually
    pos = pygame.mouse.get_pos()
    menu_rect = pygame.Rect(mainmenu_button_x, buttons_y, mainmenu_img.get_width(), mainmenu_img.get_height())
    if menu_rect.collidepoint(pos):
        if pygame.mouse.get_pressed()[0] == 1:
            go_to_main_menu()

try:
    trophy_img = pygame.image.load('img/trophy.png')
except:
    # Create a simple trophy if image is missing
    trophy_surface = pygame.Surface((32, 32))
    trophy_surface.fill((255, 215, 0))  # Gold color
    pygame.draw.polygon(trophy_surface, (255, 255, 255), [(10, 5), (22, 5), (25, 15), (7, 15)])
    pygame.draw.rect(trophy_surface, (255, 255, 255), (14, 15, 4, 12))
    pygame.draw.rect(trophy_surface, (255, 255, 255), (10, 27, 12, 3))
    trophy_img = trophy_surface

# Function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    global score, flying, game_over
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flying = False
    game_over = False
    score = 0
    return score

def go_to_main_menu():
    global game_started, game_over
    game_started = False
    game_over = False
    reset_game()

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
        self.images = [pygame.image.load(f"img/bird{num}.png") for num in range(1, 4)]
        self.index = 0
        self.counter = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
    
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

    # Trophy at the upper left of the game-over frame
    screen.blit(trophy_img, (240, 280))  
    
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
    
    # Draw high score
    screen.blit(trophy_img, (280, 350))
    draw_text(f": {high_score}", small_font, white, 330, 355)
    
    # Draw bird image
    screen.blit(flappy.images[0], (500, 350))
    
    # Create start button and center it
    start_button = Button(0, 0, start_img)
    # Center the button in the frame - horizontally and vertically
    frame_center_x = frame_rect.x + frame_rect.width // 2
    frame_center_y = 500  # Position it a bit lower in the frame for better spacing
    start_button.set_center(frame_center_x, frame_center_y)
    
    if start_button.draw():
        return True
    
    return False

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

        # Draw score
        draw_text(str(score), font, white, int(screen_width / 2), 20)

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