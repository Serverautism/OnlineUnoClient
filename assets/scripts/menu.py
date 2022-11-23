import pygame
import string


class Button:
    def __init__(self, pos, image):
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        self.pressed = False

    def update(self, mouse_press):
        if self.rect.collidepoint(mouse_press):
            self.pressed = True
        else:
            self.pressed = False

    def render(self, surface):
        surface.blit(self.image, self.rect)

    def get_pressed(self):
        if self.pressed:
            self.pressed = False
            return True
        else:
            return False

    def set_pos(self, pos):
        if pos != self.pos:
            self.pos = pos
            self.rect.topleft = self.pos


class Input:
    def __init__(self, sample_text, pos, image):
        self.sample_text = sample_text
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos

        self.active = False
        self.text = ''

        self.allowed_symbols = string.ascii_letters + string.digits + 'ßÜüÖöÄä#+-_,;!?:()= '

        self.colors = {
            'text_preset': (130, 130, 130),
            'text': (65, 65, 65)
        }

        self.font = pygame.font.Font('assets/font/font.ttf', 30)

        self.render_surface = pygame.Surface((self.rect.width, self.rect.height))
        self.render_surface.set_colorkey('black')

        self.pre_render()

    def update(self, mouse_press):
        if self.rect.collidepoint(mouse_press):
            self.active = True
        else:
            self.active = False

    def handle_input(self, input):
        if self.active:
            got_input = False
            for event in input:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        if self.text != '':
                            self.text = self.text[:-1]
                            got_input = True
                    elif event.key == pygame.K_RETURN:
                        self.active = False
                    else:
                        if event.unicode in self.allowed_symbols:
                            self.text += event.unicode
                            got_input = True

            if got_input:
                self.pre_render()

    def render(self, surface):
        surface.blit(self.render_surface, self.rect)

    def pre_render(self):
        self.render_surface.fill('black')
        self.render_surface.blit(self.image, (0, 0))

        if self.text != '':
            text_render = self.font.render(self.text, True, self.colors['text'])

            if text_render.get_width() > self.image.get_width() - 20:
                self.text = self.text[:-1]
                text_render = self.font.render(self.text, True, self.colors['text'])

            text_x = 10
            text_y = self.rect.height / 2 - text_render.get_height() / 2
        else:
            text_render = self.font.render(self.sample_text, True, self.colors['text_preset'])
            text_x = 10
            text_y = self.rect.height / 2 - text_render.get_height() / 2

        self.render_surface.blit(text_render, (text_x, text_y))

    def get_text(self):
        text = self.text
        self.text = ''
        self.pre_render()
        return text
