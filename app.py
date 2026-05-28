import pygame
import sys
import random

pygame.init()

# ==========================================
# WINDOW
# ==========================================

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Platformer")

clock = pygame.time.Clock()

# ==========================================
# LOAD ASSETS
# ==========================================

# Background
bg = pygame.image.load(
    "assets/backgrounds/bg.png"
).convert()

bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

# Tilesheet
tilesheet = pygame.image.load(
    "assets/tiles/tilesheet.png"
).convert_alpha()

# Player
player_idle = pygame.image.load(
    "assets/player/idle.png"
).convert_alpha()

player_run1 = pygame.image.load(
    "assets/player/run1.png"
).convert_alpha()

player_run2 = pygame.image.load(
    "assets/player/run2.png"
).convert_alpha()

# Resize player
player_idle = pygame.transform.scale(player_idle, (80, 80))
player_run1 = pygame.transform.scale(player_run1, (80, 80))
player_run2 = pygame.transform.scale(player_run2, (80, 80))

player_frames = [
    player_idle,
    player_run1,
    player_run2
]

# Enemy
enemy_img = pygame.image.load(
    "assets/enemies/slime.png"
).convert_alpha()

enemy_img = pygame.transform.scale(enemy_img, (70, 70))

# ==========================================
# TILE SYSTEM
# ==========================================

TILE_SIZE = 64

def get_tile(x, y):

    tile = tilesheet.subsurface(
        (
            x * TILE_SIZE,
            y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )
    )

    return tile

ground_tile = get_tile(0, 8)
platform_tile = get_tile(1, 8)

# ==========================================
# PLAYER
# ==========================================

player = pygame.Rect(100, 100, 50, 70)

player_x_vel = 0
player_y_vel = 0

speed = 7
gravity = 0.5
jump_power = -13

on_ground = False

health = 5

# Animation
animation_index = 0
animation_timer = 0

# ==========================================
# CAMERA
# ==========================================

camera_x = 0

# ==========================================
# WORLD
# ==========================================

WORLD_WIDTH = 8000
difficulty = 1

platforms = []
enemies = []

# ==========================================
# PROCEDURAL GENERATION
# ==========================================

def generate_level():

    global platforms
    global enemies

    platforms = []
    enemies = []

    # ======================================
    # GROUND WITH RANDOM GAPS
    # ======================================

    x = 0

    while x < WORLD_WIDTH:

        # Random gap
        if random.randint(0, 100) < 15:

            x += TILE_SIZE * random.randint(2, 5)
            continue

        rect = pygame.Rect(
            x,
            HEIGHT - 64,
            TILE_SIZE,
            TILE_SIZE
        )

        platforms.append((rect, ground_tile))

        x += TILE_SIZE

    # ======================================
    # RANDOM FLOATING PLATFORMS
    # ======================================

    for i in range(80 + difficulty * 20):

        x = i * 120 + 300

        y = random.randint(200, 550)

        rect = pygame.Rect(
            x,
            y,
            TILE_SIZE,
            TILE_SIZE
        )

        platforms.append((rect, platform_tile))

        # Random enemies
        if random.randint(0, 100) < 35:

            enemy = pygame.Rect(
                x,
                y - 60,
                50,
                50
            )

            enemies.append(enemy)

generate_level()

# ==========================================
# FONT
# ==========================================

font = pygame.font.SysFont("Arial", 32)

# ==========================================
# GAME LOOP
# ==========================================

while True:

    dt = clock.tick(60)

    # ==========================================
    # EVENTS
    # ==========================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # ==========================================
    # INPUT
    # ==========================================

    keys = pygame.key.get_pressed()

    player_x_vel = 0
    moving = False

    if keys[pygame.K_a]:

        player_x_vel = -speed
        moving = True

    if keys[pygame.K_d]:

        player_x_vel = speed
        moving = True

    if keys[pygame.K_SPACE] and on_ground:

        player_y_vel = jump_power
        on_ground = False

    # ==========================================
    # GRAVITY
    # ==========================================

    player_y_vel += gravity

    # ==========================================
    # PLAYER MOVEMENT
    # ==========================================

    player.x += player_x_vel
    player.y += player_y_vel

    # ==========================================
    # COLLISION
    # ==========================================

    on_ground = False

    for platform, image in platforms:

        if player.colliderect(platform):

            # Falling
            if player_y_vel > 0:

                player.bottom = platform.top
                player_y_vel = 0

                on_ground = True

            # Hitting underside
            elif player_y_vel < 0:

                player.top = platform.bottom
                player_y_vel = 0

    # ==========================================
    # DEATH
    # ==========================================

    if player.y > HEIGHT + 300:

        health -= 1

        player.x = 100
        player.y = 100

        player_y_vel = 0

    # ==========================================
    # CAMERA
    # ==========================================

    camera_x = player.x - 300

    # ==========================================
    # ENEMY MOVEMENT
    # ==========================================

    for enemy in enemies:

        enemy.x += random.choice([-1, 1])

    # ==========================================
    # ENEMY COLLISION
    # ==========================================

    for enemy in enemies[:]:

        if player.colliderect(enemy):

            # Stomp enemy
            if player_y_vel > 0 and player.bottom < enemy.centery:

                enemies.remove(enemy)

                player_y_vel = -8

            else:

                health -= 1

                player.x = 100
                player.y = 100

    # ==========================================
    # ANIMATION
    # ==========================================

    if moving:

        animation_timer += 1

        if animation_timer >= 10:

            animation_timer = 0

            animation_index += 1

            if animation_index >= len(player_frames):
                animation_index = 0

        player_image = player_frames[animation_index]

    else:

        player_image = player_idle

    # ==========================================
    # GENERATE NEW WORLD
    # ==========================================

    if player.x > WORLD_WIDTH - 500:

        difficulty += 1

        generate_level()

        player.x = 100
        player.y = 100

        camera_x = 0

    # ==========================================
    # DRAWING
    # ==========================================

    screen.blit(bg, (0, 0))

    # Platforms
    for platform, image in platforms:

        screen.blit(
            image,
            (
                platform.x - camera_x,
                platform.y
            )
        )

    # Enemies
    for enemy in enemies:

        screen.blit(
            enemy_img,
            (
                enemy.x - camera_x,
                enemy.y
            )
        )

    # Player
    screen.blit(
        player_image,
        (
            player.x - camera_x,
            player.y
        )
    )

    # ==========================================
    # UI
    # ==========================================

    health_text = font.render(
        f"Health: {health}",
        True,
        (255, 255, 255)
    )

    difficulty_text = font.render(
        f"Difficulty: {difficulty}",
        True,
        (255, 120, 120)
    )

    screen.blit(health_text, (20, 20))
    screen.blit(difficulty_text, (20, 60))

    # ==========================================
    # GAME OVER
    # ==========================================

    if health <= 0:

        game_over = font.render(
            "GAME OVER",
            True,
            (255, 0, 0)
        )

        screen.blit(game_over, (500, 300))

    pygame.display.update()
