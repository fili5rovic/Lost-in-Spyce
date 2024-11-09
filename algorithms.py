import random


class Node:
    def __init__(self, state, action):
        self.state = state
        self.action = action
        self.children = []
        self.cost = 0
        self.parent = None


    def add_child(self, child):
        self.children.insert(0, child)
        child.parent = self
        child.cost = child.parent.cost + 0


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
            if(parent.action == None):
                continue
            actions.append(parent.action)
        actions.append(self.action)
        return actions


class Algorithm:
    def get_path(self, state):
        pass


class ExampleAlgorithm(Algorithm):
    def get_path(self, state):
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            path.append(action)
            state = state.generate_successor_state(action)
        return path


class Blue(Algorithm):
    def get_path(self, state):
        stack = [Node(state, None)]
        while len(stack) > 0:
            node = stack.pop(0)
            if node.state.is_goal_state():
                return node.get_actions()
            else:
                successors = []
                for legal_action in node.state.get_legal_actions():
                    next_state = node.state.generate_successor_state(legal_action)

                    if self.already_exists_in_parents(next_state, node):
                        continue

                    next_node = Node(next_state, legal_action)
                    node.add_child(next_node)
                    successors.append(next_node)
                stack = successors + stack
        return None

    def already_exists_in_parents(self, next_state, parent_node):
        while parent_node is not None:
            if parent_node.state == next_state:
                return True
            parent_node = parent_node.parent
        return False
