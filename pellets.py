import pygame
from vector import Vector2
from constants import *
import numpy as np


class Pellet(object):
    def __init__(self, row, column):
        self.name = PELLET
        self.position = Vector2(column * TILEWIDTH, row * TILEHEIGHT)
        self.color = WHITE
        self.radius = int(4 * TILEWIDTH / 16)
        self.collideRadius = int(4 * TILEWIDTH / 16)
        self.points = 10
        self.visible = True

    def render(self, screen):
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.flashTime:
            self.visible = not self.visible
            self.timer = 0


class PelletGroup(object):
    def __init__(self, map):
        self.pelletList = []
        self.createPelletList(map)
        self.numEaten = 0
                
    def createPelletList(self, map):
        for row in range(map.shape[0]):
            for col in range(map.shape[1]):
                if map[row][col] in ['.', '+']:
                    self.pelletList.append(Pellet(row, col))

    
    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False
    
    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)