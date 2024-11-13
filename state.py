"""
STATE REPRESENTATION
For instance, for (6 x 7) map dimension
state is represented with 3 values of 42 (6 x 7) bits
representing spaceships (S), obstacles (O) and goals (G).
Row numbers increase from top to bottom,
while column numbers increase from left to right.
 0   1   2   3   4   5   6 | column id
 =====================================
 0   1   2   3   4   5   6 | 0th row
 7   8   9  10  11  12  13 | 1st row
14  15  16  17  18  19  20 | 2nd row
21  22  23  24  25  26  27 | 3rd row
28  29  30  31  32  33  34 | 4th row
35  36  37  38  39  40  41 | 5th row

For instance:
STATE            STATE_binary_    spaceships state  obstacles state  goals state
_ _ _ _ _ _ G    0 0 0 0 0 0 1    0 0 0 0 0 0 0     0 0 0 0 0 0 0    0 0 0 0 0 0 1
_ _ _ _ _ _ _    0 0 0 0 0 0 0    0 0 0 0 0 0 0     0 0 0 0 0 0 0    0 0 0 0 0 0 0
_ _ S _ _ _ G    0 0 1 0 0 0 1    0 0 1 0 0 0 0     0 0 0 0 0 0 0    0 0 0 0 0 0 1
_ _ O _ _ _ _    0 0 1 0 0 0 0    0 0 0 0 0 0 0     0 0 1 0 0 0 0    0 0 0 0 0 0 0
_ _ _ _ _ _ _    0 0 0 0 0 0 0    0 0 0 0 0 0 0     0 0 0 0 0 0 0    0 0 0 0 0 0 0
_ _ _ _ O _ S    0 0 0 0 1 0 1    0 0 0 0 0 0 1     0 0 0 0 1 0 0    0 0 0 0 0 0 0
"""
import copy
import math

import config
from sprites import Spaceship, Obstacle, Goal, Empty


class State:
    def __init__(self, bit_mask, spaceships, obstacles, goals):
        self.bit_mask = bit_mask
        self.spaceships = spaceships
        self.obstacles = obstacles
        self.goals = goals
        self.row_masks = [((1 << config.N) - 1) << (i * config.N) for i in range(config.M - 1, -1, -1)]

    def __str__(self):
        return '\n'.join(
            [' '.join([Spaceship.kind() if ((mask := 1 << (i * config.N + j)) & self.spaceships) == mask else
                       Obstacle.kind() if (mask & self.obstacles) == mask else
                       Goal.kind() if (mask & self.goals) == mask else
                       Empty.kind() for j in range(config.N)])
             for i in range(0, config.M)])

    def __eq__(self, other):
        return self.get_state(Spaceship.kind()) == other.get_state(Spaceship.kind())

    def get_state(self, kind=None):
        if kind is None:
            return self.spaceships | self.obstacles | self.goals
        elif kind == Spaceship.kind():
            return self.spaceships
        elif kind == Obstacle.kind():
            return self.obstacles
        elif kind == Goal.kind():
            return self.goals
        else:
            return None

    def is_goal_state(self):
        return self.spaceships == self.goals

    @staticmethod
    def get_action_cost(action):
        return int(abs(action[0][0] - action[1][0]) + abs(action[0][1] - action[1][1]))

    def get_legal_actions(self):
        if self.is_goal_state():
            return []
        actions = []
        obs = self.spaceships | self.obstacles
        spaceships = self.spaceships
        while spaceships:
            s = spaceships & -spaceships
            o = obs & ~s
            # up
            new_b = s
            while (val := (new_b >> config.N)) and not (val & o):
                new_b = val
            actions.append((int(math.log2(s)), int(math.log2(new_b))))
            # right
            m = next(filter(lambda _m: _m & s, self.row_masks))
            new_b = s
            while (val := (new_b << 1)) & m and not (val & o):
                new_b = val
            actions.append((int(math.log2(s)), int(math.log2(new_b))))
            # down
            new_b = s
            while (val := (new_b << config.N)) < self.bit_mask and not (val & o):
                new_b = val
            actions.append((int(math.log2(s)), int(math.log2(new_b))))
            # left
            new_b = s
            while (val := (new_b >> 1)) & m and not (val & o):
                new_b = val
            actions.append((int(math.log2(s)), int(math.log2(new_b))))
            spaceships &= spaceships - 1
        actions = [((int(a[0] / config.N), a[0] % config.N),
                    (int(a[1] / config.N), a[1] % config.N))
                   for a in actions if a[0] != a[1]]
        return actions

    def generate_successor_state(self, action):
        if self.is_goal_state():
            raise Exception(f'State is goal!\n{self}')
        if action not in self.get_legal_actions():
            raise Exception(f'Illegal action {action}!')
        copy_state = copy.copy(self)
        mask = (1 << (action[0][0] * config.N + action[0][1])) & self.bit_mask
        copy_state.spaceships &= ~mask  # clear spaceship from current position
        mask = (1 << (action[1][0] * config.N + action[1][1])) & self.bit_mask
        copy_state.spaceships |= mask  # set spaceship to next position
        return copy_state
