import random
from abc import abstractmethod

import config
from state import State


class Node:
    def __init__(self, state, action):
        self.state = state
        self.action = action
        self.children = []
        self.cost = 0
        self.cost_heuristic = 0
        self.parent = None

    def add_child(self, child, is_heuristic_algorithm):
        self.children.append(child)
        child.parent = self
        child.cost = child.parent.cost + State.get_action_cost(child.action)
        if is_heuristic_algorithm:
            child.cost_heuristic = child.parent.cost_heuristic + self.calc_heuristic(child.state)
            print(child.cost_heuristic)
    def get_parents(self):
        parents = []
        current = self
        while current.parent:
            parents.append(current.parent)
            current = current.parent
        return reversed(parents)

    def get_actions(self):
        actions = []
        for parent in self.get_parents():
            if parent.action is None:
                continue
            actions.append(parent.action)
        actions.append(self.action)
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


    def get_coordinates(self,decimal_number):
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
        self._is_heuristic = False

    def get_path(self, state):
        self.container = [Node(state, None)]
        while self.container:
            node = self.get_next_from_container()
            if node.state.is_goal_state():
                return node.get_actions()
            else:
                self.update_container(node)
        return None

    def create_successors(self, node):
        successors = []

        for legal_action in node.state.get_legal_actions():
            next_state = node.state.generate_successor_state(legal_action)

            if node.state_exists_in_parents(next_state):
                continue

            next_node = Node(next_state, legal_action)
            node.add_child(next_node, self._is_heuristic)
            successors.append(next_node)
        return successors

    @abstractmethod
    def update_container(self, node):
        pass

    @abstractmethod
    def get_next_from_container(self):
        pass




# Uses DFS
class Blue(Algorithm):

    # we need to reverse it, because of stack
    def update_container(self, node):
        self.container = self.container + list(reversed(self.create_successors(node)))

    # since stack is used, we pop the element
    def get_next_from_container(self):
        return self.container.pop()


# Uses BFS
class Red(Algorithm):

    def update_container(self, node):
        self.container = self.container + self.create_successors(node)

    # since queue is used, we get the first element
    def get_next_from_container(self):
        return self.container.pop(0)

# Uses Branch n bound
class Black(Algorithm):

    def __init__(self):
        super().__init__()
        self.best_costs = {}

    def get_next_from_container(self):
        return self.container.pop(0)

    def update_container(self, node):
        self.dynamically_add_successors(node)
        self.container.sort(key=lambda node1: node1.cost)

    def dynamically_add_successors(self, node):
        successors = self.create_successors(node)

        for successor in successors:
            state = successor.state
            num = state.get_state('S')
            if num in self.best_costs:
                if successor.cost >= self.best_costs[num]:
                    continue

            self.best_costs[num] = successor.cost
            self.container.append(successor)


# Uses A*
class White(Algorithm):

    def __init__(self):
        super().__init__()
        self.best_costs = {}
        _is_heuristic = True

    def get_next_from_container(self):
        return self.container.pop(0)

    def update_container(self, node):
        self.container.extend(self.create_successors(node))
        self.container.sort(key=lambda node1: node1.cost + node1.cost_heuristic)

    def dynamically_add_successors(self, node):
        successors = self.create_successors(node)
        for successor in successors:
            state = successor.state
            num = state.get_state('S')
            if num in self.best_costs:
                if successor.cost >= self.best_costs[num]:
                    continue

            self.best_costs[num] = successor.cost + successor.cost_heuristic
            self.container.append(successor)


class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            path.append(action)
            state = state.generate_successor_state(action)
        return path
