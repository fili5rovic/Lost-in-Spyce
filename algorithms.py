import random


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
        path = []
        while not state.is_goal_state():
            possible_actions = state.get_legal_actions()
            print(possible_actions)
            action = possible_actions[random.randint(0, len(possible_actions) - 1)]
            print(action)
            path.append(action)
            state = state.generate_successor_state(action)
        return path
