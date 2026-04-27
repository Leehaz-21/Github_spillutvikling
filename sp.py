import pygame
from pygame.locals import *

pygame.init()

screen_width=1000
screen_height=700

screen=pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Leo sitt spill")
clock = pygame.time.Clock()

#define game variables
tile_size= 50

#load images
bg_img=pygame.image.load("Graphics/BG-Dark-Fantasy-1.png")



class Player():
    def __init__(self, x, y):
        img = pygame.image.load("Graphics/Figur 10.png")
        self.image = pygame.transform.scale(img, (40, 80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False

    def update(self, tile_list):

        dx = 0
        dy = 0

        # key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jumped:
            self.vel_y = -15
            self.jumped = True
        if not key[pygame.K_SPACE]:
            self.jumped = False
        if key[pygame.K_LEFT]:
            dx -= 5
        if key[pygame.K_RIGHT]:
            dx += 5

        # gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # move horizontally and check collisions
        self.rect.x += dx
        for tile in tile_list:
            if self.rect.colliderect(tile[1]):
                if dx > 0:
                    self.rect.right = tile[1].left
                elif dx < 0:
                    self.rect.left = tile[1].right

        # move vertically and check collisions
        self.rect.y += dy
        for tile in tile_list:
            if self.rect.colliderect(tile[1]):
                if self.vel_y > 0:
                    self.rect.bottom = tile[1].top
                    self.vel_y = 0
                    self.jumped = False
                elif self.vel_y < 0:
                    self.rect.top = tile[1].bottom
                    self.vel_y = 0

        # floor collision
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.vel_y = 0
            self.jumped = False

        # tegn spilleren
        screen.blit(self.image, self.rect)
        

class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        stone_img=pygame.image.load("Graphics/Skjermbilde 2026-03-17 131626.png")
        row_count=0
        for row in data:
            col_count= 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(stone_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

                   

world_data=[
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0],
[0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

Player= Player(100, screen_height - 130)
world= World(world_data)

run = True
while run:

    screen.blit(bg_img,(0,0))

    world.draw()

    Player.update(world.tile_list)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
