import pygame
import random
from assets.scripts import scenes


class Game:
    def __init__(self):
        pygame.init()

        self.running = True

        self.fps = 60
        self.clock = pygame.time.Clock()

        self.screen_dimensions = (1920, 1080)
        self.screen_width, self.screen_height = self.screen_dimensions
        self.screen = pygame.display.set_mode(self.screen_dimensions)
        pygame.display.set_caption('Uno')

        self.render_dimensions = (1920, 1080)
        self.render_width, self.render_height = self.render_dimensions
        self.render_surface = pygame.Surface(self.render_dimensions)
        self.render_surface.set_colorkey('black')

        self.input = None

        self.active_scene = scenes.MainMenuScene()

    def run(self):
        while self.running:
            self.clock.tick(self.fps)

            self.handle_input()

            self.active_scene.update(self.input)
            self.active_scene.render(self.render_surface)

            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen_dimensions), (0, 0))
            pygame.display.update()

            if self.active_scene.next_scene:
                self.active_scene = self.active_scene.next_scene

    def handle_input(self):
        self.input = pygame.event.get()
        for event in self.input:
            if event.type == pygame.QUIT:
                self.running = False
                self.active_scene.close()


if __name__ == '__main__':
    game = Game()
    game.run()
