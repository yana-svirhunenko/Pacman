import random
import pygame
from pygame.locals import *
from entities.entity import *
import math

center = Vector2(180, 270)
def dijkstra_find_path(start_node, finish_node, return_dist=False):

    node_queue = [(0, start_node, [start_node])]
    distances = {start_node: 0}
    visited = set()

    while node_queue:

        node_queue.sort(key=lambda x: x[0])
        current_distance, current_node, path = node_queue[0]
        node_queue.pop(0)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == finish_node:
            if return_dist:
                return current_distance
            else:
                return path

        for direction, neighbor in current_node.neighbors.items():
            if neighbor is None:
                continue
            if neighbor not in visited:
                distance_to_neighbor = distance(current_node.position, neighbor.position)
                new_distance = current_distance + distance_to_neighbor

                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    node_queue.append((new_distance, neighbor, path + [neighbor]))

    return None
def distance(vec1, vec2):
    return math.sqrt((vec2.x - vec1.x)**2 + (vec2.y - vec1.y)**2)
class Pacman(Entity):

    def __init__(self, node, speed=None, path=None):
        Entity.__init__(self, node=node, speed=speed)
        self.name = PACMAN
        self.color = YELLOW
        self.alive = True
        self.path = path
        self.t_start = 0

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def reset(self, node):

        self.alive = True
        self.node = node
        self.target = node
        self.setPosition()

    def die(self):
        self.alive = False
        self.direction = STOP

    def far(self, ghosts):

        for g in ghosts:
            if distance(self.position, g.position) <= 100:
                return False
        return True


    def on_one_line(self, obj):
        if abs(self.position.x - obj.position.x) >= 1 and abs(self.position.y - obj.position.y) >= 1:
            return False
        return False


    def goalDirection(self, directions, goal):
        distances = []
        for direction in directions:
            vec = self.node.position + self.directions[direction] * TILEWIDTH - goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(max(distances))
        return directions[index]


    def update(self, dt, ghosts=None):

        self.position += self.directions[self.direction] * self.speed * dt

        if self.overshotTarget():

            self.node = self.target
            dir = self.validDirections()
            directions = []

            for d in dir:

                t = self.getNewTarget(d)
                pacmen_dist = distance(t.position, self.position)
                p_time = pacmen_dist / 100
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
                            dist = d1 + d2

                    print((dist - 7) / 90)
                    g_time.append((dist - 7) / 90)

                if all(p_time < gt for gt in g_time):
                    directions.append(d)

            if len(directions) >= 1:
                self.direction = self.randomDirection(directions)
                self.target = self.getNewTarget(self.direction)
                return
                if random.choice([True, False]):
                    self.direction = self.goalDirection(directions, center)
                    self.target = self.getNewTarget(self.direction)
                else:
                    self.direction = directions[0]
                    self.target = self.getNewTarget(self.direction)

            self.handleNoPath()

        else:
            for g in ghosts:
                if self.on_one_line(g) and distance(self.position, g.position <= 50):
                    directions = [self.direction, self.direction * -1]
                    self.direction = self.goalDirection(directions, g.position)
                    self.target = self.getNewTarget(self.direction)



        return

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


    def render(self, screen):
        p = self.position.asInt()
        pygame.draw.circle(screen, self.color, p, self.radius)

