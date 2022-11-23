import pygame


class Card:
    def __init__(self, color=None, number=None, action=None):
        self.color = color
        self.number = number
        self.action = action

        self.image = None

        if color or number or action:
            self.load_image()

    def from_string(self, string):
        color, number, action = string.split(':')

        if color != 'None':
            self.color = color

        if number != 'None':
            self.number = int(number)

        if action != 'None':
            self.action = action

        self.load_image()

    def load_image(self):
        if self.color:
            back = pygame.image.load('assets/images/{}_base.png'.format(self.color)).convert_alpha()

            if self.action:
                front = pygame.image.load('assets/images/{}.png'.format(self.action)).convert_alpha()
            else:
                front = pygame.image.load('assets/images/{}.png'.format(self.number)).convert_alpha()

            self.image = pygame.Surface(back.get_size())
            self.image.set_colorkey('black')
            self.image.blit(back, (0, 0))
            self.image.blit(front, (0, 0))

        else:
            self.image = pygame.image.load('assets/images/{}.png'.format(self.action)).convert_alpha()
