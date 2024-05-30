"""
A simplified version of the original file.
This version uses constant acceleration.
User input can be applied continiously (instead of having to be pressed each time).
Input adds upward velocity to the bird.
The bird moves in x while the background and single pipe is static.
The single pipe always appears at the same location.
This creates a simpler linear model for the first implementation.

Date Modified:  March 17, 2024
Author: Tech With Tim + daahl
"""
import pygame
import random
import os
import time
import numpy as np
import controllers as ctrl
pygame.font.init()  # init font

WIN_WIDTH = 1000
WIN_HEIGHT = 700
PIPE_VEL = 3
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird Simplfied")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (WIN_WIDTH, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

class Bird:
    """
    Bird class representing the flappy bird
    """
    WIN_HEIGHT = 0
    WIN_WIDTH = 0
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.gravity = 9.8
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        #self.xvel = 0
        self.base_y_vel = 5
        self.jump_y_vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.jump_y_vel = -10
        self.height = self.y
        
    def notjump(self):
        """
        make the bird not jump
        :return: None
        """
        self.jump_y_vel = 0
        self.height = self.y
        
    def move(self):
        """
        make the bird move
        :return: None
        """

        # calculate velocity
        y_vel = self.base_y_vel + self.jump_y_vel  

        # calculate new position
        self.y = self.y + y_vel
        
        self.x += 5

        if y_vel < 0:  # tilt up
            self.tilt = self.MAX_ROTATION
        else:  # tilt down
            self.tilt = -self.MAX_ROTATION

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)

class Pipe():
    """
    represents a pipe object
    """
    WIN_HEIGHT = WIN_HEIGHT
    WIN_WIDTH = WIN_WIDTH
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0
        self.gap = 100  # gap between top and bottom pipe

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        #self.height = random.randrange(50, 450)
        self.height = 200
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False
    
    def get_gap_center(self):
        return self.height + self.GAP/2

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIN_WIDTH = WIN_WIDTH
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def menu_screen(win):
    """
    the menu screen that will start the game
    :param win: the pygame window surface
    :return: None
    """
    pass

def end_screen(win):
    """
    display an end screen when the player loses
    :param win: the pygame window surface
    :return: None
    """
    run = True
    text_label = END_FONT.render("Press Space to Restart", 1, (255,255,255))
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(win)

        win.blit(text_label, (WIN_WIDTH/2 - text_label.get_width()/2, 500))
        pygame.display.update()

    pygame.quit()
    quit()

def draw_window(win, bird, pipe, base, score):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :return: None
    """
    win.blit(bg_img, (0,0))

    pipe.draw(win)

    base.draw(win)
    bird.draw(win)
    
    # test figures
    # center line of the game
    pipe_gap_center = pipe.get_gap_center()
    pygame.draw.line(win, (255,0,0), (0, pipe_gap_center), (WIN_WIDTH, pipe_gap_center), 1)
    
    # constraint boxes
    # TODO pygame.draw.rect(win, (255,0,0), (0,0,WIN_WIDTH,FLOOR), 1)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()


def main(win):
    """
    Runs the main game loop
    :param win: pygame window surface
    :return: None
    """
    #bird = Bird(230,350)
    bird = Bird(230, WIN_HEIGHT/2)
    base = Base(FLOOR)
    pipe = Pipe(WIN_WIDTH - 350)
    score = 0

    clock = pygame.time.Clock()
    start = False
    lost = False
    
    FRAMERATE = 30
    Ts = 1/FRAMERATE

    run = True
    while run:
        pygame.time.delay(30)
        clock.tick(FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        
        # input from controller
        if ctrl.pid(pipe.get_gap_center(), bird.y):
            bird.jump()
        else:
            bird.notjump()
        

        # new input method. Manual input
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_SPACE]:
        #     if not start:
        #                 start = True
        #                 start_time = time.time()
        #     bird.jump()
        # else:
        #     bird.notjump()
        
        # start game on input
        keys = pygame.key.get_pressed()
        if not start and keys[pygame.K_SPACE]:
            start = True
            start_time = time.time()
        
        # Move Bird
        if start:
            bird.move()

        # collide with floor
        #if bird.y + bird_images[0].get_height() - 10 >= FLOOR:
        #    break
        
        # test
        if bird.y == WIN_HEIGHT:
            break
        
        # check for collision
        if pipe.collide(bird, win):
            lost = True
            break
        
        # if start:
        #     print(f"Elapsed time: {time.time() - start_time}")

        draw_window(WIN, bird, pipe, base, score)

    end_screen(WIN)

main(WIN)