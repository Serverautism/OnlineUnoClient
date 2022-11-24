import pygame
import time


class WarningBox:
    def __init__(self, pos, message='this is a warning', uptime=10):
        self.pos = pos
        self.message = message
        self.uptime = uptime

        self.dead = False

        self.font = pygame.font.Font('assets/font/font.ttf', 30)

        self.colors = {
            'text': (240, 240, 240)
        }

        self.background = pygame.image.load('assets/images/warning_background.png').convert_alpha()
        self.render_surface = pygame.Surface(self.background.get_size())
        self.render_surface.set_colorkey('black')

        self.pre_render()

        self.start_time = time.time()

    def update(self):
        t = time.time() - self.start_time
        if t > self.uptime:
            self.dead = True

    def render(self, surface):
        if not self.dead:
            surface.blit(self.render_surface, self.pos)

    def pre_render(self):
        splits = []
        text = ''

        j = 0
        for i, word in enumerate(self.message.split(' ')):
            text += word + ' '
            text_render = self.font.render(text, True, self.colors['text'])

            if text_render.get_width() > self.render_surface.get_width() - 20:
                line = ''
                for item in text.split(' ')[:i - j]:
                    line += item + ' '

                splits.append(line)
                text = ''.join(text.split(' ')[i - j:]) + ' '
                j = i

        splits.append(text)

        self.render_surface.blit(self.background, (0, 0))

        x = 10
        for i, line in enumerate(splits):
            text_render = self.font.render(line, True, self.colors['text'])
            y = self.render_surface.get_height() / 2 - text_render.get_height() / 2 - text_render.get_height() * ((len(splits) - 1) / 2) + text_render.get_height() * i
            self.render_surface.blit(text_render, (x, y))
