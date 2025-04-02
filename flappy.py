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
font = pygame.font.Font("Jersey10-Regular.ttf", 60)
small_font = pygame.font.Font("Jersey10-Regular.ttf", 40)
smaller_font = pygame.font.Font("Jersey10-Regular.ttf", 30)
white = (255, 255, 255)
orange = (255, 102, 0)
themes = [
    {"name": "Default", "bg": "img/bg.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (135, 206, 235)},
    {"name": "Dark", "bg": "img/darkmode.png", "ground": "img/ground.png", "pipe": "img/pipe.png", "sky": (25, 25, 112)}
]
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

showing_bird_selection = False
showing_theme_selection = False
difficulty_increase_interval = 5  # Increase difficulty every 5 points
max_scroll_speed = 7
min_pipe_gap = 120

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
        bg = pygame.image.load(themes[current_theme]["bg"])
    except (pygame.error, FileNotFoundError):
        bg = pygame.Surface((screen_width, screen_height))
        bg.fill(themes[current_theme]["sky"])  # Use the sky color from the theme
    

    try:
        ground_img = pygame.image.load(themes[current_theme]["ground"])
    except (pygame.error, FileNotFoundError):
        ground_img = pygame.Surface((screen_width, 168))
        ground_img.fill((139, 69, 19))  # Brown
    try:
        pipe_img = pygame.image.load(themes[current_theme]["pipe"])
    except (pygame.error, FileNotFoundError):
        pipe_img = pygame.Surface((80, 500))
        pipe_img.fill((0, 128, 0))  # Green
    
    return bg, ground_img, pipe_img
bg, ground_img, pipe_img = load_theme_images()

try:
    button_img = pygame.image.load('img/restart.png')
except pygame.error:
    button_img = pygame.Surface((100, 50))
    button_img.fill((230, 97, 29))  # Orange
    pygame.draw.rect(button_img, white, (0, 0, 100, 50), 3)
    font_btn = pygame.font.SysFont(None, 30)
    restart_text = font_btn.render('RESTART', True, white)
    button_img.blit(restart_text, ((100 - restart_text.get_width())//2, (50 - restart_text.get_height())//2))
try:
    mainmenu_img = pygame.image.load('img/mainmenu.png')
except pygame.error:
    mainmenu_img = pygame.Surface((120, 50))  # Slightly wider than restart button
    mainmenu_img.fill((0, 102, 204))  # Blue color to differentiate from restart
    pygame.draw.rect(mainmenu_img, white, (0, 0, mainmenu_img.get_width(), mainmenu_img.get_height()), 3)
    font_menu = pygame.font.SysFont(None, 28)
    menu_text = font_menu.render('MAIN MENU', True, white)
    text_rect = menu_text.get_rect(center=(mainmenu_img.get_width()//2, mainmenu_img.get_height()//2))
    mainmenu_img.blit(menu_text, text_rect)
    
back_img = pygame.Surface((80, 40))
back_img.fill((100, 100, 100))  # Gray color
pygame.draw.rect(back_img, white, (0, 0, 80, 40), 3)
font_back = pygame.font.SysFont(None, 28)
back_text = font_back.render('BACK', True, white)
text_rect = back_text.get_rect(center=(40, 20))
back_img.blit(back_text, text_rect)

try:
    start_img = pygame.image.load('img/start.png')
    start_img = pygame.transform.scale(start_img, (int(start_img.get_width() * 0.7), int(start_img.get_height() * 0.5)))
except pygame.error:
    start_img = pygame.Surface((100, 50))
    start_img.fill((0, 128, 0))  # Green
    pygame.draw.rect(start_img, white, (0, 0, 100, 50), 3)
    font_start = pygame.font.SysFont(None, 30)
    start_text = font_start.render('START', True, white)
    start_img.blit(start_text, ((100 - start_text.get_width())//2, (50 - start_text.get_height())//2))

try:
    trophy_img = pygame.image.load('img/trophy.png')
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

def reset_game():
    global score, flying, game_over, scroll_speed, pipe_gap
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    flying = False
    game_over = False
    score = 0
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
    difficulty_level = score // difficulty_increase_interval
    new_scroll_speed = min(4 + (difficulty_level * 0.5), max_scroll_speed)
    scroll_speed = new_scroll_speed
    new_pipe_gap = max(180 - (difficulty_level * 10), min_pipe_gap)
    pipe_gap = int(new_pipe_gap)

def change_bird_type(new_type=None):
    global current_bird_type
    if new_type is not None:
        current_bird_type = new_type
    else:
        current_bird_type = (current_bird_type + 1) % len(bird_types)
    flappy.load_images(bird_types[current_bird_type])

def change_theme(new_theme=None):
    global current_theme, bg, ground_img, pipe_img
    if new_theme is not None:
        current_theme = new_theme
    else:
        current_theme = (current_theme + 1) % len(themes)
        bg, ground_img, pipe_img = load_theme_images()
    for pipe in pipe_group:
        pipe.update_image(pipe_img)

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
            for num in range(1, 4):
                try:
                    img = pygame.image.load(f"img/bird{num}.png")
                    self.images.append(img)
                except pygame.error:
                    bird_img = pygame.Surface((34, 24))
                    bird_img.fill((255, 255, 0))  # Yellow
                    pygame.draw.ellipse(bird_img, (255, 255, 0), (0, 0, 34, 24))
                    pygame.draw.circle(bird_img, (0, 0, 0), (28, 10), 3)  # Eye
                    self.images.append(bird_img)
            
        elif bird_type == "rocket":
            try:
                rocket_img = pygame.image.load("img/rocket.png")
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
def draw_game_over():
    global high_score, score, game_over
    
    if score > high_score:
        high_score = score
        save_high_score(high_score)  # Save high score when it's beaten

    frame_color = orange if current_theme == 0 else (50, 50, 100)
    
    frame_rect = pygame.Rect(232, 268, 400, 300)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)

    screen.blit(trophy_img, (270, 300))  
    draw_text(f": {high_score}", font, white, 320, 290)
    draw_text(f"SCORE: {score}", font, white, 260, 350)
    bird_img = flappy.images[0]
    bird_box = pygame.Rect(520, 290, bird_img.get_width() + 10, bird_img.get_height() + 10)
    pygame.draw.rect(screen, white, bird_box)

    screen.blit(bird_img, (520, 290))

    restart_button = Button(320, 450, button_img)

    mainmenu_button = Button(420, 450, mainmenu_img)

    if restart_button.draw():
        game_over = False
        reset_game()
    
    if mainmenu_button.draw():
        go_to_main_menu()

def draw_main_menu():
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
        global showing_bird_selection
        showing_bird_selection = True
    
    if theme_clicked:
        global showing_theme_selection
        showing_theme_selection = True
    
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
    bird_buttons = []
    bird_displays = []
    for i, bird_type in enumerate(bird_types):
        temp_bird = Bird(0, 0)
        temp_bird.load_images(bird_type)
        button_width = 250
        button_height = 150
        button_img = pygame.Surface((button_width, button_height))
        button_color = (50, 150, 200) if i == current_bird_type else (80, 80, 80)
        button_img.fill(button_color)
        pygame.draw.rect(button_img, white, (0, 0, button_width, button_height), 3)
        btn_font = pygame.font.SysFont(None, 30)
        btn_text = btn_font.render(bird_type.upper(), True, white)
        text_rect = btn_text.get_rect(center=(button_width//2, 30))
        button_img.blit(btn_text, text_rect)
        button = Button(0, 0, button_img)
        col = i % 2
        row = i // 2
        x_center = frame_rect.x + (frame_rect.width // 4) + (col * (frame_rect.width // 2))
        y_center = frame_rect.y + 300 + (row * 160)
        button.set_center(x_center, y_center)
        bird_buttons.append(button)
        bird_displays.append(temp_bird)
    for i, button in enumerate(bird_buttons):
        bird_img = bird_displays[i].images[0]
        img_x = button.rect.centerx - bird_img.get_width() // 2
        img_y = button.rect.y + 60
        bird_box = pygame.Rect(img_x - 5, img_y - 5, bird_img.get_width() + 10, bird_img.get_height() + 10)
        pygame.draw.rect(screen, white, bird_box)
        screen.blit(bird_img, (img_x, img_y))
        if button.draw():
            change_bird_type(i)
            showing_bird_selection = False
    if back_button.draw():
        showing_bird_selection = False
def draw_theme_selection():
    global showing_theme_selection
    screen.blit(bg, (0, 0))
    screen.blit(ground_img, (ground_scroll, 768))
    frame_color = orange if current_theme == 0 else (50, 50, 100)
    frame_rect = pygame.Rect(132, 200, 600, 450)
    pygame.draw.rect(screen, frame_color, frame_rect)
    pygame.draw.rect(screen, white, frame_rect, 10)
    draw_text("SELECT THEME", font, white, 250, 220)
    back_button = Button(20, 20, back_img)
    theme_buttons = []
    original_theme = current_theme
    for i, theme in enumerate(themes):
        button_width = 250
        button_height = 150
        button_img = pygame.Surface((button_width, button_height))
        button_color = (150, 100, 200) if i == current_theme else (80, 80, 80)
        button_img.fill(button_color)
        pygame.draw.rect(button_img, white, (0, 0, button_width, button_height), 3)
        btn_font = pygame.font.SysFont(None, 30)
        btn_text = btn_font.render(theme["name"].upper(), True, white)
        text_rect = btn_text.get_rect(center=(button_width//2, 30))
        button_img.blit(btn_text, text_rect)
        try:
            preview_img = pygame.image.load(theme["bg"])
            preview_img = pygame.transform.scale(preview_img, (button_width - 20, 80))
        except (pygame.error, FileNotFoundError):
            preview_img = pygame.Surface((button_width - 20, 80))
            preview_img.fill(theme["sky"])
        button_img.blit(preview_img, (10, 60))
        button = Button(0, 0, button_img)
        col = i % 2
        row = i // 2
        x_center = frame_rect.x + (frame_rect.width // 4) + (col * (frame_rect.width // 2))
        y_center = frame_rect.y + 300 + (row * 160)
        button.set_center(x_center, y_center)
        theme_buttons.append(button)
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
bird_group.add(flappy)
run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    if showing_bird_selection:
        draw_bird_selection()
    elif showing_theme_selection:
        draw_theme_selection()
    elif game_started:
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
        screen.blit(ground_img, (ground_scroll, 768))
        if game_over:
            draw_game_over()
        else:
            if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
                game_over = True
            if flappy.rect.bottom >= 768:
                game_over = True
                flying = False
            
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
            pipe_group.update()
            if not game_over and flying:
                time_now = pygame.time.get_ticks()
                if time_now - last_pipe > pipe_frequency:
                    pipe_height = random.randint(-100, 100)
                    btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                    top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                    pipe_group.add(btm_pipe)
                    pipe_group.add(top_pipe)
                    last_pipe = time_now
            if not game_over:
                ground_scroll -= scroll_speed
                if abs(ground_scroll) > 35:
                    ground_scroll = 0
    else:
        if draw_main_menu():
            game_started = True
            flying = True
            reset_game()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over and game_started:
            flying = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if showing_bird_selection or showing_theme_selection:
                    showing_bird_selection = False
                    showing_theme_selection = False
                elif game_started:
                    go_to_main_menu()
                else:
                    run = False
            
    pygame.display.update()

pygame.quit()