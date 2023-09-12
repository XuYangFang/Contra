import pygame
import os
import random
import csv
import button

# initialize pygame
pygame.init()

# set the screen dimensions and initialize the display
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Contra')

# set the framerate and game variables
clock = pygame.time.Clock()
FPS = 60
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 3
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load images and store them in lists
start = pygame.image.load('D:/pic/img/start_btn.png').convert_alpha()
exit = pygame.image.load('D:/pic/img/exit_btn.png').convert_alpha()
restart = pygame.image.load('D:/pic/img/restart_btn.png').convert_alpha()
pine1_img = pygame.image.load('D:/pic/img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('D:/pic/img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('D:/pic/img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('D:/pic/img/Background/sky_cloud.png').convert_alpha()
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'D:/pic/img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
bullet = pygame.image.load('D:/pic/img/icons/bullet.png').convert_alpha()
bomb = pygame.image.load('D:/pic/img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('D:/pic/img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('D:/pic/img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('D:/pic/img/icons/grenade_box.png').convert_alpha()
supply = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colors
BG = (100, 100, 100)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# Define font
font = pygame.font.SysFont('Helvetica', 20)

def draw_text(text, font, color, x, y):
    """Draws text to the screen"""
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def draw_background():
    """Draws the background images"""
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    """Resets the level"""
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    water_group.empty()
    exit_group.empty()

    # Create an empty tile list
    data = [[-1] * COLS for row in range(ROWS)]

    return data

# Define a class for the game's soldier
class Figure(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()

        # Set initial attributes for the soldier
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # Define variables specific to the AI
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # Load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Reset the temporary list of images
            temp_list = []
            # Count the number of files in the folder
            num_of_frames = len(os.listdir(f'D:/pic/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                # Load and scale the image
                img = pygame.image.load(f'D:/pic/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Set the image and rect attributes for the soldier
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()

        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        # Reset movement variables
        screen_scroll = 0
        dx, dy = 0, 0

        # Assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y

        dy += self.vel_y

        # Check for collision with obstacles
        for tile in world.obstacle_list:
            # Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # Turn around if AI hits a wall
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0

            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below the ground (i.e. jumping)
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground (i.e. falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # Check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll <
                (world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction)
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            # check if the AI is near the player
            if self.vision.colliderect(player.rect):
                # stop running
                self.update_action(0)
                # shoot
                self.shoot()
            else:
                if not self.idling:
                    ai_moving_right = self.direction == 1
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1
                    # update AI vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out, reset it back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different from the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # Set the length of the level
        self.level_length = len(data[0])

        # Iterate through each tile in the level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    # Create an image for the tile and set its position
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)

                    # Add the tile to the obstacle list if it's an obstacle
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)

                    # Create a water object if the tile is water
                    elif 9 <= tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)

                    # Create a player object if the tile is a player
                    elif tile == 15:
                        player = Figure('player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    # Create an enemy object if the tile is an enemy
                    elif tile == 16:
                        enemy = Figure('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0)
                        enemy_group.add(enemy)

                    # Create an item box object if the tile is an item box
                    elif tile == 17:
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile == 18:
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

                    elif tile == 19:
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)

                    # Create an exit object if the tile is an exit
                    elif tile == 20:
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        # Return the player and the health bar
        return player, health_bar

    def draw(self):
        # Draw each tile in the obstacle list
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = supply[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3

            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()



class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100  # Grenade timer, in frames
        self.vel_y = -11  # Initial vertical velocity
        self.speed = 7    # Horizontal speed
        self.image = bomb
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction  # 1 for right, -1 for left

    def update(self):
        # Apply gravity
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check for collisions with the level
        for tile in world.obstacle_list:
            # Check collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                # Reverse direction on wall hit
                self.direction *= -1
                dx = self.direction * self.speed
            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Check if below the ground, i.e. thrown up
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # Update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Countdown timer
        self.timer -= 1
        if self.timer <= 0:
            # Remove grenade and spawn explosion
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            # Apply damage to nearby entities
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
                        abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'D:/pic/img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        # Move with screen scroll
        self.rect.x += screen_scroll

        # Update explosion animation
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                # If animation is complete, delete the explosion
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# Create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart, 2)

# Create sprite groups
enemy_group, bullet_group, grenade_group, explosion_group, item_box_group, decoration_group, water_group, exit_group = (pygame.sprite.Group() for _ in range(8))

# Create empty tile list
world_data = [[-1] * COLS for _ in range(ROWS)]

# Load in level data and create world
with open(f'D:/pic/img/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)

    if not start_game:
        # Draw menu
        screen.fill(BG)

        # Add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
    else:
        # Update background and draw world map
        draw_background()
        world.draw()

        # Show player health, ammo, and grenades
        health_bar.draw(player.health)
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet, (90 + (x * 10), 40))
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(bomb, (135 + (x * 15), 60))

        # Update and draw player, enemies, and groups
        player.update()
        player.draw()
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Update player actions if the player is alive
        if player.alive:
            # Shoot bullets if the shoot key is pressed
            if shoot:
                player.shoot()
            # Throw grenades if the grenade key is pressed and a grenade hasn't been thrown already
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + 0.5 * player.rect.size[0] * player.direction, player.rect.top,
                                  player.direction)
                grenade_group.add(grenade)
                # Reduce the number of grenades the player has
                player.grenades -= 1
                grenade_thrown = True
            # Update player action depending on whether the player is jumping, running, or idle
            if player.in_air:
                player.update_action(2)  # 2: jump
            elif moving_left or moving_right:
                player.update_action(1)  # 1: run
            else:
                player.update_action(0)  # 0: idle
            # Move the player and scroll the screen
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # If the player has completed the level, go to the next level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                # Reset the level data
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Load level data from a CSV file and create the world
                    with open(f'D:/pic/img/level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)
        # If the player is not alive, show the death fade
        else:
            # If the restart button is pressed, reset the level data and go to the first level
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                # Load level data from a CSV file and create the world
                with open(f'D:/pic/img/level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Quit the game if the user closes the window
            run = False
        elif event.type == pygame.KEYDOWN:
            # Process key presses
            if event.key == pygame.K_a:
                moving_left = True
            elif event.key == pygame.K_d:
                moving_right = True
            elif event.key == pygame.K_SPACE:
                shoot = True
            elif event.key == pygame.K_q:
                grenade = True
            elif event.key == pygame.K_w and player.alive:
                player.jump = True
            elif event.key == pygame.K_ESCAPE:
                # Quit the game if the user presses the escape key
                run = False
        elif event.type == pygame.KEYUP:
            # Process key releases
            if event.key == pygame.K_a:
                moving_left = False
            elif event.key == pygame.K_d:
                moving_right = False
            elif event.key == pygame.K_SPACE:
                shoot = False
            elif event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    # Update the display
    pygame.display.update()

pygame.quit()