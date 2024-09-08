import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity

class Ghost(Entity):

    def __init__(self, node, algorithm=None):
        Entity.__init__(self, node, algorithm)
        self.name = GHOST
        self.path = None
        self.goal = Vector2()
