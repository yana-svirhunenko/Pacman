import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity

class Ghost(Entity):

    def __init__(self, node, color=None, speed=None, algorithm=None):
        Entity.__init__(self, node, color=color, speed=speed, algorithm=algorithm)
        self.name = GHOST
        self.path = None
        self.goal = Vector2()
