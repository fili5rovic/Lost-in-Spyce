import copy
import os
import threading
import time
from queue import Queue

import pygame

import config
from sprites import Spaceship, Goal, Obstacle, Empty
from state import State
from util import TimedFunction, Timeout, Logger


class Quit(Exception):
    pass


class SimulateToEnd(Exception):
    pass


class Game:
    def adjust_dimensions(self, lines):
        config.M = len(lines)
        config.N = len(lines[0].strip())
        tile_height = int(config.SCREEN_HEIGHT * 0.9 / config.M)
        tile_width = int(config.SCREEN_WIDTH * 0.9 / config.N)
        if tile_height < config.MIN_TILE_SIZE:
            raise Exception(f'ERROR: Lower the number of rows in map! '
                            f'MIN_TILE_SIZE is {config.MIN_TILE_SIZE}px but {tile_height}px occurred.')
        if tile_width < config.MIN_TILE_SIZE:
            raise Exception(f'ERROR: Lower the number of columns in map! '
                            f'MIN_TILE_SIZE is {config.MIN_TILE_SIZE}px but {tile_width}px occurred.')
        config.TILE_SIZE = int(min(config.MAX_TILE_SIZE, tile_height, tile_width))
        config.TILE_OFFSET = int(config.TILE_SIZE * config.TILE_STEP)
        self.WIDTH = config.N * config.TILE_SIZE
        self.HEIGHT = config.M * config.TILE_SIZE
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT + config.INFO_HEIGHT), flags=pygame.HIDDEN)

    def load_map(self, map_name):
        try:
            self.empty_sprites = pygame.sprite.Group()
            self.balls_sprites = pygame.sprite.Group()
            self.obstacles_sprites = pygame.sprite.Group()
            self.goals_sprites = pygame.sprite.Group()
            self.balls_map = {}

            with open(os.path.join(config.MAP_FOLDER, map_name), 'r') as file:
                lines = file.readlines()
                self.adjust_dimensions(lines)

                bit = 1
                bit_mask = (1 << (config.M * config.N)) - 1
                balls_bits = 0 & bit_mask
                obstacles_bits = 0 & bit_mask
                goals_bits = 0 & bit_mask

                for i, line in enumerate(lines):
                    for j, char in enumerate(line.strip()):
                        tile = Empty((i, j))
                        tile.add(self.empty_sprites)
                        if char != Empty.kind():
                            if char == Spaceship.kind():
                                sprite = Spaceship((i, j), self.algorithm.__class__.__name__.lower())
                                sprite.add(self.balls_sprites)
                                self.balls_map[(i, j)] = sprite
                                balls_bits |= bit
                            elif char == Obstacle.kind():
                                sprite = Obstacle((i, j))
                                sprite.add(self.obstacles_sprites)
                                obstacles_bits |= bit
                            elif char == Goal.kind():
                                sprite = Goal((i, j))
                                sprite.add(self.goals_sprites)
                                goals_bits |= bit
                            else:
                                raise Exception(f'ERROR: Illegal character {char} in map!')
                        bit <<= 1
            self.initial_state = State(bit_mask, balls_bits, obstacles_bits, goals_bits)
        except Exception as e:
            raise e

    def __init__(self, algorithm, map_name, max_time):
        self.logger = Logger()
        pygame.font.init()
        config.INFO_FONT = pygame.font.Font(os.path.join(config.FONT_FOLDER, 'info_font.ttf'), 25)
        pygame.display.set_caption('Title')
        self.WIDTH = None
        self.HEIGHT = None
        self.screen = None
        self.empty_sprites = None
        self.balls_sprites = None
        self.obstacles_sprites = None
        self.goals_sprites = None
        self.balls_map = None
        self.initial_state = None
        self.running = True
        self.playing = False
        self.done = False
        self.path = None
        self.cost = 0
        self.algorithm = algorithm
        self.max_elapsed_time = max_time
        self.load_map(map_name)
        self.clock = pygame.time.Clock()

    def get_path(self):
        elapsed_time = None
        try:
            tf_queue = Queue(1)
            tf = TimedFunction(threading.current_thread().ident,
                               tf_queue, self.max_elapsed_time,
                               self.algorithm.get_path,
                               self.initial_state
                               )
            tf.daemon = True
            tf.start()
            sleep_time = 0.001
            while tf_queue.empty():
                time.sleep(sleep_time)
            path, elapsed_time = tf_queue.get(block=False)
            return path
        except Timeout:
            raise Exception(f'Algorithm took more than {self.max_elapsed_time} seconds!')
        finally:
            if elapsed_time:
                self.logger.log_info(f'Algorithm took {elapsed_time:.3f} seconds.', to_std_out=True)

    def check_legal_path(self):
        self.path = self.get_path()
        self.cost = 0
        path = copy.copy(self.path)
        if not path:
            raise Exception(f'Path is empty!')
        state = copy.copy(self.initial_state)
        path_len = len(path)
        for step in range(path_len):
            action = path[step]
            src, dst = action
            self.logger.log_info(f'Step {(step + 1):03} - from {src} to {dst} ; '
                                 f'cost {State.get_action_cost(action)}', to_std_out=True)
            self.cost += State.get_action_cost(action)
            state = state.generate_successor_state(action)
        self.logger.log_info(f'Path length is {path_len} steps.', to_std_out=True)
        self.logger.log_info(f'Path cost is {self.cost} units.', to_std_out=True)
        if not state.is_goal_state():
            raise Exception(f'State is NOT goal!')

    def run(self):
        try:
            self.logger.log_info('Waiting for solution ...', to_std_out=True)
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT + config.INFO_HEIGHT),
                                                  flags=pygame.SHOWN)
            self.check_legal_path()
            balls_map = copy.copy(self.balls_map)
            path = copy.copy(self.path)
            state = copy.copy(self.initial_state)
            step = 0
            action = path[step]
            src, dst = action
            while self.running:
                try:
                    try:
                        if self.playing and not self.done:
                            try:
                                if not balls_map[src].move_towards(dst):
                                    balls_map[dst] = balls_map[src]
                                    del balls_map[src]
                                    state = state.generate_successor_state(action)
                                    step += 1
                                    action = path[step]
                                    src, dst = action
                            except IndexError:
                                self.done = True
                        self.draw()
                        self.events()
                        self.clock.tick(config.FRAMES_PER_SEC)
                    except SimulateToEnd:
                        balls_map = copy.copy(self.balls_map)
                        path = copy.copy(self.path)
                        state = copy.copy(self.initial_state)
                        for step in range(len(path)):
                            action = path[step]
                            src, dst = action
                            balls_map[dst] = balls_map[src]
                            balls_map[dst].place_to(dst)
                            del balls_map[src]
                            state = state.generate_successor_state(action)
                        self.playing = False
                except Quit:
                    self.running = self.playing = False
        except Exception as e:
            self.logger.log_error(repr(e))
            raise e

    def draw_info_text(self):
        self.screen.fill(config.BLACK, [0, self.HEIGHT, self.WIDTH, config.INFO_HEIGHT])
        text_str = f'{"DONE" if self.done else "" if self.playing else "PAUSED"}'
        text_width, text_height = config.INFO_FONT.size(text_str)
        text = config.INFO_FONT.render(f'{text_str}', True, config.GREEN)
        self.screen.blit(text, (self.WIDTH - text_width - config.INFO_SIDE_OFFSET, self.HEIGHT))
        pygame.display.flip()

    def draw(self):
        self.screen.fill(config.WHITE)
        self.empty_sprites.draw(self.screen)
        self.goals_sprites.draw(self.screen)
        self.obstacles_sprites.draw(self.screen)
        self.balls_sprites.draw(self.screen)
        self.draw_info_text()

    def events(self):
        # catch all events here
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.WINDOWCLOSE or \
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                raise Quit()
            if self.done:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.playing = not self.playing
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.done = True
                raise SimulateToEnd()
