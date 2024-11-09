import random
from abc import abstractclassmethod, abstractmethod

from state import State


class Node:
    def __init__(self, state, action):
        self.state = state
        self.action = action
        self.children = []
        self.cost = 0
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        child.cost = child.parent.cost + State.get_action_cost(child.action)

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
            if (parent.action == None):
                continue
            actions.append(parent.action)
        actions.append(self.action)
        return actions

    def state_exists_in_parents(self, state):
        parent_node = self
        while parent_node is not None:
            if parent_node.state == state:
                return True
            parent_node = parent_node.parent
        return False


class Algorithm:
    container = []

    def get_path(self, state):
        self.container = [Node(state, None)]
        while self.container:
            node = self.get_next_from_container()
            if node.state.is_goal_state():
                return node.get_actions()
            else:
                self.update_container(node)
        return None

    @abstractmethod
    def update_container(self, node):
        pass

    @abstractmethod
    def get_next_from_container(self):
        pass

    @abstractmethod
    def create_successors(self, node):
        pass


class Blue(Algorithm):
    # if it's not goal state, create successors for given node
    def create_successors(self, node):
        successors = []
        for legal_action in reversed(node.state.get_legal_actions()):
            next_state = node.state.generate_successor_state(legal_action)

            if node.state_exists_in_parents(next_state):
                continue

            next_node = Node(next_state, legal_action)
            node.add_child(next_node)
            successors.append(next_node)
        return successors

    # successors are added before the others
    def update_container(self, node):
        self.container.extend(self.create_successors(node))

    # since stack is used, we pop the element
    def get_next_from_container(self):
        return self.container.pop()


class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            path.append(action)
            state = state.generate_successor_state(action)
        return path
