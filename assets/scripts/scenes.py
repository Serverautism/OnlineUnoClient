import pygame
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import random
from . import menu, cards, player, chat


class MainMenuScene:
    def __init__(self):
        self.screen_dimensions = (1920, 1080)
        self.screen_width, self.screen_height = self.screen_dimensions
        self.render_dimensions = (1920, 1080)
        self.render_width, self.render_height = self.render_dimensions
        self.render_surface = pygame.Surface(self.render_dimensions)
        self.render_surface.set_colorkey('black')

        self.next_scene = None

        self.colors = {
            '1': (54, 65, 76),
            '2': (77, 85, 97),
            '3': (81, 92, 107),
            '4': (128, 151, 189),
            '5': (179, 202, 240)
        }

        # ui elements
        self.background_image = pygame.transform.scale(pygame.image.load('assets/images/background.png'), self.render_dimensions)
        self.title_image = pygame.image.load('assets/images/logo.png').convert_alpha()
        self.title_pos = (self.render_width / 2 - self.title_image.get_width() / 2, 50)
        self.join_button = menu.Button((self.render_width / 2 - 359 - 40, self.render_height * .65), pygame.image.load('assets/images/join_game.png').convert_alpha())
        self.create_button = menu.Button((self.render_width / 2 + 40, self.render_height * .65), pygame.image.load('assets/images/create_game.png').convert_alpha())
        self.ui_elements = [self.join_button, self.create_button]

    def update(self, input):
        self.handle_input(input)

        self.render_surface.fill(self.colors['1'])
        # self.render_surface.blit(self.background_image, (0, 0))
        self.render_surface.blit(self.title_image, self.title_pos)

        for element in self.ui_elements:
            element.render(self.render_surface)

        if self.join_button.get_pressed():
            self.next_scene = SelectGameScene()

        elif self.create_button.get_pressed():
            self.next_scene = MainScene()

    def handle_input(self, input):
        for event in input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                new_pos = (self.render_width * mouse_pos[0] / self.screen_width, self.render_height * mouse_pos[1] / self.screen_height)
                for item in self.ui_elements:
                    item.update(new_pos)

    def render(self, surface):
        surface.blit(self.render_surface, (0, 0))

    def close(self):
        pass


