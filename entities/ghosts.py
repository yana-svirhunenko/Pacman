from pygame.locals import *
from utils.vector import Vector2
from utils.constants import *
from entities.entity import Entity
from utils.sprites import GhostSprites

class Ghost(Entity):

    def __init__(self, node, color, speed, algorithm, id=None):
        Entity.__init__(self, node, color=color, speed=speed, algorithm=algorithm)
        self.name = GHOST
        self.goal = Vector2()
        self.path = None
        self.id = id
        self.sprites = GhostSprites(self)

    def reset(self, node):
        self.node = node
        self.target = node
        self.setPosition()

