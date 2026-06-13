import pygame
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600

window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Boricua Jump")

#set frame rate
clock = pygame.time.Clock()
FPS = 60

# game variables
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
IVORY = (255, 255, 240)
SCROLL_THRESH = 80
GRAVITY = 1
JUMP_STRENGTH = -18
MAX_PLATFORMS = 7

MIN_PLATFORM_GAP = 80
MAX_PLATFORM_GAP = 115
MAX_HORIZONTAL_GAP = 135
MIN_HORIZONTAL_GAP = 35

START_FIRST_MIN_GAP = 60
START_FIRST_MAX_GAP = 78
START_FIRST_MAX_HORIZONTAL_GAP = 90

BIRD_SPAWN_TIME = 220
PLANE_SPAWN_TIME = 300

WATER_START_Y = SCREEN_HEIGHT + 140
WATER_SPEED = 1.1
WATER_MAX_SPEED = 3.0
WATER_BLUE = (35, 115, 210)
WATER_LIGHT = (95, 185, 255)
WATER_DARK = (15, 75, 155)

PLATFORM_BREAK_TIME = 3 * FPS
PLATFORM_DISAPPEAR_TIME = 2 * FPS

scroll = 0
score = 0
bird_timer = 0
plane_timer = 0
water_y = WATER_START_Y
wave_offset = 0

# infinite background variables
sky_y1 = 0
sky_y2 = -SCREEN_HEIGHT

clouds_y1 = 0
clouds_y2 = -SCREEN_HEIGHT

clouds2_y1 = 0
clouds2_y2 = -SCREEN_HEIGHT

start_land_y = 0

# game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# font
font = pygame.font.Font("fonts/Slackey-Regular.ttf", 34)
small_font = pygame.font.Font("fonts/Slackey-Regular.ttf", 18)

# load images
walk_imgs = [
    pygame.image.load("assets/jibaro1.png").convert_alpha(),
    pygame.image.load("assets/jibaro2.png").convert_alpha(),
    pygame.image.load("assets/jibaro3.png").convert_alpha()
]

jump_imgs = [
    pygame.image.load("assets/jump1.png").convert_alpha(),
    pygame.image.load("assets/jump2.png").convert_alpha(),
    pygame.image.load("assets/jump3.png").convert_alpha(),
    pygame.image.load("assets/jump4.png").convert_alpha()
]

bird_imgs = [
    pygame.image.load("assets/bird1.png").convert_alpha(),
    pygame.image.load("assets/bird2.png").convert_alpha()
]

plane_imgs = [
    pygame.image.load("assets/plane_1_blue.png").convert_alpha(),
    pygame.image.load("assets/plane_1_red.png").convert_alpha(),
    pygame.image.load("assets/plane_1_pink.png").convert_alpha(),
    pygame.image.load("assets/plane_1_yellow.png").convert_alpha()
]

