import pygame, sys
from pygame.locals import *
import time
import random
from copy import deepcopy

WHITE = (255, 255, 255)
BLUE = (10, 95, 230)
RED = (219, 18, 18)
PURPLE = (129, 14, 158)
BLACK = (0, 0, 0)
GREEN = (10, 163, 53)
GOLD = (230, 220, 0)
GRAY = (194, 194, 194)
HIGHLIGHT = (247, 255, 217)
LIGHT_BLUE = (191, 228, 255)

pygame.font.init()

class Piece:
    def __init__(self, color, is_king = False):
        self.value = 1
        self.color = color
        self.is_king = is_king 

    def crown(self):
        self.value = 2
        self.is_king = True

class Square:
    def __init__(self, color, piece = None):
        self.color = color
        self.piece = piece
        
class Game:
    def __init__(self):
        self.gui = GUI()
        self.turn = BLUE
        self.selected_piece = None
        self.hop = False
        self.available_legal_moves = []
        self.board = Board(RED, BLUE)
        self.gameover = False
        self.player1_color = RED
        self.player2_color = BLUE
        self.player1_bot = False
        self.player2_bot = False
        self.player1_bot_diff = "Medium"
        self.player2_bot_diff = "Medium"
        self.game_style = "Classic"
        
    def setup(self):
        self.player1_color, self.player2_color, self.player1_bot, self.player2_bot, self.player1_bot_diff, self.player2_bot_diff, self.game_style = self.gui.main_menu()
        self.turn = self.player2_color
        self.board = Board(self.player1_color, self.player2_color)
        self.gui.setup_window(self.game_style)

    def player_turn(self):
        mouse_position = tuple(map(int, pygame.mouse.get_pos()))
        self.mouse_position = tuple(map(int, self.gui.board_coords(*mouse_position)))
        #print(self.mouse_position)

        if self.selected_piece:
            self.available_legal_moves = self.board.legal_moves_list(*self.selected_piece, self.hop)

        for event in pygame.event.get():
            if event.type == QUIT:
                self.end_game()

            if event.type == MOUSEBUTTONDOWN:
                if self.hop == False:
                    self.handle_normal_move()

                # podwojne bicie check
                if self.hop == True:
                    self.handle_hop_move()

    def handle_normal_move(self):
        if self.board.location(self.mouse_position[0], self.mouse_position[1]).piece != None and self.board.location(self.mouse_position[0], self.mouse_position[1]).piece.color == self.turn:
            self.selected_piece = self.mouse_position

        elif self.selected_piece != None and self.mouse_position in self.board.legal_moves_list(self.selected_piece[0], self.selected_piece[1]):
            # ruszanie pionkiem
            self.board.move_piece(self.selected_piece[0], self.selected_piece[1], self.mouse_position[0], self.mouse_position[1])

            # sprawdza czy zbito i zbija lub kończy turę
            if self.mouse_position not in self.board.adjacent(self.selected_piece[0], self.selected_piece[1]):
                self.board.destroy_piece(self.selected_piece[0] + (self.mouse_position[0] - self.selected_piece[0]) // 2, self.selected_piece[1] + (self.mouse_position[1] - self.selected_piece[1]) // 2)

                self.selected_piece = self.mouse_position
                self.hop = True
            else:
                self.end_turn()

    def handle_hop_move(self):
        if self.selected_piece != None and self.mouse_position in self.board.legal_moves_list(self.selected_piece[0], self.selected_piece[1], self.hop):
            self.board.move_piece(self.selected_piece[0], self.selected_piece[1], self.mouse_position[0], self.mouse_position[1])
            self.board.destroy_piece(self.selected_piece[0] + (self.mouse_position[0] - self.selected_piece[0]) // 2, self.selected_piece[1] + (self.mouse_position[1] - self.selected_piece[1]) // 2)

        if self.board.legal_moves_list(self.mouse_position[0], self.mouse_position[1], self.hop) == []:
                self.end_turn()

        else:
            self.selected_piece = self.mouse_position

    def update(self):
        self.gui.update_display(self.board, self.available_legal_moves, self.selected_piece)

    def end_game(self):
        pygame.quit()
        sys.exit(0)

    def end_turn(self):
        # zmiana tury miedzy graczami
        self.turn = self.player2_color if self.turn == self.player1_color else self.player1_color

        self.selected_piece = None
        self.available_legal_moves = []
        self.hop = False

        if self.check_for_end():
            self.gui.draw_text("PLAYER 1 WINS!" if self.turn == self.player2_color else "PLAYER 2 WINS!")
            self.gameover = True

    def check_for_end(self):
        for x in range(8):
            for y in range(8):
                location = self.board.location(x, y)
                if location.color == BLACK and location.piece and location.piece.color == self.turn:
                    if self.board.legal_moves_list(x, y):
                        return False

        return True
    
    def run(self):
        self.setup()
        run = True
        bot1 = Bot(self, self.player1_color, self.player2_color, self.player1_bot_diff)
        bot2 = Bot(self, self.player2_color, self.player1_color, self.player2_bot_diff)
        while run:
            if self.turn == self.player1_color:
                if self.player1_bot:            
                    bot1.step(self.board)

                else:
                    self.player_turn()

                self.update()

            if self.turn == self.player2_color:
                if self.player2_bot:	      
                    bot2.step(self.board)

                else:
                    self.player_turn()

                self.update()
                        
            if self.gameover:
                time.sleep(3)
                break
        
class GUI:
    def __init__(self):
        self.window_size = 1016
        self.square_size = self.window_size // 8
        self.piece_size = self.square_size // 2
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.message = False

    def setup_window(self, game_style):
        pygame.init()
        pygame.display.set_caption("Checkers")

        background_files = {
            "Classic": 'files/board_classic.png',
            "Black and white": 'files/board_blackandwhite.png',
            "Modern": 'files/board_modern.png'
        }

        self.background = pygame.image.load(background_files[game_style])

    def update_display(self, board, legal_moves, selected_piece):
        self.screen.blit(self.background, (0,0))
        self.HIGHLIGHTlight_squares(legal_moves, selected_piece)
        self.draw_board_pieces(board)

        if self.message:
            self.screen.blit(self.text_surface_obj, self.text_rect_obj)

        pygame.display.update()
        self.clock.tick(self.fps)

    def draw_board_squares(self, board):
        for x in range(8):
            for y in range(8):
                pygame.draw.rect(self.screen, board[x][y].color, (x * self.square_size, y * self.square_size, self.square_size, self.square_size))

    def draw_board_pieces(self, board):
        for x in range(8):
            for y in range(8):
                piece = board.board_matrix[x][y].piece
                if piece:
                    pygame.draw.circle(self.screen, piece.color, self.pixel_coords((x, y)), int(self.piece_size * 0.9))
                    if piece.is_king:
                        pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x, y)), int(self.piece_size * 0.9), int(self.piece_size // 16))


    def pixel_coords(self, board_coords):
        return (board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

    def board_coords(self, pixel_x, pixel_y):
        return (pixel_x // self.square_size, pixel_y // self.square_size)

    def HIGHLIGHTlight_squares(self, squares, origin):
        for square in squares:
            pygame.draw.rect(self.screen, HIGHLIGHT, (square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))

        if origin:
            pygame.draw.rect(self.screen, HIGHLIGHT, (origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

    def draw_text(self, message):
        self.message = True
        self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
        self.text_surface_obj = self.font_obj.render(message, True, HIGHLIGHT, BLACK)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size // 2, self.window_size // 2)

    def draw_menu_text(self, text, font, color, surface, x, y):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def main_menu(self):
        font = pygame.font.SysFont(None, 40)
        pygame.display.set_caption("Main Menu")
        player1_color = RED
        player2_color = BLUE
        player1_bot = False
        player2_bot = False
        game_style = "Classic"
        player1_difficulty = "Medium"
        player2_difficulty = "Medium"

        player_colors = [RED, BLUE, GRAY, PURPLE, GREEN]
        game_styles = ["Classic", "Modern", "Black and white"]
        difficulty_levels = ["Easy", "Medium", "Hard"]

        player1_height = 160
        player2_height = 320

        while True:
            self.screen.fill(LIGHT_BLUE)

            self.draw_menu_text('Main Menu', font, BLACK, self.screen, self.window_size//2 - 100, 20)
            self.draw_menu_text('Player 1:', font, BLACK, self.screen, self.window_size//2 - 400, player1_height - 60)
            self.draw_menu_text('Player 2:', font, BLACK, self.screen, self.window_size//2 - 400, player2_height - 60)
            self.draw_menu_text('Color:', font, BLACK, self.screen, self.window_size//2 - 400, player1_height)
            self.draw_menu_text('Color:', font, BLACK, self.screen, self.window_size//2 - 400, player2_height)
            self.draw_menu_text('Bot:', font, BLACK, self.screen, self.window_size//2 - 200, player1_height)
            self.draw_menu_text('Bot:', font, BLACK, self.screen, self.window_size//2 - 200, player2_height)
            if player1_bot:
                self.draw_menu_text('Bot difficulty:', font, BLACK, self.screen, self.window_size//2, player1_height)
            if player2_bot:
                self.draw_menu_text('Bot difficulty:', font, BLACK, self.screen, self.window_size//2, player2_height)
            self.draw_menu_text('Game Style:', font, BLACK, self.screen, self.window_size//2 - 400, 440)
            self.draw_menu_text('Start Game', font, BLACK, self.screen, self.window_size//2 - 100, 550)

            pygame.draw.rect(self.screen, player1_color, (self.window_size//2 - 300, player1_height - 10, 40, 40))
            pygame.draw.rect(self.screen, player2_color, (self.window_size//2 - 300, player2_height - 10, 40, 40))
            self.draw_menu_text('Yes' if player1_bot else 'No', font, BLACK, self.screen, self.window_size//2 - 130, player1_height)
            self.draw_menu_text('Yes' if player2_bot else 'No', font, BLACK, self.screen, self.window_size//2 - 130, player2_height)
            if player1_bot:
                self.draw_menu_text(player1_difficulty, font, BLACK, self.screen, self.window_size//2 + 200, player1_height)
            if player2_bot:
                self.draw_menu_text(player2_difficulty, font, BLACK, self.screen, self.window_size//2 + 200, player2_height)
            self.draw_menu_text(game_style, font, BLACK, self.screen, self.window_size//2 - 200, 440)

            mx, my = pygame.mouse.get_pos()

            button_player1_color = pygame.Rect(self.window_size//2 - 300, player1_height - 10, 40, 40)
            button_player2_color = pygame.Rect(self.window_size//2 - 300, player2_height - 10, 40, 40)
            button_player1_bot = pygame.Rect(self.window_size//2 - 130, player1_height, 60, 40)
            button_player2_bot = pygame.Rect(self.window_size//2 - 130, player2_height, 60, 40)
            button_player1_difficulty = pygame.Rect(self.window_size//2 + 200, player1_height, 150, 40)
            button_player2_difficulty = pygame.Rect(self.window_size//2 + 200, player2_height, 150, 40)
            button_game_style = pygame.Rect(self.window_size//2 - 200, 440, 150, 40)
            button_start = pygame.Rect(self.window_size//2 - 100, 550, 200, 50)

            if button_player1_color.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    current_index = player_colors.index(player1_color)
                    player1_color = player_colors[(current_index + 1) % len(player_colors)]
                    pygame.time.wait(200)
        
            if button_player2_color.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    current_index = player_colors.index(player2_color)
                    player2_color = player_colors[(current_index + 1) % len(player_colors)]
                    pygame.time.wait(200)

            if button_player1_bot.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    player1_bot = not player1_bot
                    pygame.time.wait(200)

            if button_player2_bot.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    player2_bot = not player2_bot
                    pygame.time.wait(200)

            if player1_bot and button_player1_difficulty.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    current_index = difficulty_levels.index(player1_difficulty)
                    player1_difficulty = difficulty_levels[(current_index + 1) % len(difficulty_levels)]
                    pygame.time.wait(200)

            if player2_bot and button_player2_difficulty.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    current_index = difficulty_levels.index(player2_difficulty)
                    player2_difficulty = difficulty_levels[(current_index + 1) % len(difficulty_levels)]
                    pygame.time.wait(200)

            if button_game_style.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    current_index = game_styles.index(game_style)
                    game_style = game_styles[(current_index + 1) % len(game_styles)]
                    pygame.time.wait(200)

            if button_start.collidepoint((mx, my)):
                if pygame.mouse.get_pressed()[0]:
                    if player1_color == player2_color:
                        print("Both players can't have the same color")
                    else:
                        print(f"Starting game with Player 1 color: {player1_color}, Player 2 color: {player2_color}, Player 1 bot: {player1_bot}, Player 2 bot: {player2_bot}, Game style: {game_style}")
                        return player1_color, player2_color, player1_bot, player2_bot, player1_difficulty, player2_difficulty, game_style

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

class Board:
    def __init__(self, player1_color, player2_color):
        self.player1_color = player1_color
        self.player2_color = player2_color
        self.board_matrix = self.new_board()

    def new_board(self):
        matrix = [[None] * 8 for _ in range(8)]

        for x in range(8):
            for y in range(8):
                if (x % 2 != y % 2):
                    matrix[y][x] = Square(WHITE)
                else:
                    matrix[y][x] = Square(BLACK)

        for x in range(8):
            for y in range(3):
                if matrix[x][y].color == BLACK:
                    matrix[x][y].piece = Piece(self.player1_color)
            for y in range(5, 8):
                if matrix[x][y].color == BLACK:
                    matrix[x][y].piece = Piece(self.player2_color)

        return matrix

    def adjacent(self, x, y):
        return [(x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)]

    def location(self, x, y):
        return self.board_matrix[x][y]

    def blind_legal_moves(self, x, y):
        piece = self.location(x, y).piece
        if piece:
            if not piece.is_king:
                if piece.color == self.player2_color:
                    return [(x - 1, y - 1), (x + 1, y - 1)]
                if piece.color == self.player1_color:
                    return [(x - 1, y + 1), (x + 1, y + 1)]
            else:
                return self.adjacent(x, y)
        return []

    def legal_moves_list(self, x, y, hop=False):
        blind_legal_moves = self.blind_legal_moves(x, y)
        legal_moves = []

        if not hop:
            for move in blind_legal_moves:
                if self.is_on_board(*move):
                    if self.location(*move).piece is None:
                        legal_moves.append(move)

                    elif (self.location(*move).piece.color != self.location(x, y).piece.color and 
                            self.is_on_board(move[0] + (move[0] - x), move[1] + (move[1] - y)) and 
                            self.location(move[0] + (move[0] - x), move[1] + (move[1] - y)).piece is None):
                        legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

        else:
            for move in blind_legal_moves:
                if (self.is_on_board(*move) and self.location(*move).piece and 
                        self.location(*move).piece.color != self.location(x, y).piece.color and 
                        self.is_on_board(move[0] + (move[0] - x), move[1] + (move[1] - y)) and 
                        self.location(move[0] + (move[0] - x), move[1] + (move[1] - y)).piece is None):
                    legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

        return legal_moves

    def destroy_piece(self, x, y):
        self.board_matrix[x][y].piece = None

    def is_end_square(self, coords):
        return coords[1] == 0 or coords[1] == 7

    def is_on_board(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def move_piece(self, start_x, start_y, end_x, end_y):
        self.board_matrix[end_x][end_y].piece = self.board_matrix[start_x][start_y].piece
        self.destroy_piece(start_x, start_y)
        self.promotion(end_x, end_y)

    def promotion(self, x, y):
        piece = self.location(x, y).piece
        if piece and ((piece.color == self.player2_color and y == 0) or (piece.color == self.player1_color and y == 7)):
            piece.crown()

class Bot:
    def __init__(self, game, color, enemy_color, diff="Medium"):
        if diff == "Easy":
            self.depth = 1
        elif diff == "Medium":
            self.depth = 2
        else:
            self.depth = 3

        self.game = game
        self.color = color
        self.enemy_color = enemy_color
        self.eval_color = color
        
    def step(self, board):
        best_move, best_choice, _ = self.minimax(self.depth - 1, board, 'max')
        #print(best_move, best_choice)
        self.action(best_move, best_choice, board)
        
    def minimax(self, depth, board, fn):
        if depth == 0:
            return self.evaluate_moves(board, fn)
        else:
            return self.minimax_recursion(depth, board, fn)

    def evaluate_moves(self, board, fn):
        best_value = -float("inf") if fn == 'max' else float("inf")
        best_pos = None
        best_action = None

        for pos in self.generate_move(board):
            for action in pos[2]:
                board_clone = deepcopy(board)
                self.toggle_colors_and_turn()
                self.action_on_board(board_clone, pos, action)
                step_value = self.evaluate(board_clone)
                self.toggle_colors_and_turn()

                if fn == 'max':
                    if step_value > best_value:
                        best_value = step_value
                        best_pos = pos
                        best_action = (action[0], action[1])

                    elif step_value == best_value and random.random() <= 0.5:
                        best_value = step_value
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

                    if step_value == -float("inf") and best_pos is  None:
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

                else:
                    if step_value < best_value:
                        best_value = step_value
                        best_pos = pos
                        best_action = action

                    elif step_value == best_value and random.random() <= 0.5:
                        best_value = step_value
                        best_pos = pos
                        best_action = action

                    if step_value == float("inf") and best_pos is  None:
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

        return best_pos, best_action, best_value
        
    def minimax_recursion(self, depth, board, fn):
        best_value = -float("inf") if fn == 'max' else float("inf")
        best_pos = None
        best_action = None

        for pos in self.generate_move(board):
            for action in pos[2]:
                board_clone = deepcopy(board)
                self.toggle_colors_and_turn()
                self.action_on_board(board_clone, pos, action)

                if self.check_for_endgame(board_clone):
                    step_value = float("inf") if fn == 'max' else -float("inf")

                else:
                    _, _, step_value = self.minimax(depth - 1, board_clone, 'min' if fn == 'max' else 'max')

                self.toggle_colors_and_turn()

                if fn == 'max':
                    if step_value is None:
                        continue

                    if step_value > best_value:
                        best_value = step_value
                        best_pos = pos
                        best_action = action

                    elif step_value == best_value and random.random() <= 0.5:
                        best_value = step_value
                        best_pos = pos
                        best_action = action

                    if step_value == -float("inf") and best_pos is  None:
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

                else:
                    if step_value is None:
                        continue

                    if step_value < best_value:
                        best_value = step_value
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

                    elif step_value == best_value and random.random() <= 0.5:
                        best_value = step_value
                        best_pos = pos
                        best_action = action

                    if step_value == float("inf") and best_pos is  None:
                        best_pos = (pos[0], pos[1])
                        best_action = (action[0], action[1])

        return best_pos, best_action, best_value
    
    def toggle_colors_and_turn(self):
        self.color, self.enemy_color = self.enemy_color, self.color
        self.game.turn = self.color

    def action(self, current_position, final_position, board):
        if current_position is None:
            self.game.end_turn()

        if not self.game.hop:
            if final_position and board.location(final_position[0], final_position[1]).piece and board.location(final_position[0], final_position[1]).piece.color == self.game.turn:
                current_position = final_position

            elif current_position and final_position in board.legal_moves_list(current_position[0], current_position[1]):
                board.move_piece(current_position[0], current_position[1], final_position[0], final_position[1])

                if final_position not in board.adjacent(current_position[0], current_position[1]):
                    board.destroy_piece(current_position[0] + (final_position[0] - current_position[0]) // 2, current_position[1] + (final_position[1] - current_position[1]) // 2)
                    self.game.hop = True
                    current_position = final_position
                    final_position = board.legal_moves_list(current_position[0], current_position[1], True)
                    if final_position:
                        self.action(current_position, final_position[0], board)
                    self.game.end_turn()

        if self.game.hop:
            if current_position and final_position in board.legal_moves_list(current_position[0], current_position[1], self.game.hop):
                board.move_piece(current_position[0], current_position[1], final_position[0], final_position[1])
                board.destroy_piece(current_position[0] + (final_position[0] - current_position[0]) // 2, current_position[1] + (final_position[1] - current_position[1]) // 2)

            if not board.legal_moves_list(final_position[0], final_position[1], self.game.hop):
                self.game.end_turn()

            else:
                current_position = final_position
                final_position = board.legal_moves_list(current_position[0], current_position[1], True)
                if final_position:
                    self.action(current_position, final_position[0], board)
                self.game.end_turn()

        if not self.game.hop:
            self.game.turn = self.enemy_color

    def action_on_board(self, board, current_position, final_position, hop=False):
        if not hop:
            if board.location(final_position[0], final_position[1]).piece and board.location(final_position[0], final_position[1]).piece.color == self.game.turn:
                current_position = final_position

            elif current_position and final_position in board.legal_moves_list(current_position[0], current_position[1]):
                board.move_piece(current_position[0], current_position[1], final_position[0], final_position[1])

                if final_position not in board.adjacent(current_position[0], current_position[1]):
                    board.destroy_piece(current_position[0] + (final_position[0] - current_position[0]) // 2, current_position[1] + (final_position[1] - current_position[1]) // 2)
                    hop = True
                    current_position = final_position
                    final_position = board.legal_moves_list(current_position[0], current_position[1], True)
                    if final_position:
                        self.action_on_board(board, current_position, final_position[0],hop=True)
        else:
            if current_position and final_position in board.legal_moves_list(current_position[0], current_position[1], hop):
                board.move_piece(current_position[0], current_position[1], final_position[0], final_position[1])
                board.destroy_piece(current_position[0] + (final_position[0] - current_position[0]) // 2, current_position[1] + (final_position[1] - current_position[1]) // 2)

            if board.legal_moves_list(final_position[0], final_position[1], self.game.hop) == []:
                return
            
            else:
                current_position = final_position
                final_position = board.legal_moves_list(current_position[0], current_position[1], True)
                if final_position:
                    self.action_on_board(board, current_position, final_position[0],hop=True)

    def generate_move(self, board):
        for x in range(8):
            for y in range(8):
                if(board.legal_moves_list(x, y, self.game.hop) != [] and board.location(x, y).piece != None and board.location(x, y).piece.color == self.game.turn):
                    yield (x, y, board.legal_moves_list(x, y, self.game.hop))

    def evaluate(self, board):
        score = 0
        num_pieces = 0
        is_player1 = (self.eval_color == self.game.player1_color)

        for x in range(8):
            for y in range(8):
                piece = board.location(x, y).piece
                if piece is not None:
                    num_pieces += 1
                    if piece.color == self.eval_color:
                        if piece.is_king:
                            score += 10
                        elif y < 4:
                            score += 5 if is_player1 else 7
                        else:
                            score += 7
                    else:
                        if piece.is_king:
                            score -= 10
                        elif y < 4:
                            score -= 7 if is_player1 else 5  # for sure?
                        else:
                            score -= 5

        return score / num_pieces if num_pieces > 0 else 0

    def all_kings(self, board):
        for x in range(8):
            for y in range(8):
                piece = board.location(x, y).piece
                if piece and not piece.is_king:
                    return False
        return True

    def check_for_endgame(self, board):
        for x in range(8):
            for y in range(8):
                if board.location(x, y).piece and board.location(x, y).color == BLACK and board.location(x, y).piece.color == self.game.turn and board.legal_moves_list(x, y):
                    return False
        return True
