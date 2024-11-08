import os

import screeninfo

monitor = screeninfo.get_monitors()[0]

# parameters
M = None
N = None
SCREEN_WIDTH = monitor.width
SCREEN_HEIGHT = monitor.height
MIN_TILE_SIZE = 32
TILE_SIZE = 64
MAX_TILE_SIZE = 128
TILE_STEP = 0.05
TILE_OFFSET = None
INFO_FONT = None
INFO_HEIGHT = 30
INFO_SIDE_OFFSET = 10
FRAMES_PER_SEC = 120

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (192, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)

# paths
GAME_FOLDER = os.path.dirname(__file__)
MAP_FOLDER = os.path.join(GAME_FOLDER, 'maps')
IMG_FOLDER = os.path.join(GAME_FOLDER, 'img')
LOG_FOLDER = os.path.join(GAME_FOLDER, 'logs')
FONT_FOLDER = os.path.join(GAME_FOLDER, 'fonts')
