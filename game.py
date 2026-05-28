import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Link Movement")
clock = pygame.time.Clock()

player_rect = pygame.Rect(400, 300, 40, 40)
speed = 5

active_keys = []

movement_map = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0)
}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in movement_map:
                if event.key in active_keys:
                    active_keys.remove(event.key)
                active_keys.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in active_keys:
                active_keys.remove(event.key)

    if active_keys:
        last_key = active_keys[-1]
        dx, dy = movement_map[last_key]
        
        cancel_movement = False
        for key in active_keys:
            kx, ky = movement_map[key]
            if dx == -kx and dy == -ky:
                cancel_movement = True
                break
        
        if not cancel_movement:
            player_rect.x += dx * speed
            player_rect.y += dy * speed

    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 150, 255), player_rect)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
