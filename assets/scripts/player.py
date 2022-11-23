import pygame


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = 0
        self.spot = None

        self.colors = {
            '1': (54, 65, 76),
            '2': (77, 85, 97),
            '3': (81, 92, 107),
            '4': (128, 151, 189),
            '5': (179, 202, 240),
            'text': (240, 240, 240)
        }

        self.hands_images = []
        for i in range(7):
            image = pygame.image.load('assets/images/hand_{}.png'.format(i + 1)).convert_alpha()
            self.hands_images.append(image)

        self.font = pygame.font.Font('assets/font/font.ttf', 50)

        self.name_render = self.font.render(self.name, True, self.colors['text'])

    def render(self, surface):
        if self.spot:
            name_x = self.spot[0][0] - self.name_render.get_width() / 2
            name_y = self.spot[0][1]

            surface.blit(self.name_render, (name_x, name_y))

            if self.cards > 0:
                index = self.cards - 1
                if index > 6:
                    index = 6

                hand_render = self.hands_images[index]
                hand_x = self.spot[0][0] - hand_render.get_width() / 2
                hand_y = name_y + self.name_render.get_height() + 20

                surface.blit(hand_render, (hand_x, hand_y))

    def draw(self, amount):
        self.cards += amount

    def discard(self):
        self.cards -= 1
