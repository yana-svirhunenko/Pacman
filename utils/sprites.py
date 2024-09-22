import pygame
from utils.constants import *
from utils.animation import *

BASETILEWIDTH = 16
BASETILEHEIGHT = 16


class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("spritesheet.png").convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def getImage(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class PacmanSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)

        self.animations = {}
        self.defineAnimations()
        self.stopimage = (8, 0)
        self.entity = entity
        self.entity.image = self.getStartImage()

    def getStartImage(self):
        return self.getImage(8, 0)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        self.animations[LEFT] = Animator(((8, 0), (0, 0), (0, 2), (0, 0)))
        self.animations[RIGHT] = Animator(((10, 0), (2, 0), (2, 2), (2, 0)))
        self.animations[UP] = Animator(((10, 2), (6, 0), (6, 2), (6, 0)))
        self.animations[DOWN] = Animator(((8, 2), (4, 0), (4, 2), (4, 0)))

    def update(self, dt):

        if self.entity.direction == LEFT:
            self.entity.image = self.getImage(*self.animations[LEFT].update(dt))
            self.stopimage = (8, 0)
        elif self.entity.direction == RIGHT:
            self.entity.image = self.getImage(*self.animations[RIGHT].update(dt))
            self.stopimage = (10, 0)
        elif self.entity.direction == DOWN:
            self.entity.image = self.getImage(*self.animations[DOWN].update(dt))
            self.stopimage = (8, 2)
        elif self.entity.direction == UP:
            self.entity.image = self.getImage(*self.animations[UP].update(dt))
            self.stopimage = (10, 2)
        elif self.entity.direction == STOP:
            self.entity.image = self.getImage(*self.stopimage)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class GhostSprites(Spritesheet):
    def __init__(self, entity):
        Spritesheet.__init__(self)
        #self.x = {0, 1, INKY: 4, CLYDE: 6}
        self.entity = entity
        self.entity.image = self.getStartImage()

    def getStartImage(self):
        return self.getImage(self.entity.id , 4)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2 * TILEWIDTH, 2 * TILEHEIGHT)


class LifeSprites(Spritesheet):
    def __init__(self, numlives):
        Spritesheet.__init__(self)
        self.resetLives(numlives)

    def removeImage(self):
        if len(self.images) > 0:
            self.images.pop(0)

    def resetLives(self, numlives):
        self.images = []
        for i in range(numlives):
            self.images.append(self.getImage(0,0))

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)


class MazeSprites:
    def __init__(self, maze_matrix):
        self.data = maze_matrix

    def constructBackground(self, background, tile_width, tile_height):

        colors = {
            '0': (0, 0, 255),
            '9': (0, 0, 255),
            '3': (0, 0, 0),
            '.': (0, 0, 0),
            '+': (0, 0, 0),
            '=': (0, 0, 255),
            '-': (0, 0, 0),
            '#': (0, 0, 0),
            '?': (0, 0, 0)
        }

        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                char = self.data[row][col]
                color = colors.get(char, (128, 128, 128))
                pygame.draw.rect(
                    background,
                    color,
                    pygame.Rect(col * tile_width - 7, row * tile_height - 10, tile_width, tile_height)
                )
        return background


