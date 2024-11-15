import random
from collections import deque

import config
from state import State

import heapq


class Node:
    def __init__(self, state, action):
        self.state = state
        self.action = action
        self.cost = 0
        self.cost_heuristic = 0
        self.parent = None

    def __lt__(self, other):
        return (self.cost + self.cost_heuristic) < (other.cost + other.cost_heuristic)

    def add_child(self, child, is_heuristic_algorithm):
        child.parent = self
        child.cost = child.parent.cost + State.get_action_cost(child.action)
        if is_heuristic_algorithm:
            child.cost_heuristic = child.parent.cost_heuristic + self.calc_heuristic(child.state)

    def get_actions(self):
        actions = []
        current = self
        while current.parent:
            if current.action is not None:
                actions.append(current.action)
            current = current.parent
        actions.reverse()
        return actions

    def state_exists_in_parents(self, state):
        parent_node = self
        while parent_node is not None:
            if parent_node.state.get_state('S') == state.get_state('S'):
                return True
            parent_node = parent_node.parent
        return False

    def calc_heuristic(self, state):
        goals = self.get_coordinates(state.goals)
        spaceships = self.get_coordinates(state.spaceships)

        total_distance = 0

        for goal in goals:
            min_distance = float('inf')

            for spaceship in spaceships:
                distance = abs(goal[0] - spaceship[0]) + abs(goal[1] - spaceship[1])
                min_distance = min(min_distance, distance)

            total_distance += min_distance

        return total_distance


    def get_coordinates(self, decimal_number):
        rows = config.N
        cols = config.M
        num = str(bin(decimal_number))[2:]
        string = reversed(num)
        coords = []
        col_num = 0
        row_num = 0
        for c in string:
            if c == '1':
                coords.append((row_num, col_num))
            col_num += 1
            if col_num % cols == 0:
                row_num += 1
                col_num = 0
        return coords


class Algorithm:

    def __init__(self):
        self.container = []

    def get_path(self, state):
        self.container = [Node(state, None)]
        while self.container:
            node = self.get_next_from_container()
            if node.state.is_goal_state():
                return node.get_actions()
            self.update_container(node)
        return None

    def create_successors(self, node, is_heuristic):
        successors = []

        for legal_action in node.state.get_legal_actions():
            next_state = node.state.generate_successor_state(legal_action)

            if node.state_exists_in_parents(next_state):
                continue

            next_node = Node(next_state, legal_action)
            node.add_child(next_node, is_heuristic)
            successors.append(next_node)
        return successors

    def update_container(self, node):
        pass

    def get_next_from_container(self):
        pass


# Uses DFS
class Blue(Algorithm):
    def __init__(self):
        super().__init__()
        self.visited = set()

    def get_path(self, state):
        start_node = Node(state, None)
        self.container = [start_node]

        while self.container:
            node = self.get_next_from_container()

            if node.state.spaceships == node.state.goals:
                return node.get_actions()

            state_key = node.state.spaceships
            if state_key in self.visited:
                continue

            self.visited.add(state_key)

            for action in reversed(node.state.get_legal_actions()):
                next_state = node.state.generate_successor_state(action)
                if next_state.spaceships not in self.visited:
                    next_node = Node(next_state, action)
                    next_node.parent = node
                    self.update_container(next_node)

        return None

    def update_container(self, node):
        self.container.append(node)

    def get_next_from_container(self):
        return self.container.pop()


# Uses BFS
class Red(Algorithm):
    def __init__(self):
        super().__init__()
        self.visited = set()

    def get_path(self, state):
        start_node = Node(state, None)
        self.container = deque([start_node])

        while self.container:
            node = self.get_next_from_container()

            if node.state.spaceships == node.state.goals:
                return node.get_actions()

            state_key = node.state.spaceships
            if state_key in self.visited:
                continue

            self.visited.add(state_key)

            for action in node.state.get_legal_actions():
                next_state = node.state.generate_successor_state(action)
                if next_state.spaceships not in self.visited:
                    next_node = Node(next_state, action)
                    next_node.parent = node
                    self.update_container(next_node)

        return None

    def update_container(self, node):
        self.container.append(node)

    def get_next_from_container(self):
        return self.container.popleft()

# Uses Branch n bound
class Black(Algorithm):

    def __init__(self):
        super().__init__()
        self.best_costs = {}

    def get_next_from_container(self):
        return heapq.heappop(self.container)

    def update_container(self, node):
        successors = self.create_successors(node, False)

        for successor in successors:
            state = successor.state
            num = state.get_state('S')
            if num in self.best_costs:
                if successor.cost >= self.best_costs[num]:
                    continue

            self.best_costs[num] = successor.cost
            heapq.heappush(self.container, successor)

# Uses A*
class White(Algorithm):
    def __init__(self):
        super().__init__()
        self.best_costs = {}

    def get_next_from_container(self):
        return heapq.heappop(self.container)

    def update_container(self, node):
        successors = self.create_successors(node, True)
        for successor in successors:
            state = successor.state
            num = state.get_state('S')
            if num in self.best_costs:
                if successor.cost >= self.best_costs[num]:
                    continue

            self.best_costs[num] = successor.cost
            heapq.heappush(self.container, successor)

class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            path.append(action)
            state = state.generate_successor_state(action)
        return path
