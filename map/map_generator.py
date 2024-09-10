import random
import numpy as np


def can_place_node(r, c, nodesr, nodesc, matrix):

    if matrix[r, c] != '0':
        return False
    if any(r + dr in nodesr for dr in [-1, 0, 1]) or any(c + dc in nodesc for dc in [-1, 0, 1]):
        return False
    return True


def extract_node_coordinates(matrix):

    nodesr, nodesc = [], []
    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            if matrix[r, c] == '+':
                nodesr.append(r)
                nodesc.append(c)
    return nodesr, nodesc


def connect_node(r, c, matrix, difficulty):

    try:
        chance = 1 / difficulty
    except Exception:
        chance = 1/10

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    sides = [0, 0, 0, 0]

    random_indices = random.sample(range(4), 2)
    for idx in random_indices:
        sides[idx] = 1

    for i in range(4):
        if sides[i] == 0:
            sides[i] = 1 if random.random() < chance else 0

    for i, (dr, dc) in enumerate(directions):

        if sides[i] == 0:
            continue

        nr, nc = r, c
        while 0 <= nr < matrix.shape[0] and 0 <= nc < matrix.shape[1]:
            nr += dr
            nc += dc
            if matrix[nr, nc] == '0':
                matrix[nr, nc] = '.'
            elif matrix[nr, nc] == '.':
                matrix[nr, nc] = '+'
                if random.choice([True * 8, False * 2]):
                    break
            elif matrix[nr, nc] in ['+', '9', '=']:
                break


def is_inside_room(r, c, room_params):

    start_row, room_height, start_col, room_width = room_params
    return start_row <= r < start_row + room_height and start_col <= c < start_col + room_width


def place_nodes(matrix, num_nodes, nodesr, nodesc, row_range, col_range, room_params, difficulty):

    attempts = 50
    r1, r2 = row_range
    c1, c2 = col_range

    for _ in range(num_nodes):
        for attempt in range(attempts):
            r, c = random.randint(r1, r2), random.randint(c1, c2)
            if not is_inside_room(r, c, room_params) and can_place_node(r, c, nodesr, nodesc, matrix):
                matrix[r, c] = '+'
                nodesr.append(r)
                nodesc.append(c)
                connect_node(r, c, matrix, difficulty)
                break


def generate_map(difficulty):

    matrix = np.full((36, 29), '0', dtype=str)
    upper_margin = 3
    lower_margin = 1
    matrix[:, 0] = '9'
    matrix[:, -1] = '9'
    matrix[upper_margin, :] = '9'
    matrix[-(lower_margin + 1), :] = '9'

    matrix[:upper_margin, :] = '3'
    matrix[-lower_margin:, :] = '3'

    room_height, room_width = 6, 9
    start_row = (36 - room_height) // 2
    start_col = (29 - room_width) // 2

    matrix[start_row:start_row + room_height, start_col] = '9'
    matrix[start_row:start_row + room_height, start_col + room_width - 1] = '9'
    matrix[start_row + room_height - 1, start_col:start_col + room_width] = '9'
    matrix[start_row, start_col:start_col + room_width] = '9'

    entrance_col_start = start_col + (room_width // 2) - 1
    matrix[start_row, entrance_col_start:entrance_col_start + 3] = '='
    matrix[start_row + 1:start_row + room_height - 1, start_col + 1:start_col + room_width - 1] = '-'

    matrix[1 + upper_margin, 2:27] = '.'
    matrix[34 - lower_margin, 2:27] = '.'
    matrix[1 + upper_margin:34 - lower_margin, 1] = '.'
    matrix[1 + upper_margin:34 - lower_margin, 27] = '.'
    matrix[17, 1:9] = '.'
    matrix[17, 19:27] = '.'
    matrix[1 + upper_margin:14, 14] = '.'
    matrix[21:34 - lower_margin, 14] = '.'

    start_row -= 1
    start_col -= 1
    room_width += 2
    room_height += 2

    room_corners = [(start_row, start_col), (start_row, start_col + room_width - 1),
                    (start_row + room_height - 1, start_col),
                    (start_row + room_height - 1, start_col + room_width - 1)]
    for r, c in room_corners:
        matrix[r, c] = '+'

    matrix[start_row, start_col + 1:start_col + room_width - 1] = '.'
    matrix[start_row + room_height - 1, start_col + 1:start_col + room_width - 1] = '.'
    matrix[start_row + 1:start_row + room_height - 1, start_col] = '.'
    matrix[start_row + 1:start_row + room_height - 1, start_col + room_width - 1] = '.'

    inner_corners = [(upper_margin + 1, 1), (upper_margin + 1, 27),
                     (34 - lower_margin, 1), (34 - lower_margin, 27),
                     (17, 1), (17, 9), (17, 19), (17, 27), (upper_margin + 1, 14),
                     (14, 14), (21, 14), (34 - lower_margin, 14)]

    for r, c in inner_corners:
        matrix[r, c] = '+'

    num_nodes = (difficulty * 5 + 7) // 4
    nodesr, nodesc = extract_node_coordinates(matrix)
    room_params = [start_row, room_height, start_col, room_width]

    quadrants = [
        (upper_margin, 17, upper_margin, 13),
        (upper_margin, 17, 14, 27),
        (18, 34 - lower_margin, upper_margin, 13),
        (18, 34 - lower_margin, 14, 27)
    ]

    for i in range(num_nodes):
        for quadrant in quadrants:
            row_range, col_range = quadrant[:2], quadrant[2:]
            place_nodes(matrix, 1, nodesr, nodesc, row_range, col_range, room_params, difficulty)

    matrix[start_row, entrance_col_start:entrance_col_start + 3] = '+'
    matrix[start_row + 2, entrance_col_start:entrance_col_start + 3] = '?'

    for row in matrix:
        print("".join(row))

    return matrix