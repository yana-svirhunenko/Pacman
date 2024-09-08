import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint

wait = True

class Entity(object):
    def __init__(self, node, algorithm=None):
        self.name = None
        self.directions = {UP: Vector2(0, -1), DOWN: Vector2(0, 1),
                           LEFT: Vector2(-1, 0), RIGHT: Vector2(1, 0), STOP: Vector2()}
        self.direction = STOP
        self.speed = 100 * TILEWIDTH / 16
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        self.node = node
        self.setPosition()
        self.target = node
        self.visible = True
        self.path = None
        self.algorithm = None

    def setPosition(self):
        self.position = self.node.position.copy()

    def validDirection(self, direction):
        if direction is not STOP:
            if self.node.neighbors[direction] is not None:
                return True
        return False


    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp

    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def setSpeed(self, speed):
        self.speed = speed * TILEWIDTH / 16

    def render(self, screen):
        if self.visible:
            p = self.position.asInt()
            pygame.draw.circle(screen, self.color, p, self.radius)

    def handleNoPath(self):

        self.direction = self.randomDirection(self.validDirections())
        self.target = self.getNewTarget(self.direction)


    def get_closer(self):
        self.direction = self.goalDirection(self.validDirections())
        self.target = self.getNewTarget(self.direction)

    def handlePath(self):

        try:
            ind = self.path.index(self.target)
        except ValueError:
            self.path = None
            self.handleNoPath()
            return

        if ind < len(self.path) - 1:

            self.target = self.path[ind + 1]
            for dir, neighbor in self.node.neighbors.items():
                if neighbor == self.target:
                    self.direction = dir
                    self.target = self.getNewTarget(self.direction)
                    return dir
        else:
            self.path = None
            self.handleNoPath()


    def handleCut(self):

        if self.path is not None:
            return

        if self.direction == STOP:
            self.handleNoPath()

        directions = self.validDirections()

        if self.direction in directions:
            directions.remove(self.direction)

        opposite_dir = self.direction * -1
        if opposite_dir in directions:
            directions.remove(opposite_dir)

        if len(directions) == 0:
            self.handleNoPath()

        d = self.direction
        self.direction = self.goalDirection(directions)
        target = self.getNewTarget(self.direction)
        self.target = target
        path = [self.target]

        if target.neighbors[d] is None:
            if target.neighbors[self.direction] is not None:
                path.append([target.neighbors[self.direction]])
                target = target.neighbors[self.direction]

        while True:

            if target.neighbors[d] is not None:
                path.append(target.neighbors[d])
                target = target.neighbors[d]
            else:
                break
            if len(path) >= 3:
                self.path = path
                self.algorithm = 'handling_cut'
                return

        self.handleNoPath()


    def update(self, dt):


        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshotTarget():
            self.node = self.target

            if self.algorithm == 'random':
                self.handleNoPath()
                self.setPosition()
                return

            if self.algorithm == 'cut':
                self.handleCut()
                self.setPosition()
                return

            if self.path is None:
                self.get_closer()
            else:
                self.handlePath()

            self.setPosition()


    def stop_movement(self):
        self.direction = STOP
        self.path = None


    def set_new_target_or_stop(self):
        try:
            ind = self.path.index(self.node)
        except ValueError:
            self.get_closer()
            return

        if ind < len(self.path) - 1:
            self.target = self.path[ind + 1]
            for dir, neighbor in self.node.neighbors.items():
                if neighbor == self.target:
                    self.direction = dir
        else:
            self.get_closer()

    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        return directions[randint(0, len(directions) - 1)]

    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        return directions[index]

