import pygame
import sys


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Leo sitt spill")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


clock = pygame.time.Clock()
FPS = 60

try:
    background = pygame.image.load("Graphics/BG-Dark-Fantasy-1.png").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    
    player_image = pygame.image.load("Graphics/Figur 10.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (40, 60))  

    
    enemy_image = pygame.image.load("Graphics/New Piskel (1).png").convert_alpha()
    enemy_image = pygame.transform.scale(enemy_image, (40, 60))


    platform_image = pygame.image.load("Graphics/Skjermbilde 2026-03-17 131626.png").convert_alpha()

    weapon_image = pygame.image.load("Graphics/New Piskel (4).png").convert_alpha()
    weapon_image = pygame.transform.scale(weapon_image, (30, 40))  

except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

font = pygame.font.SysFont(None, 36)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_speed = -15
        self.on_ground = False
        self.direction = 1  
        self.health = 100
        self.max_health = 100
        self.invincible_timer = 0
        self.attack_cooldown = 0

    def take_damage(self, amount):
        if self.invincible_timer <= 0:
            self.health -= amount
            self.invincible_timer = 5 
            if self.health < 0:
                self.health = 0

    def update(self, platforms):
        
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:  
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        
        if self.direction == -1:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image

        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
            if self.invincible_timer % 4 < 2:  
                self.image = self.image.copy()
                self.image.set_alpha(128)  
            else:
                self.image = self.original_image.copy()
                if self.direction == -1:
                    self.image = pygame.transform.flip(self.image, True, False)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw_health_bar(self, surface, x, y):
        
        pygame.draw.rect(surface, RED, (x, y, 200, 20))
        
        health_width = (self.health / self.max_health) * 200
        pygame.draw.rect(surface, GREEN, (x, y, health_width, 20))
      
        pygame.draw.rect(surface, BLACK, (x, y, 200, 20), 2)

    def move(self, dx, dy):
        
        self.rect.x += dx * self.speed
        
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_speed
            self.on_ground = False

    def attack(self, weapons_group):
        if self.attack_cooldown <= 0 and len(weapons_group) == 0:
           
            weapon = Weapon(self.rect.centerx, self.rect.centery, weapon_image, self.direction)
            weapons_group.add(weapon)
            self.attack_cooldown = 20  


class Weapon(pygame.sprite.Sprite):
    def __init__(self, x, y, image, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.direction = direction

        self.speed = 12
        self.max_distance = 220
        self.start_x = x
        self.returning = False

    
        if self.direction == 1:
            self.rect.x += 35
        else:
            self.rect.x -= 35
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player):
      
        if not self.returning:
            self.rect.x += self.speed * self.direction
            if abs(self.rect.centerx - self.start_x) >= self.max_distance:
                self.returning = True
        else:
            
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = max(1, (dx**2 + dy**2) ** 0.5)
            self.rect.x += int(self.speed * dx / dist)
            self.rect.y += int(self.speed * dy / dist)

            
            if self.rect.colliderect(player.rect):
                self.kill()


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        
        self.image = pygame.Surface((width, height))
        self.image.set_colorkey((0, 0, 0))  
      
        scaled_height = height
        scaled_width = int(platform_image.get_width() * (height / platform_image.get_height()))
        
        scaled_platform = pygame.transform.scale(platform_image, (scaled_width, scaled_height))
        
      
        for i in range(0, width, scaled_width):
            self.image.blit(scaled_platform, (i, 0))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2
        self.vel_y = 0
        self.gravity = 0.8
        self.direction = -1  
        self.move_timer = 0
        self.health = 50

    def update(self, platforms, player):
       
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    on_ground = True

        self.move_timer += 1
        if self.move_timer > 120:  
            self.direction *= -1
            self.move_timer = 0

        
        feet_x = self.rect.centerx + (self.direction * 25)  
        feet_on_platform = False
        for platform in platforms:
            if (platform.rect.left <= feet_x <= platform.rect.right and 
                abs(self.rect.bottom - platform.rect.top) < 5):
                feet_on_platform = True
                break
        
        if not feet_on_platform:
            self.direction *= -1  

        if abs(self.rect.x - player.rect.x) < 200:
            if self.rect.x < player.rect.x:
                self.direction = 1
            else:
                self.direction = -1

        self.rect.x += self.direction * self.speed

       
        if self.rect.colliderect(player.rect):
            player.take_damage(15)

       
        if self.direction == -1:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

class Minion(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        self.vel_y = 0
        self.gravity = 0.8
        self.direction = 1  
        self.move_timer = 0
        self.health = 20

    def update(self, platforms, player):
        
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    on_ground = True

        self.move_timer += 1
        if self.move_timer > 60:  
            self.direction *= -1
            self.move_timer = 0

        feet_x = self.rect.centerx + (self.direction * 25)  
        feet_on_platform = False
        for platform in platforms:
            if (platform.rect.left <= feet_x <= platform.rect.right and 
                abs(self.rect.bottom - platform.rect.top) < 5):
                feet_on_platform = True
                break
        
        if not feet_on_platform:
            self.direction *= -1  

        self.rect.x += self.direction * self.speed

        
        if self.rect.colliderect(player.rect):
            player.take_damage(10)

      
        if self.direction == -1:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0


platforms = pygame.sprite.Group()

platforms.add(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

platforms.add(Platform(200, 450, 150, 20))
platforms.add(Platform(450, 350, 150, 20))
platforms.add(Platform(100, 250, 150, 20))
platforms.add(Platform(500, 150, 150, 20))


player = Player(50, SCREEN_HEIGHT - 110, player_image)


minion_image = pygame.transform.scale(enemy_image, (30, 45))
minions = pygame.sprite.Group()
minions.add(Minion(300, SCREEN_HEIGHT - 110, minion_image))
minions.add(Minion(400, 320, minion_image))  
minions.add(Minion(600, 220, minion_image))  


weapons = pygame.sprite.Group()

boss = None

game_over = False
player_won = False
boss_spawned = False


running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
       
        keys = pygame.key.get_pressed()
        dx = 0

        if keys[pygame.K_a]:
            dx = -1
            player.direction = -1
        if keys[pygame.K_d]:
            dx = 1
            player.direction = 1
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            player.jump()
        if keys[pygame.K_q] or keys[pygame.K_e]:
            player.attack(weapons)

        player.move(dx, 0)

        
        player.update(platforms)

        weapons.update(player)

        for minion in minions:
            minion.update(platforms, player)
            
            for weapon in weapons:
                if weapon.rect.colliderect(minion.rect):
                    minion.take_damage(10)
                    weapon.kill()

        
        minions = pygame.sprite.Group([minion for minion in minions if minion.health > 0])

        
        if not boss_spawned and len(minions) == 0:
            boss = Enemy(650, SCREEN_HEIGHT - 110, enemy_image)
            boss_spawned = True

        
        if boss:
            boss.update(platforms, player)
            
            for weapon in weapons:
                if weapon.rect.colliderect(boss.rect):
                    boss.take_damage(10)
                    weapon.kill()

        if boss and boss.health <= 0:
            game_over = True
            player_won = True
        elif player.health <= 0:
            game_over = True
            player_won = False
        elif player.rect.y > SCREEN_HEIGHT:
            game_over = True
            player_won = False

    screen.blit(background, (0, 0))

    
    for platform in platforms:
        screen.blit(platform.image, platform.rect)

    screen.blit(player.image, player.rect)

    for weapon in weapons:
        screen.blit(weapon.image, weapon.rect)

    for minion in minions:
        screen.blit(minion.image, minion.rect)

    if boss:
        screen.blit(boss.image, boss.rect)

    player.draw_health_bar(screen, 50, 50)

    if boss:
        boss_health_width = (boss.health / 50) * 200
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 250, 50, 200, 20))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 250, 50, boss_health_width, 20))
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH - 250, 50, 200, 20), 2)

    player_label = font.render("Player (WASD + Q/E to attack)", True, WHITE)
    screen.blit(player_label, (50, 20))

    if boss:
        boss_label = font.render("Boss", True, WHITE)
        screen.blit(boss_label, (SCREEN_WIDTH - 250, 20))
    else:
        minions_label = font.render(f"Minions Left: {len(minions)}", True, WHITE)
        screen.blit(minions_label, (SCREEN_WIDTH - 250, 20))

    if game_over:
        
        if player_won:
            game_over_text = font.render("You Win! Boss Defeated!", True, WHITE)
        else:
            if player.health <= 0:
                game_over_text = font.render("Game Over!", True, WHITE)
            
        restart_text = font.render("Press R to restart or Q to quit", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
          
            player = Player(50, SCREEN_HEIGHT - 110, player_image)
            minions = pygame.sprite.Group()
            minions.add(Minion(300, SCREEN_HEIGHT - 110, minion_image))
            minions.add(Minion(400, 320, minion_image))  
            minions.add(Minion(600, 220, minion_image))  
            weapons = pygame.sprite.Group()
            boss = None
            game_over = False
            player_won = False
            boss_spawned = False
        elif keys[pygame.K_q]:
            running = False

    pygame.display.flip()

pygame.quit()
sys.exit()