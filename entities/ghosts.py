from pygame.locals import *
from utils.vector import Vector2
from utils.constants import *
from entities.entity import Entity

class Ghost(Entity):

    def __init__(self, node, color, speed, algorithm):
        Entity.__init__(self, node, color=color, speed=speed, algorithm=algorithm)
        self.name = GHOST
        self.goal = Vector2()
        self.path = None

    def reset(self, node):
        self.node = node
        self.target = node
        self.setPosition()