class MainScene:
    def __init__(self, port=None):
        self.connected = True

        self.screen_dimensions = (1920, 1080)
        self.screen_width, self.screen_height = self.screen_dimensions
        self.render_dimensions = (1920, 1080)
        self.render_width, self.render_height = self.render_dimensions
        self.render_surface = pygame.Surface(self.render_dimensions)
        self.render_surface.set_colorkey('black')

        self.next_scene = None

        self.colors = {
            '1': (54, 65, 76),
            '2': (77, 85, 97),
            '3': (81, 92, 107),
            '4': (128, 151, 189),
            '5': (179, 202, 240)
        }

        with open('assets/data/name.txt', 'r') as f:
            self.name = f.read()
            print('loaded name {} from file'.format(self.name))

        self.start_image = pygame.image.load('assets/images/start.png').convert_alpha()
        start_button_pos = (self.render_width / 2 - self.start_image.get_width() / 2, self.render_height - self.start_image.get_height() - 20)
        self.start_button = menu.Button(start_button_pos, self.start_image)

        deck_image = pygame.image.load('assets/images/deck.png').convert_alpha()
        deck_pos = (1335, 480)
        self.deck = menu.Button(deck_pos, deck_image)

        self.discard_pos = (1015, 447)
        self.discard_render = pygame.Surface((314, 258))
        self.discard_render.set_colorkey('black')

        self.last_discard = ''

        self.chat = chat.Chat()

        self.direction_image_ac = pygame.image.load('assets/images/direction.png').convert_alpha()
        self.direction_image_c = pygame.transform.flip(self.direction_image_ac, False, True)
        self.direction_pos = (1021, 319)
        self.direction_center = (self.direction_pos[0] + self.direction_image_ac.get_width() / 2, self.direction_pos[1] + self.direction_image_ac.get_height() / 2)
        self.direction_rotation = 0
        self.rotation_speed = 1

        self.other_turn_image = pygame.image.load('assets/images/other_player_border.png').convert_alpha()
        self.my_turn_image = pygame.image.load('assets/images/my_turn.png').convert_alpha()

        wish_red_pos = (1677, 893)
        wish_red_image = pygame.image.load('assets/images/wish_red.png').convert_alpha()
        self.wish_red = menu.Button(wish_red_pos, wish_red_image)
        wish_blue_pos = (wish_red_pos[0] + wish_red_image.get_width(), wish_red_pos[1])
        wish_blue_image = pygame.image.load('assets/images/wish_blue.png').convert_alpha()
        self.wish_blue = menu.Button(wish_blue_pos, wish_blue_image)
        wish_green_pos = (wish_blue_pos[0], wish_red_pos[1] + wish_blue_image.get_height())
        wish_green_image = pygame.image.load('assets/images/wish_green.png').convert_alpha()
        self.wish_green = menu.Button(wish_green_pos, wish_green_image)
        wish_yellow_pos = (wish_red_pos[0], wish_red_pos[1] + wish_red_image.get_height())
        wish_yellow_image = pygame.image.load('assets/images/wish_yellow.png').convert_alpha()
        self.wish_yellow = menu.Button(wish_yellow_pos, wish_yellow_image)

        self.player_spots = [
            [(190, 490), 90],
            [(200, 100), 70],
            [(580, 18), 0],
            [(960, 10), 0],
            [(1340, 18), 0],
            [(1720, 100), -70],
            [(1730, 490), -90]
        ]

        self.is_host = False
        self.game_started = False

        self.players = []
        self.id = None

        self.cards = []
        self.discarded_cards = []
        self.last_discard_len = 0

        self.turn = -1
        self.made_turn = False
        self.wished_color = None
        self.can_wish = False
        self.has_wished = False
        self.clockwise = True
        self.discard_on_drawcard = False

        # network stuff
        with open('assets/data/host.txt', 'r') as f:
            self.host = f.read()

        self.bufsiz = 1024

        if port:
            self.port = port
            self.adr = (self.host, self.port)

            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.adr)
            print('connected to game server on port {}...'.format(self.port))

        else:
            self.port = 33000
            self.adr = (self.host, self.port)

            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.adr)
            print('connected to MAIN game server...')

            self.create_game()

            print('created new game on port {}'.format(self.port))

            self.adr = (self.host, self.port)

            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_socket.connect(self.adr)

            print('connected to NEW game server...')

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        pygame.display.set_caption('session {}'.format(self.port))

        self.send(self.name)

    def receive(self):
        while True:
            try:
                msg = self.client_socket.recv(self.bufsiz)
                text_msg = msg.decode('utf8')
                # print(text_msg)
                commands = text_msg.split('\0')[:-1]

                for command in commands:
                    if command == 'host':
                        if self.is_host:
                            self.is_host = False
                        else:
                            self.is_host = True

                    elif command == 'start':
                        self.game_started = True
                        print('host started the game...')

                    elif command == 'reverse':
                        if self.clockwise:
                            self.clockwise = False
                        else:
                            self.clockwise = True

                    elif command == 'wish':
                        if self.can_wish:
                            self.can_wish = False
                            print('no more color can be wished..')
                        else:
                            self.can_wish = True
                            print('a color can be wished..')

                        self.has_wished = False

                    elif command.startswith('win'):
                        self.reset()
                        id = int(command.split(',')[1])
                        if id != self.id:
                            print('player {} won!'.format(self.players[id].name))
                        else:
                            print('I won!!!')

                    elif command.startswith('wish'):
                        color = command.split(',')[1]

                        if color == 'None':
                            self.wished_color = None
                            print('wished color reset...')

                        else:
                            self.wished_color = color
                            print('the player wished {}...'.format(color))

                    elif command.startswith('players'):
                        players = command.split(',')[1:]

                        if len(self.players) == 0:
                            self.id = len(players) - 1
                            print('my id is {}...'.format(self.id))

                        for p in players:
                            self.players.append(player.Player(p))

                        print('list of all players in this game:\n{}'.format([p.name for p in self.players]))
                        self.distribute_spots()

                    elif command.startswith('join'):
                        p = command.split(',', 1)[1]
                        p = player.Player(p)
                        self.players.append(p)
                        print('player {} joined this game...'.format(p.name))
                        self.distribute_spots()

                    elif command.startswith('disconnect'):
                        id = int(command.split(',')[1])
                        print('player {} disconnected...'.format(self.players[id].name))

                        if id < self.id:
                            self.id -= 1
                            print('new id due to disconnect of {} is {}...'.format(self.players[id].name, self.id))

                        self.players.pop(id)
                        self.distribute_spots()

                    elif command.startswith('draws'):
                        id, amount = command.split(',')[1:]
                        if int(id) != self.id:
                            print('player {} draws {} cards...'.format(self.players[int(id)].name, amount))
                            self.players[int(id)].draw(int(amount))

                        if len(self.discarded_cards) > 0:
                            if self.discarded_cards[-1].action == 'drawtwo' or self.discarded_cards[-1].action == 'wilddrawfour':
                                self.discard_on_drawcard = True

                    elif command.startswith('draw'):
                        c = command.split(',')[1:]
                        for card in c:
                            new_card = cards.Card()
                            new_card.from_string(card)
                            new_button = menu.Button((0, 0), new_card.image)
                            self.cards.append((new_card, new_button))
                            print('I draw {}...'.format(card))

                    elif command.startswith('discard'):
                        player_id, card = command.split(',')[1:]
                        if int(player_id) == -1:
                            pass
                        else:
                            self.players[int(player_id)].discard()

                        c = cards.Card()
                        c.from_string(card)
                        self.discarded_cards.append(c)

                        if c.action == 'drawtwo' or c.action == 'wilddrawfour':
                            self.discard_on_drawcard = False

                        print('{} got discarded...'.format(card))

                    elif command.startswith('turn'):
                        id = command.split(',')[1]
                        self.turn = int(id)
                        if self.turn == self.id:
                            print('its my turn...')
                            self.made_turn = False
                        else:
                            print('its {} turn...'.format(self.players[self.turn].name))

                    elif command.startswith('message'):
                        message = command.split(',', 1)[1]
                        self.chat.add_message(message)

            except OSError:
                break

    def send(self, msg):
        msg += '\0'
        self.client_socket.send(bytes(msg, 'utf8'))
        if msg == '{quit}\0':
            self.client_socket.close()
            self.connected = False

    def update(self, input):
        self.handle_input(input)

        self.chat.update(input)

        if self.turn == self.id and not self.made_turn:
            for card, button in self.cards:
                if button.get_pressed() and self.check_turn(card):
                    self.send('discard,{},{}:{}:{}'.format(self.id, card.color, card.number, card.action))
                    self.cards.remove((card, button))

                    if len(self.cards) == 0:
                        self.send('win,{}'.format(self.id))

                    break

        self.render_surface.fill(self.colors['1'])

        self.update_start_button()

        self.chat.render(self.render_surface)

        self.update_card_deck()
        self.render_discard_pile()
        self.render_direction()

        self.render_players()
        self.render_turn_indication()

        self.render_wish_buttons()

        self.render_cards()

    def handle_input(self, input):
        for event in input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                new_pos = (self.render_width * mouse_pos[0] / self.screen_width, self.render_height * mouse_pos[1] / self.screen_height)

                if event.button == 1:
                    if self.is_host and not self.game_started:
                        self.start_button.update(new_pos)

                    if self.game_started:
                        if self.turn == self.id and not self.made_turn:
                            for item in self.cards:
                                item[1].update(new_pos)

                            self.deck.update(new_pos)

                    if self.turn == self.id and self.can_wish and not self.has_wished:
                        self.wish_red.update(new_pos)
                        self.wish_blue.update(new_pos)
                        self.wish_green.update(new_pos)
                        self.wish_yellow.update(new_pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    message = self.chat.get_message_to_send()
                    if message:
                        self.send('message,{}:{}'.format(self.name, message))

    def render(self, surface):
        surface.blit(self.render_surface, (0, 0))

    def update_start_button(self):
        if self.is_host and not self.game_started:
            self.start_button.render(self.render_surface)
            if self.start_button.get_pressed() and len(self.players) > 1:
                self.send('start')
                self.game_started = True

    def distribute_spots(self):
        if len(self.players) > 1:
            for i, p in enumerate(self.players):
                x = i
                if i >= self.id:
                    x -= 1
                index = x - self.id
                p.spot = self.player_spots[index]

    def render_players(self):
        for i, p in enumerate(self.players):
            if i != self.id:
                p.render(self.render_surface)

    def render_turn_indication(self):
        if self.game_started and self.turn > -1:
            if self.turn == self.id:
                y = self.render_height - self.my_turn_image.get_height()
                self.render_surface.blit(self.my_turn_image, (0, y))
            else:
                pos = self.players[self.turn].spot[0]
                x = pos[0] - self.other_turn_image.get_width() / 2
                y = pos[1] - 10
                self.render_surface.blit(self.other_turn_image, (x, y))

    def render_discard_pile(self):
        if self.last_discard_len != len(self.discarded_cards):
            self.last_discard_len = len(self.discarded_cards)
            image = pygame.transform.rotate(self.discarded_cards[-1].image, random.randint(0, 360))
            x = self.discard_render.get_width() / 2 - image.get_width() / 2
            y = self.discard_render.get_height() / 2 - image.get_height() / 2
            self.discard_render.blit(image, (x, y))

        self.render_surface.blit(self.discard_render, self.discard_pos)

    def render_direction(self):
        if self.game_started:
            if self.clockwise:
                self.direction_rotation -= self.rotation_speed
                if self.direction_rotation < -360:
                    self.direction_rotation += 360

                new_render = pygame.transform.rotate(self.direction_image_c, self.direction_rotation)
                x = self.direction_center[0] - new_render.get_width() / 2
                y = self.direction_center[1] - new_render.get_height() / 2

            else:
                self.direction_rotation += self.rotation_speed
                if self.direction_rotation > 360:
                    self.direction_rotation -= 360

                new_render = pygame.transform.rotate(self.direction_image_ac, self.direction_rotation)
                x = self.direction_center[0] - new_render.get_width() / 2
                y = self.direction_center[1] - new_render.get_height() / 2

            self.render_surface.blit(new_render, (x, y))

    def render_wish_buttons(self):
        if self.turn == self.id and self.can_wish and not self.has_wished:
            self.wish_red.render(self.render_surface)
            if self.wish_red.get_pressed():
                self.send('wish,red')
                self.has_wished = True

            self.wish_blue.render(self.render_surface)
            if self.wish_blue.get_pressed():
                self.send('wish,blue')
                self.has_wished = True

            self.wish_green.render(self.render_surface)
            if self.wish_green.get_pressed():
                self.send('wish,green')
                self.has_wished = True

            self.wish_yellow.render(self.render_surface)
            if self.wish_yellow.get_pressed():
                self.send('wish,yellow')
                self.has_wished = True

    def render_cards(self):
        if self.game_started and len(self.cards) > 0:
            for i, item in enumerate(self.cards):
                card, button = item
                x = (self.render_width / 2 - (len(self.cards) / 2) * (card.image.get_width() + 20)) + i * (card.image.get_width() + 20)
                y = self.render_height - card.image.get_height() - 30
                self.render_surface.blit(card.image, (x, y))
                button.set_pos((x, y))

    def update_card_deck(self):
        self.deck.render(self.render_surface)

        if self.game_started and self.turn == self.id:
            if self.deck.get_pressed():
                self.send('draw')

    def check_turn(self, card):
        last_card = self.discarded_cards[-1]

        if last_card.color:
            if card.action == 'wilddrawfour':
                return True

            # color action card
            if last_card.action:
                if card.action == last_card.action:
                    return True

                if last_card.action != 'drawtwo' or self.discard_on_drawcard:
                    if card.color == last_card.color or card.action == 'wild':
                        return True

            # normal number card
            else:
                if card.number == last_card.number:
                    return True

                if card.color == last_card.color:
                    return True

                if card.action == 'wild':
                    return True

        # action card without color
        else:
            if self.wished_color:
                if card.action == 'wilddrawfour':
                    return True

                # wild card
                if last_card.action == 'wild':
                    if card.color == self.wished_color:
                        return True

                    if card.action == 'wild':
                        return True

                # wild draw four card
                else:
                    if self.discard_on_drawcard and card.color == self.wished_color:
                        return True

                    elif self.discard_on_drawcard and card.action == 'wild':
                        return True

                    elif card.action == 'drawtwo' and card.color == self.wished_color:
                        return True

        return False

    def reset(self):
        self.game_started = False
        self.discarded_cards.clear()
        self.cards.clear()
        self.last_discard_len = 0
        self.turn = -1
        self.made_turn = False
        self.wished_color = None
        self.can_wish = False
        self.has_wished = False
        self.clockwise = True
        self.discard_on_drawcard = False

        self.discard_render = pygame.Surface((314, 258))
        self.discard_render.set_colorkey('black')

        for player in self.players:
            player.cards = 0

        print('game reset done...')

    def create_game(self):
        self.send(self.name + '\0create')
        self.port = int(self.client_socket.recv(self.bufsiz).decode("utf8"))
        self.client_socket.close()

    def close(self):
        if self.connected:
            self.send('{quit}')


class SelectGameScene:
    def __init__(self):
        self.connected = True

        self.screen_dimensions = (1920, 1080)
        self.screen_width, self.screen_height = self.screen_dimensions
        self.render_dimensions = (1920, 1080)
        self.render_width, self.render_height = self.render_dimensions
        self.render_surface = pygame.Surface(self.render_dimensions)
        self.render_surface.set_colorkey('black')

        self.next_scene = None

        self.colors = {
            '1': (54, 65, 76),
            '2': (77, 85, 97),
            '3': (81, 92, 107),
            '4': (128, 151, 189),
            '5': (179, 202, 240),
            'text': (240, 240, 240)
        }

        with open('assets/data/name.txt', 'r') as f:
            self.name = f.read()
            print('loaded name {} from file'.format(self.name))

        self.font = pygame.font.Font('assets/font/font.ttf', 70)

        self.title_image = pygame.image.load('assets/images/logo.png').convert_alpha()
        self.title_pos = (self.render_width / 2 - self.title_image.get_width() / 2, 50)
        self.game_borders = [
            pygame.image.load('assets/images/select_game_border_0.png').convert_alpha(),
            pygame.image.load('assets/images/select_game_border_1.png').convert_alpha(),
            pygame.image.load('assets/images/select_game_border_2.png').convert_alpha(),
            pygame.image.load('assets/images/select_game_border_3.png').convert_alpha(),
            pygame.image.load('assets/images/select_game_border_4.png').convert_alpha()
            ]
        self.refresh_image = pygame.image.load('assets/images/refresh.png').convert_alpha()
        refresh_pos = (self.render_width - self.refresh_image.get_width() - 30, self.render_height - self.refresh_image.get_height() - 30)
        self.refresh_button = menu.Button(refresh_pos, self.refresh_image)

        self.games_list_buttons = []
        self.games_list_offset = 0

        self.available_games_list_pos = (self.render_width / 2 - self.game_borders[0].get_width() / 2, self.title_pos[1] + self.title_image.get_height() + 50)
        self.available_games_render = pygame.Surface((self.game_borders[0].get_width(), self.render_height - self.available_games_list_pos[1] - 30))
        self.available_games_render.set_colorkey('black')

        self.available_games_rect = self.available_games_render.get_rect()
        self.available_games_rect.topleft = self.available_games_list_pos

        # network stuff
        with open('assets/data/host.txt', 'r') as f:
            self.host = f.read()

        self.port = 33000
        self.bufsiz = 1024
        self.adr = (self.host, self.port)

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.adr)
        print('connected to MAIN game server...')

        print('requesting games...')
        self.available_games = []
        self.get_games()
        print('received all available games...')

    def receive(self):
        while True:
            try:
                msg = self.client_socket.recv(self.bufsiz).decode("utf8")
            except OSError:
                break

    def send(self, msg):
        msg += '\0'
        self.client_socket.send(bytes(msg, 'utf8'))
        if msg == '{quit}\0':
            self.client_socket.close()
            self.connected = False

    def update(self, input):
        self.handle_input(input)

        for button, game in zip(self.games_list_buttons, self.available_games):
            if button.get_pressed():
                port = game[2]
                self.next_scene = MainScene(port=port)

        if self.refresh_button.get_pressed():
            self.refresh()

        self.render_surface.fill(self.colors['1'])
        self.render_surface.blit(self.title_image, self.title_pos)

        self.refresh_button.render(self.render_surface)

        if len(self.available_games) > 0:
            self.render_available_games()
            self.render_surface.blit(self.available_games_render, self.available_games_list_pos)

    def handle_input(self, input):
        for event in input:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    new_pos = (self.render_width * mouse_pos[0] / self.screen_width, self.render_height * mouse_pos[1] / self.screen_height)

                    if self.available_games_rect.collidepoint(new_pos) and len(self.games_list_buttons) > 0:
                        for button in self.games_list_buttons:
                            button.update(new_pos)

                    else:
                        self.refresh_button.update(new_pos)

                elif event.button == 4:
                    self.games_list_offset += 10
                    if len(self.games_list_buttons) > 0:
                        for button in self.games_list_buttons:
                            button.rect.topleft = (button.pos[0], button.pos[1] + self.games_list_offset)

                elif event.button == 5:
                    self.games_list_offset -= 10
                    if len(self.games_list_buttons) > 0:
                        for button in self.games_list_buttons:
                            button.rect.topleft = (button.pos[0], button.pos[1] + self.games_list_offset)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.next_scene = MainMenuScene()
                    self.close()

    def render(self, surface):
        surface.blit(self.render_surface, (0, 0))

    def pre_render_available_games(self):
        buttons = []
        for i, game in enumerate(self.available_games):
            surface = pygame.Surface(self.game_borders[0].get_size()).convert_alpha()
            surface.blit(random.choice(self.game_borders), (0, 0))

            name_render = self.font.render(game[0], True, self.colors['text'])
            name_x = 20
            name_y = int(surface.get_height() / 2 - name_render.get_height() / 2)

            players_render = self.font.render('{}/8'.format(game[1]), True, self.colors['text'])
            players_x = surface.get_width() - players_render.get_width() - 20
            players_y = int(surface.get_height() / 2 - players_render.get_height() / 2)

            surface.blit(name_render, (name_x, name_y))
            surface.blit(players_render, (players_x, players_y))

            buttons.append(menu.Button((self.available_games_list_pos[0], self.available_games_list_pos[1] + i * (162 + 50)), surface))

        self.games_list_buttons = buttons

    def render_available_games(self):
        self.available_games_render.fill(self.colors['1'])

        for i, button in enumerate(self.games_list_buttons):
            self.available_games_render.blit(button.image, (0, i * (162 + 50) + self.games_list_offset))

    def create_game(self):
        self.send(self.name + '\0create')
        self.port = int(self.client_socket.recv(self.bufsiz).decode("utf8"))
        self.client_socket.close()

    def get_games(self):
        self.send(self.name + '\0getgames')
        msg_buffer = ''
        while not msg_buffer or msg_buffer.split('\0')[-2] != 'DONEFLAG':
            msg_buffer += self.client_socket.recv(self.bufsiz).decode("utf8")

        print('available games:')
        msg_split = msg_buffer.split('\0')[:-2]
        for game in msg_split:
            name, players, port = game.split(',')
            print(name, players, port)
            self.available_games.append((name, players, int(port)))

        self.pre_render_available_games()

    def refresh(self):
        self.available_games.clear()
        self.games_list_offset = 0
        print('requesting refresh on available games...')
        self.send('getgames')
        msg_buffer = ''
        while not msg_buffer or msg_buffer.split('\0')[-2] != 'DONEFLAG':
            msg_buffer += self.client_socket.recv(self.bufsiz).decode("utf8")

        print('available games:')
        msg_split = msg_buffer.split('\0')[:-2]
        for game in msg_split:
            name, players, port = game.split(',')
            print(name, players, port)
            self.available_games.append((name, players, int(port)))

        self.pre_render_available_games()

    def close(self):
        if self.connected:
            self.send('{quit}')
