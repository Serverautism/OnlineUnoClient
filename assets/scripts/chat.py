import pygame
from . import menu


class Chat:
    def __init__(self):
        self.messages = []
        self.message_to_send = None

        self.colors = {
            'text': (65, 65, 65)
        }

        self.font = pygame.font.Font('assets/font/font.ttf', 30)

        self.pos = (398, 354)
        self.chat_image = pygame.image.load('assets/images/chat.png').convert_alpha()

        self.input_pos = (self.pos[0] + 15, self.pos[1] + 407)
        self.input_image = pygame.image.load('assets/images/chat_input_border.png').convert_alpha()

        self.input = menu.Input('message', self.input_pos, self.input_image)

        self.screen_dimensions = (1920, 1080)
        self.screen_width, self.screen_height = self.screen_dimensions
        self.render_dimensions = (1920, 1080)
        self.render_width, self.render_height = self.render_dimensions

        self.render_surface = pygame.Surface(self.chat_image.get_size())
        self.render_surface.set_colorkey('black')

        self.message_render_pos = (16, 83)
        self.message_render_surface = pygame.Surface((533, 320))
        self.message_render_surface.set_colorkey('black')
        self.message_render_surface.fill((238, 236, 218))

    def update(self, input):
        self.handle_input(input)

        self.input.handle_input(input)

    def render(self, surface):
        self.render_surface.blit(self.chat_image, (0, 0))
        self.render_surface.blit(self.message_render_surface, self.message_render_pos)

        surface.blit(self.render_surface, self.pos)
        self.input.render(surface)

    def handle_input(self, input):
        for event in input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                new_pos = (self.render_width * mouse_pos[0] / self.screen_width, self.render_height * mouse_pos[1] / self.screen_height)

                if event.button == 1:
                    self.input.update(new_pos)

    def pre_render(self):
        self.message_render_surface.fill((238, 236, 218))
        x = 0
        from_bottom = 0

        for message in reversed(self.messages):
            name, text = message.split(':', 1)

            name_render = self.font.render(name + ':', True, self.colors['text'])
            text_render = self.font.render(text, True, self.colors['text'])

            text_y = self.message_render_surface.get_height() - from_bottom - text_render.get_height()
            name_y = text_y - name_render.get_height()

            self.message_render_surface.blit(text_render, (x, text_y))
            self.message_render_surface.blit(name_render, (x, name_y))

            from_bottom += name_render.get_height() + text_render.get_height() + 10

    def add_message(self, message):
        self.messages.append(message)
        self.pre_render()

    def get_message_to_send(self):
        self.message_to_send = self.input.get_text()
        if self.message_to_send == '':
            self.message_to_send = None

        return self.message_to_send
