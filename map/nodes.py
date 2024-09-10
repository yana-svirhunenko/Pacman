import pygame
from utils.vector import Vector2
from utils.constants import *

pacman_node = [21, 14]
ghost_node = [18, 14]

class Node(object):

    def __init__(self, x, y, id):
        self.id = id
        self.position = Vector2(x, y)
        self.neighbors = {UP: None, DOWN: None, LEFT: None, RIGHT: None}

    def render(self, screen, col=None):
        for n in self.neighbors.keys():
            if self.neighbors[n] is not None:
                line_start = self.position.asTuple()
                line_end = self.neighbors[n].position.asTuple()
                pygame.draw.line(screen, WHITE, line_start, line_end, 4)
                if col is not None:
                    pygame.draw.circle(screen, col, self.position.asInt(), 12)
                else:
                    pygame.draw.circle(screen, RED, self.position.asInt(), 12)


class NodeGroup(object):

    def __init__(self, map):
        self.map = map
        self.nodesLUT = {}
        self.nodeSymbols = ['+', '-', '?']
        self.pathSymbols = ['.', '#']
        self.avoid = []
        self.start_node = None
        self.ghost_node = None
        self.createNodeTable(map)
        self.connectHorizontally(map)
        self.connectVertically(map)


    def get_avoid_nodes(self):
        return self.avoid

    def get_node_at_index(self, i):
        nodes_list = list(self.nodesLUT.values())
        if i < 0 or i >= len(nodes_list):
            raise IndexError("Index out of range.")
        return nodes_list[i]


    def createNodeTable(self, data, xoffset=0, yoffset=0):

        id = 0
        for row in list(range(data.shape[0])):
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    x, y = self.constructKey(col+xoffset, row+yoffset)
                    n = Node(x, y, id)
                    self.nodesLUT[(x, y)] = n

                    if [row, col] == pacman_node:
                        self.start_node = n

                    if [row, col] == ghost_node:
                        self.ghost_node = n

                    if data[row][col] == '?':
                        self.avoid.append(n)

                    id += 1


    def constructKey(self, x, y):
        return x * TILEWIDTH, y * TILEHEIGHT


    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            key = None
            for col in list(range(data.shape[1])):
                if data[row][col] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[RIGHT] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[LEFT] = self.nodesLUT[key]
                        key = otherkey
                elif data[row][col] not in self.pathSymbols:
                    key = None


    def connectVertically(self, data, xoffset=0, yoffset=0):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):
            key = None
            for row in list(range(dataT.shape[1])):
                if dataT[col][row] in self.nodeSymbols:
                    if key is None:
                        key = self.constructKey(col+xoffset, row+yoffset)
                    else:
                        otherkey = self.constructKey(col+xoffset, row+yoffset)
                        self.nodesLUT[key].neighbors[DOWN] = self.nodesLUT[otherkey]
                        self.nodesLUT[otherkey].neighbors[UP] = self.nodesLUT[key]
                        key = otherkey
                elif dataT[col][row] not in self.pathSymbols:
                    key = None

    def getNodeFromPixels(self, xpixel, ypixel):
        if (xpixel, ypixel) in self.nodesLUT.keys():
            return self.nodesLUT[(xpixel, ypixel)]
        return None

    def getNodeFromTiles(self, col, row):
        x, y = self.constructKey(col, row)
        if (x, y) in self.nodesLUT.keys():
            return self.nodesLUT[(x, y)]
        return None


    def render(self, screen, nodes_h=None, poses=None):
        for node in self.nodesLUT.values():
            render = True
            for p in poses:
                #print(node.position)
                if node == p:
                    node.render(screen, WHITE)
                    render = False
            if not render: continue

            if nodes_h is not None and node in nodes_h:
                node.render(screen, WHITE)
            else:
                node.render(screen)