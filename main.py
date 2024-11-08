import sys
import traceback

import pygame

from game import Game

try:
    module_algorithms = __import__('algorithms')
    algorithm = getattr(module_algorithms, sys.argv[1] if len(sys.argv) > 1 else 'ExampleAlgorithm')
    map_filename = sys.argv[2] if len(sys.argv) > 2 else 'example_map.txt'
    max_elapsed_time = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    g = Game(algorithm(), map_filename, max_elapsed_time)
    g.run()
except (Exception,):
    traceback.print_exc()
    input()
finally:
    pygame.display.quit()
    pygame.quit()
