import random
import pygame
from pygame.locals import *
from entities.entity import *
from entities.behavior import *
from utils.sprites import PacmanSprites
import math


class Pacman(Entity):

    def __init__(self, node, speed=None, path=None, movement=None):
        Entity.__init__(self, node=node, speed=speed)
        self.name = PACMAN
        self.color = YELLOW
        self.alive = True
        self.path = path
        self.movement_type = movement
        self.sprites = PacmanSprites(self)
        self.counter = 0
        #self.cool_down = 100
        self.avoid = None

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False


    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def reset(self, node):

        self.alive = True
        self.node = node
        self.target = node
        self.setPosition()

    def die(self):
        self.alive = False
        self.direction = STOP


    def on_one_line(self, obj):
        if abs(self.position.x - obj.position.x) <= 5 or abs(self.position.y - obj.position.y) <= 5:
            return True
        return False


    def opposite_direction(self, directions, goal):
        distances = []
        for direction in directions:
            vec = self.position + self.directions[direction] * TILEWIDTH - goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]


    def should_avoid(self, target):

        for node in self.avoid:
            if node == target:
                return True
        return False


    def automatic_movement(self, ghosts):

        if self.overshotTarget():

            self.node = self.target
            dir = self.validDirections()
            directions = []

            for d in dir:

                t = self.getNewTarget(d)
                if self.should_avoid(t):
                    continue

                pacmen_dist = distance(t.position, self.position)
                p_time = pacmen_dist / self.speed
                g_time = []

                for g in ghosts:
                    if g.target == t:
                        dist = distance(t.position, g.position) - 7
                    elif g.node == t:
                        dist = distance(self.position, g.position) - 7
                    else:
                        d1 = distance(g.position, g.target.position)
                        d2 = dijkstra_find_path(g.target, t, return_dist=True)
                        if d1 is None or d2 is None:
                            dist = 10000
                        else:
                            dist = d1 + d2 - 7
                    g_time.append(dist / g.speed)

                if all(p_time < gt for gt in g_time):
                    directions.append(d)

            if len(directions) >= 1:
                self.direction = self.randomDirection(directions)
                self.target = self.getNewTarget(self.direction)
                return

            self.handleNoPath()

        else:

            if self.counter <= 100:
                self.counter += 1
                return

            for g in ghosts:
                if self.on_one_line(g) and distance(self.position, g.position) <= 20:

                    directions = [self.direction, self.direction * -1]
                    self.direction = self.opposite_direction(directions, g.position)
                    temp = self.node
                    self.node = self.target
                    self.target = temp
                    self.counter = 2
                    return


    def manual_movement(self):

        direction = self.getValidKey()
        if self.overshotTarget():
            self.node = self.target
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()


    def update(self, dt, ghosts=None):

        self.sprites.update(dt)

        if self.counter < 1:
            self.direction = DOWN
            self.target = self.getNewTarget(self.direction)
            self.counter += 1
            return

        self.position += self.directions[self.direction] * self.speed * dt
        if self.movement_type == 'automatic':
            self.automatic_movement(ghosts)
        elif self.movement_type == 'manual':
            self.manual_movement()


    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP


    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius + self.collideRadius) ** 2
            if dSquared <= rSquared:
                return pellet
        return None


    #def render(self, screen):
     #  pygame.draw.circle(screen, self.color, p, self.radius)

