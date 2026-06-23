import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def get_image(self, x, y, width, height, scale, color_key=None):
        image = pygame.Surface((width, height)).convert()
        
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        
        if color_key is not None:
            image.set_colorkey(color_key)
            
        target_w = int(width * (scale / 16))
        target_h = int(height * (scale / 16))
        image = pygame.transform.scale(image, (target_w, target_h))
        
        return image
