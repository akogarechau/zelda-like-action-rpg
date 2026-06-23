import pygame
from src.entities import Enemy, Shooter, Driller, Wall
from src.settings import WIDTH, HEIGHT, WALL_SIZE

class WorldManager:
    def __init__(self, assets):
        self.assets = assets
        base_color = (200, 160, 110)
        self.rooms_bg = {
            (0, 0): base_color, (1, 0): base_color,
            (0, 1): base_color, (1, 1): base_color
        }
        self.current_room = (0, 0)
        self.secret_door_opened = False 

        self.room_enemies = {
            (0, 0): pygame.sprite.Group(), 
            (1, 0): pygame.sprite.Group(Enemy(400, 300, self.assets), Enemy(200, 400, self.assets)),
            (0, 1): pygame.sprite.Group(Enemy(500, 200, self.assets), Enemy(300, 400, self.assets)), 
            (1, 1): pygame.sprite.Group(Shooter(350, 250, self.assets), Shooter(500, 500, self.assets), Driller(250,500, self.assets), Driller(600, 400, self.assets))
        }

        self.room_projectiles = {
            (0, 0): pygame.sprite.Group(), 
            (1, 0): pygame.sprite.Group(), 
            (0, 1): pygame.sprite.Group(), 
            (1, 1): pygame.sprite.Group()
        }
        
        self.room_walls = {
            (0, 0): self._generate_walls((0, 0)),
            (1, 0): self._generate_walls((1, 0)),
            (0, 1): self._generate_walls((0, 1)),
            (1, 1): self._generate_walls((1, 1))
        }

    def is_cleared(self):
        total_enemies = sum(len(group) for group in self.room_enemies.values())
        return total_enemies == 0

    def _generate_walls(self, room, secret_door=False):
        group = pygame.sprite.Group()
        W = WALL_SIZE
        img = self.assets['wall']
        
        top_door = None
        bottom_door = None
        left_door = None
        right_door = None
        
        if room == (0, 0):
            bottom_door = (340, 460)
            right_door = (240, 360)
        elif room == (1, 0):
            left_door = (240, 360)
            bottom_door = (600, 720)
        elif room == (0, 1):
            top_door = (340, 460)
            right_door = (400, 520)
        elif room == (1, 1):
            top_door = (600, 720)
            left_door = (400, 520)
            if secret_door:
                right_door = (240, 360) 
            
        if top_door:
            group.add(Wall(0, 0, top_door[0], W, img))
            group.add(Wall(top_door[1], 0, WIDTH - top_door[1], W, img))
        else:
            group.add(Wall(0, 0, WIDTH, W, img))
            
        if bottom_door:
            group.add(Wall(0, HEIGHT - W, bottom_door[0], W, img))
            group.add(Wall(bottom_door[1], HEIGHT - W, WIDTH - bottom_door[1], W, img))
        else:
            group.add(Wall(0, HEIGHT - W, WIDTH, W, img))
            
        if left_door:
            group.add(Wall(0, 0, W, left_door[0], img))
            group.add(Wall(0, left_door[1], W, HEIGHT - left_door[1], img))
        else:
            group.add(Wall(0, 0, W, HEIGHT, img))
            
        if right_door:
            group.add(Wall(WIDTH - W, 0, W, right_door[0], img))
            group.add(Wall(WIDTH - W, right_door[1], W, HEIGHT - right_door[1], img))
        else:
            group.add(Wall(WIDTH - W, 0, W, HEIGHT, img))
            
        return group
