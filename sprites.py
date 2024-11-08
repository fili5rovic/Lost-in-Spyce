import os
from random import randint

import pygame

import config


class BaseSprite(pygame.sprite.Sprite):
    images_dict = {}

    def __init__(self, position, size, image_name=None, offset=(0, 0)):
        super().__init__()
        if image_name is None:
            image_name = f'{self.__class__.__name__.lower()}.png'
        if image_name in BaseSprite.images_dict:
            image = BaseSprite.images_dict[image_name]
        else:
            image = pygame.image.load(os.path.join(config.IMG_FOLDER, image_name)).convert()
            image = pygame.transform.scale(image, size)
            image.set_colorkey(config.WHITE)
            BaseSprite.images_dict[image_name] = image
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = (position[1] * config.TILE_SIZE + offset[1], position[0] * config.TILE_SIZE + offset[0])

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    @staticmethod
    def kind():
        pass


class Spaceship(BaseSprite):
    def __init__(self, position, algo_name):
        super().__init__(position, (config.TILE_SIZE, config.TILE_SIZE),
                         f'{self.__class__.__name__.lower()}_{algo_name}.png')

    def move_towards(self, destination):
        if self.rect.y - destination[0] * config.TILE_SIZE > config.TILE_OFFSET:
            self.rect.y -= config.TILE_OFFSET
        elif destination[1] * config.TILE_SIZE - self.rect.x > config.TILE_OFFSET:
            self.rect.x += config.TILE_OFFSET
        elif destination[0] * config.TILE_SIZE - self.rect.y > config.TILE_OFFSET:
            self.rect.y += config.TILE_OFFSET
        elif self.rect.x - destination[1] * config.TILE_SIZE > config.TILE_OFFSET:
            self.rect.x -= config.TILE_OFFSET
        else:
            self.rect.y, self.rect.x = destination[0] * config.TILE_SIZE, destination[1] * config.TILE_SIZE
            return False
        return True

    def place_to(self, destination):
        self.rect.y, self.rect.x = destination[0] * config.TILE_SIZE, destination[1] * config.TILE_SIZE

    @staticmethod
    def kind():
        return 'S'


class Obstacle(BaseSprite):
    def __init__(self, position):
        super().__init__(position, (config.TILE_SIZE, config.TILE_SIZE))

    @staticmethod
    def kind():
        return 'O'


class Goal(BaseSprite):
    def __init__(self, position):
        super().__init__(position, (config.TILE_SIZE, config.TILE_SIZE))

    @staticmethod
    def kind():
        return 'G'


class Empty(BaseSprite):
    def __init__(self, position):
        super().__init__(position, (config.TILE_SIZE, config.TILE_SIZE),
                         f'{self.__class__.__name__.lower()}{randint(0, 7)}.png')

    @staticmethod
    def kind():
        return '_'
