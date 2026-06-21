import pygame
from src.entities import Enemy

class WorldManager:
    def __init__(self):
        self.rooms_bg = {
            (0, 0): (40, 40, 50), (1, 0): (70, 40, 40),
            (0, 1): (40, 70, 40), (1, 1): (70, 70, 40)
        }
        self.current_room = (0, 0)

        self.room_enemies = {
            (0, 0): pygame.sprite.Group(Enemy(300, 200)), 
            (1, 0): pygame.sprite.Group(Enemy(400, 300), Enemy(200, 400)),
            (0, 1): pygame.sprite.Group(Enemy(500, 200)), 
            (1, 1): pygame.sprite.Group(Enemy(350, 250), Enemy(600, 400))
        }

        self.room_projectiles = {
            (0, 0): pygame.sprite.Group(), 
            (1, 0): pygame.sprite.Group(), 
            (0, 1): pygame.sprite.Group(), 
            (1, 1): pygame.sprite.Group()
        }