sky_img = pygame.image.load("assets/sky.png").convert_alpha()
sky_img = pygame.transform.scale(sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

start_land_img = pygame.image.load("assets/start_land.png").convert_alpha()
start_land_img = pygame.transform.scale(start_land_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

clouds_img = pygame.image.load("assets/clows.png").convert_alpha()
clouds_img = pygame.transform.scale(clouds_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

clouds2_img = pygame.image.load("assets/clows2.png").convert_alpha()
clouds2_img = pygame.transform.scale(clouds2_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

platform_images = {
    "grass": {
        "normal": pygame.image.load("assets/ground_grass.png").convert_alpha(),
        "broken": pygame.image.load("assets/ground_grass_broken.png").convert_alpha()
    },
    "sand": {
        "normal": pygame.image.load("assets/ground_sand.png").convert_alpha(),
        "broken": pygame.image.load("assets/ground_sand_broken.png").convert_alpha()
    },
    "stone": {
        "normal": pygame.image.load("assets/ground_stone.png").convert_alpha(),
        "broken": pygame.image.load("assets/ground_stone_broken.png").convert_alpha()
    },
    "wood": {
        "normal": pygame.image.load("assets/ground_wood.png").convert_alpha(),
        "broken": pygame.image.load("assets/ground_wood_broken.png").convert_alpha()
    }
}


def make_clouds_white(image, alpha):
    cloud_image = image.copy()

    # This makes the blue clouds look white while keeping transparency
    cloud_image.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # This controls how soft or visible the clouds are
    cloud_image.set_alpha(alpha)

    return cloud_image


clouds_img = make_clouds_white(clouds_img, 190)
clouds2_img = make_clouds_white(clouds2_img, 120)


def get_stage_info():
    if score < 800:
        return "grass", "Grass"
    elif score < 1600:
        return "sand", "Sand"
    elif score < 2600:
        return "stone", "Stone"
    else:
        return "wood", "Wood"


def should_platform_move():
    if score < 500:
        return False
    elif score < 1200:
        return random.random() < 0.15
    elif score < 2200:
        return random.random() < 0.25
    else:
        return random.random() < 0.35


def draw_repeating_layer(image, y1, y2):
    window.blit(image, (0, int(y1)))
    window.blit(image, (0, int(y2)))


def draw_background(scroll_amount):
    global sky_y1, sky_y2
    global clouds_y1, clouds_y2
    global clouds2_y1, clouds2_y2
    global start_land_y

    # sky moves very slowly so it feels calm
    sky_y1 += scroll_amount * 0.15
    sky_y2 += scroll_amount * 0.15

    if sky_y1 >= SCREEN_HEIGHT:
        sky_y1 = sky_y2 - SCREEN_HEIGHT

    if sky_y2 >= SCREEN_HEIGHT:
        sky_y2 = sky_y1 - SCREEN_HEIGHT

    draw_repeating_layer(sky_img, sky_y1, sky_y2)

    # far clouds move slower
    clouds2_y1 += scroll_amount * 0.25
    clouds2_y2 += scroll_amount * 0.25

    if clouds2_y1 >= SCREEN_HEIGHT:
        clouds2_y1 = clouds2_y2 - SCREEN_HEIGHT

    if clouds2_y2 >= SCREEN_HEIGHT:
        clouds2_y2 = clouds2_y1 - SCREEN_HEIGHT

    draw_repeating_layer(clouds2_img, clouds2_y1, clouds2_y2)

    # near clouds move a little faster
    clouds_y1 += scroll_amount * 0.45
    clouds_y2 += scroll_amount * 0.45

    if clouds_y1 >= SCREEN_HEIGHT:
        clouds_y1 = clouds_y2 - SCREEN_HEIGHT

    if clouds_y2 >= SCREEN_HEIGHT:
        clouds_y2 = clouds_y1 - SCREEN_HEIGHT

    draw_repeating_layer(clouds_img, clouds_y1, clouds_y2)

    # start land only appears at the beginning
    start_land_y += scroll_amount

    if start_land_y < SCREEN_HEIGHT:
        window.blit(start_land_img, (0, int(start_land_y)))


def generate_platform_position():
    highest_platform = min(platforms, key=lambda p: p.rect.y)

    platform_width = random.randint(70, 105)

    vertical_gap = random.randint(MIN_PLATFORM_GAP, MAX_PLATFORM_GAP)
    platform_y = highest_platform.rect.y - vertical_gap

    old_center = highest_platform.rect.centerx

    direction = random.choice([-1, 1])
    horizontal_gap = random.randint(MIN_HORIZONTAL_GAP, MAX_HORIZONTAL_GAP)
    new_center = old_center + (horizontal_gap * direction)

    if new_center < platform_width // 2:
        new_center = old_center + horizontal_gap

    if new_center > SCREEN_WIDTH - platform_width // 2:
        new_center = old_center - horizontal_gap

    platform_x = new_center - platform_width // 2

    if platform_x < 0:
        platform_x = 0

    if platform_x > SCREEN_WIDTH - platform_width:
        platform_x = SCREEN_WIDTH - platform_width

    return platform_x, platform_y, platform_width


# player class
class Player:
    def __init__(self, x, y):
        self.walk_imgs = [pygame.transform.scale(img, (45, 45)) for img in walk_imgs]
        self.jump_imgs = [pygame.transform.scale(img, (45, 45)) for img in jump_imgs]
        self.image = self.walk_imgs[0]

        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

        self.animation_index = 0
        self.animation_counter = 0
        self.moving = False
        self.on_ground = False
        self.current_platform = None

    def move(self):

        #reset variables for movement
        dx, dy = 0, 0
        scroll = 0
        self.moving = False
        was_on_ground = self.on_ground
        self.on_ground = False
        self.current_platform = None

        # process keyboard input for movement
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx -= 5
            self.flip = True
            self.moving = True
        if key[pygame.K_RIGHT]:
            dx += 5
            self.flip = False
            self.moving = True
        if key[pygame.K_UP] and was_on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 15:
            self.vel_y = 15

        dy += self.vel_y

        # ensure player doesn't go off the edges of the screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # Check collision with platforms
        for platform in platforms:
            if not platform.disappearing:
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if the player is falling and above the platform
                    if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 10:
                        dy = platform.rect.top - self.rect.bottom
                        self.vel_y = 0
                        self.on_ground = True
                        self.current_platform = platform

        #
        if self.rect.top + dy <= SCROLL_THRESH and self.vel_y < 0:
            scroll = -dy
            dy = 0

        #update player position
        self.rect.x += dx
        self.rect.y += dy

        self.update_animation()

        return scroll

    def stick_to_platform(self):
        if self.current_platform is not None:
            if self.current_platform.alive():
                self.rect.x += self.current_platform.move_dx

                if self.rect.left < 0:
                    self.rect.left = 0

                if self.rect.right > SCREEN_WIDTH:
                    self.rect.right = SCREEN_WIDTH

    def update_animation(self):
        if not self.on_ground:
            if self.vel_y < -12:
                self.image = self.jump_imgs[0]
            elif self.vel_y < -5:
                self.image = self.jump_imgs[1]
            elif self.vel_y < 0:
                self.image = self.jump_imgs[2]
            else:
                self.image = self.jump_imgs[3]
        elif self.moving:
            self.animation_counter += 1

            if self.animation_counter >= 8:
                self.animation_counter = 0
                self.animation_index += 1

                if self.animation_index >= len(self.walk_imgs):
                    self.animation_index = 0

            self.image = self.walk_imgs[self.animation_index]
        else:
            self.image = self.walk_imgs[0]

    def draw(self, surface):
        surface.blit(
            pygame.transform.flip(self.image, self.flip, False),
            (self.rect.x - 10, self.rect.y - 8)
        ) # Adjust position to center the image on the hitbox
        #pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Draw hitbox for debugging


# platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, platform_type=None, moving=False):
        pygame.sprite.Sprite.__init__(self)

        if platform_type is None:
            platform_type, stage_name = get_stage_info()

        self.platform_type = platform_type
        self.moving = moving

        self.normal_image = pygame.transform.scale(
            platform_images[self.platform_type]["normal"],
            (width, 12)
        )

        self.broken_image = pygame.transform.scale(
            platform_images[self.platform_type]["broken"],
            (width, 12)
        )

        self.image = self.normal_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.float_x = float(x)
        self.move_dx = 0

        self.move_speed = random.choice([-1, 1]) * random.uniform(1.0, 1.7)
        self.move_range = random.randint(45, 85)
        self.start_x = x

        self.touch_timer = 0
        self.broken_timer = 0
        self.is_broken = False
        self.disappearing = False

    def update(self, scroll, current_platform):
        self.rect.y += scroll

        self.move_dx = 0

        if self.moving:
            old_x = self.rect.x

            self.float_x += self.move_speed

            if self.float_x < self.start_x - self.move_range:
                self.float_x = self.start_x - self.move_range
                self.move_speed *= -1

            if self.float_x > self.start_x + self.move_range:
                self.float_x = self.start_x + self.move_range
                self.move_speed *= -1

            self.rect.x = int(self.float_x)

            if self.rect.left < 0:
                self.rect.left = 0
                self.float_x = float(self.rect.x)
                self.move_speed *= -1

            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.float_x = float(self.rect.x)
                self.move_speed *= -1

            self.move_dx = self.rect.x - old_x

        if current_platform == self:
            self.touch_timer += 1

            if self.touch_timer >= PLATFORM_BREAK_TIME:
                self.is_broken = True
                self.image = self.broken_image
                self.broken_timer += 1

                if self.broken_timer >= PLATFORM_DISAPPEAR_TIME:
                    self.disappearing = True
                    self.kill()
        else:
            if not self.is_broken:
                self.touch_timer = 0

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [pygame.transform.scale(img, (55, 35)) for img in bird_imgs]
        self.animation_index = 0
        self.animation_counter = 0

        self.direction = random.choice([-1, 1])
        self.speed = random.randint(2, 4)

        self.image = self.images[0]
        self.rect = self.image.get_rect()

        self.rect.y = random.randint(90, 160)

        if self.direction == 1:
            self.rect.x = -70
        else:
            self.rect.x = SCREEN_WIDTH + 70

        self.shoot_timer = random.randint(45, 90)
        self.has_shot = False

        self.defeated = False
        self.fall_speed = 0

    def update(self, scroll):
        self.rect.y += scroll

        if self.defeated:
            self.fall_speed += 1
            self.rect.y += self.fall_speed

            self.image = pygame.transform.flip(self.images[self.animation_index], False, True)

            if self.rect.top > SCREEN_HEIGHT:
                self.kill()

            return

        self.rect.x += self.speed * self.direction

        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_counter = 0
            self.animation_index += 1

            if self.animation_index >= len(self.images):
                self.animation_index = 0

        self.image = self.images[self.animation_index]

        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and not self.has_shot:
            ball = BirdBall(self.rect.centerx, self.rect.bottom)
            bird_balls.add(ball)
            self.has_shot = True

        if self.rect.right < -80 or self.rect.left > SCREEN_WIDTH + 80 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


# bird ball class
class BirdBall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.radius = 6
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, IVORY, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.speed_y = 5

    def update(self, scroll):
        self.rect.y += self.speed_y + scroll

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# plane class
class Plane(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # choose one random plane color
        original_image = random.choice(plane_imgs)
        self.image = pygame.transform.scale(original_image, (70, 38))

        self.direction = random.choice([-1, 1])
        self.speed = random.randint(3, 5)

        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.y = random.randint(85, 210)

        if self.direction == 1:
            self.rect.x = -90
        else:
            self.rect.x = SCREEN_WIDTH + 90

    def update(self, scroll):
        self.rect.y += scroll
        self.rect.x += self.speed * self.direction

        if self.rect.right < -100 or self.rect.left > SCREEN_WIDTH + 100 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


def update_water(scroll):
    global water_y, wave_offset

    water_y += scroll

    # water gets faster as the score goes up
    current_water_speed = WATER_SPEED + (score * 0.0003)

    if current_water_speed > WATER_MAX_SPEED:
        current_water_speed = WATER_MAX_SPEED

    water_y -= current_water_speed

    wave_offset += 2
    if wave_offset >= 40:
        wave_offset = 0


def draw_water():
    water_top = int(water_y)

    if water_top < SCREEN_HEIGHT:
        if water_top < 0:
            water_top = 0

        water_height = SCREEN_HEIGHT - water_top

        # main water body - now it always reaches the bottom of the screen
        pygame.draw.rect(window, WATER_BLUE, (0, water_top, SCREEN_WIDTH, water_height))

        # darker bottom part to give the water more depth
        pygame.draw.rect(window, WATER_DARK, (0, water_top + 45, SCREEN_WIDTH, max(0, water_height - 45)))

        # animated top waves
        for x in range(-40, SCREEN_WIDTH + 40, 40):
            pygame.draw.arc(
                window,
                WATER_LIGHT,
                (x + wave_offset, water_top - 8, 40, 24),
                0,
                3.14,
                3
            )

        # bright line at the surface
        pygame.draw.line(window, WATER_LIGHT, (0, water_top), (SCREEN_WIDTH, water_top), 3)


def create_starting_platforms():
    starting_x = SCREEN_WIDTH // 2 - 55
    starting_y = SCREEN_HEIGHT - 50
    starting_width = 110

    starting_platform = Platform(
        starting_x,
        starting_y,
        starting_width,
        "grass",
        False
    )
    platforms.add(starting_platform)

    last_x = starting_x
    last_y = starting_y
    last_width = starting_width

    for p in range(MAX_PLATFORMS - 1):
        platform_width = random.randint(70, 105)

        if p == 0:
            vertical_gap = random.randint(START_FIRST_MIN_GAP, START_FIRST_MAX_GAP)
            horizontal_gap = random.randint(MIN_HORIZONTAL_GAP, START_FIRST_MAX_HORIZONTAL_GAP)
        else:
            vertical_gap = random.randint(MIN_PLATFORM_GAP, MAX_PLATFORM_GAP)
            horizontal_gap = random.randint(MIN_HORIZONTAL_GAP, MAX_HORIZONTAL_GAP)

        platform_y = last_y - vertical_gap

        old_center = last_x + last_width // 2
        direction = random.choice([-1, 1])
        new_center = old_center + (horizontal_gap * direction)

        if new_center < platform_width // 2:
            new_center = old_center + horizontal_gap

        if new_center > SCREEN_WIDTH - platform_width // 2:
            new_center = old_center - horizontal_gap

        platform_x = new_center - platform_width // 2

        if platform_x < 0:
            platform_x = 0

        if platform_x > SCREEN_WIDTH - platform_width:
            platform_x = SCREEN_WIDTH - platform_width

        platform = Platform(
            platform_x,
            platform_y,
            platform_width,
            "grass",
            False
        )
        platforms.add(platform)

        last_x = platform_x
        last_y = platform_y
        last_width = platform_width


def reset_game():
    global jumpy_player, platforms, bird_group, bird_balls, plane_group
    global score, bird_timer, plane_timer, scroll
    global water_y, wave_offset
    global sky_y1, sky_y2
    global clouds_y1, clouds_y2
    global clouds2_y1, clouds2_y2
    global start_land_y

    score = 0
    bird_timer = 0
    plane_timer = 0
    scroll = 0
    water_y = WATER_START_Y
    wave_offset = 0

    sky_y1 = 0
    sky_y2 = -SCREEN_HEIGHT

    clouds_y1 = 0
    clouds_y2 = -SCREEN_HEIGHT

    clouds2_y1 = 0
    clouds2_y2 = -SCREEN_HEIGHT

    start_land_y = 0

    # create player instance
    jumpy_player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

    platforms = pygame.sprite.Group()
    bird_group = pygame.sprite.Group()
    bird_balls = pygame.sprite.Group()
    plane_group = pygame.sprite.Group()

    create_starting_platforms()


def draw_text(text, font, text_color, outline_color, x, y):
    img_outline = font.render(text, True, outline_color)
    img = font.render(text, True, text_color)

    window.blit(img_outline, (x - 2, y))
    window.blit(img_outline, (x + 2, y))
    window.blit(img_outline, (x, y - 2))
    window.blit(img_outline, (x, y + 2))

    window.blit(img, (x, y))


def draw_center_text(text, font, text_color, outline_color, y):
    img = font.render(text, True, text_color)
    x = SCREEN_WIDTH // 2 - img.get_width() // 2
    draw_text(text, font, text_color, outline_color, x, y)


# create player instance
jumpy_player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

platforms = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
bird_balls = pygame.sprite.Group()
plane_group = pygame.sprite.Group()

create_starting_platforms()


# main game loop
running = True

while running:

    clock.tick(FPS)  # Maintain 60 FPS

    # MENU
    if game_state == MENU:
        draw_background(0)

        draw_center_text("Boricua Jump", font, WHITE, BLACK, 190)
        draw_center_text("Press SPACE", small_font, WHITE, BLACK, 270)
        draw_center_text("to start", small_font, WHITE, BLACK, 300)
        draw_center_text("Use the arrows", small_font, WHITE, BLACK, 350)

    # JUEGO
    elif game_state == PLAYING:

        scroll = jumpy_player.move()
        score += scroll
        update_water(scroll)

        draw_background(scroll)

        # create new platforms
        while len(platforms) < MAX_PLATFORMS:
            platform_x, platform_y, platform_width = generate_platform_position()
            platform_type, stage_name = get_stage_info()

            platform = Platform(
                platform_x,
                platform_y,
                platform_width,
                platform_type,
                should_platform_move()
            )

            platforms.add(platform)

        # create bird obstacle
        bird_timer += 1
        if bird_timer >= BIRD_SPAWN_TIME:
            if len(bird_group) == 0:
                bird = Bird()
                bird_group.add(bird)

            bird_timer = random.randint(-120, 0)

        # create plane obstacle
        plane_timer += 1
        if plane_timer >= PLANE_SPAWN_TIME:
            if len(plane_group) == 0:
                plane = Plane()
                plane_group.add(plane)

            plane_timer = random.randint(-180, 0)

        platforms.update(scroll, jumpy_player.current_platform)
        jumpy_player.stick_to_platform()

        bird_group.update(scroll)
        bird_balls.update(scroll)
        plane_group.update(scroll)

        platforms.draw(window)
        bird_group.draw(window)
        bird_balls.draw(window)
        plane_group.draw(window)
        draw_water()
        jumpy_player.draw(window)

        pygame.draw.line(window, WHITE, (0, SCROLL_THRESH), (SCREEN_WIDTH, SCROLL_THRESH), 2)

        score_box = pygame.Surface((190, 60))
        score_box.set_alpha(150)
        score_box.fill(BLACK)
        window.blit(score_box, (5, SCROLL_THRESH - 68))

        platform_type, stage_name = get_stage_info()

        draw_text("Score: " + str(score), small_font, WHITE, BLACK, 10, SCROLL_THRESH - 60)
        draw_text("Stage: " + stage_name, small_font, WHITE, BLACK, 10, SCROLL_THRESH - 35)

        # check collision with bird
        for bird in bird_group:
            if jumpy_player.rect.colliderect(bird.rect):

                # if player lands on top of the bird
                if jumpy_player.vel_y > 0 and jumpy_player.rect.bottom <= bird.rect.top + 15 and not bird.defeated:
                    bird.defeated = True
                    bird.fall_speed = 2
                    jumpy_player.vel_y = -13  # little boost

                # if player touches the bird from the side or bottom
                elif not bird.defeated:
                    game_state = GAME_OVER

        # game over when player touches ball
        if pygame.sprite.spritecollide(jumpy_player, bird_balls, False):
            game_state = GAME_OVER

        # game over when player touches plane
        if pygame.sprite.spritecollide(jumpy_player, plane_group, False):
            game_state = GAME_OVER

        # game over when player touches water
        if jumpy_player.rect.bottom >= water_y:
            game_state = GAME_OVER

        # game over when player falls
        if jumpy_player.rect.top > SCREEN_HEIGHT:
            game_state = GAME_OVER

    # GAME OVER
    elif game_state == GAME_OVER:
        draw_background(0)

        draw_center_text("GAME OVER", font, WHITE, BLACK, 180)
        draw_center_text("Final Score: " + str(score), small_font, WHITE, BLACK, 245)
        draw_center_text("Press SPACE", small_font, WHITE, BLACK, 300)
        draw_center_text("to restart", small_font, WHITE, BLACK, 330)
        draw_center_text("Press ESC to exit", small_font, WHITE, BLACK, 380)

    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if game_state == MENU:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = PLAYING

            elif game_state == GAME_OVER:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    game_state = PLAYING

                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.display.update()

pygame.quit()