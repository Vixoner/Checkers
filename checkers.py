import pygame, sys
from pygame.locals import *
import time

pygame.font.init()

WHITE = (255, 255, 255)
BLUE = (10, 95, 230)
RED = (219, 18, 18)
PURPLE = (129, 14, 158)
BLACK = (0, 0, 0)
GREEN = (10, 163, 53)
GOLD = (255, 215, 0)
HIGH = (160, 190, 255)
GRAY = (194, 194, 194)
LIGHT_BLUE = (191, 228, 255)

NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Piece:
	def __init__(self, color, is_king = False):
		self.color = color
		self.is_king = is_king
		self.value = 1

	def crown(self):
		self.is_king = True
		self.value = 2

class Square:
	def __init__(self, color, piece = None):
		self.color = color
		self.piece = piece
		
class Game:
	def __init__(self, loop_mode):
		self.gui = GUI()
		self.turn = BLUE
		self.selected_piece = None
		self.hop = False
		self.loop_mode = loop_mode
		self.available_legal_moves = []
		self.board = Board(RED, BLUE)
		self.endit = False
		self.player1_color = RED
		self.player2_color = BLUE
		self.player1_bot = False
		self.player2_bot = False
		self.game_style = "Classic"
		
	def setup(self):
		self.player1_color, self.player2_color, self.player1_bot, self.player2_bot, self.game_style = self.gui.main_menu()
		self.turn = self.player2_color
		self.board = Board(self.player1_color, self.player2_color)
		self.gui.setup_window(self.game_style)

	def player_turn(self):
		mouse_position = tuple(map(int, pygame.mouse.get_pos()))
		self.mouse_position = tuple(map(int, self.gui.board_coords(mouse_position[0], mouse_position[1])))
		#print(self.mouse_position)

		if self.selected_piece != None:
			self.available_legal_moves = self.board.legal_moves_list(self.selected_piece[0], self.selected_piece[1], self.hop)

		for event in pygame.event.get():
			#print(event)
			if event.type == QUIT:
				self.end_game()

			if event.type == MOUSEBUTTONDOWN:
				#print("ola boga")
				#print(self.hop)
				if self.hop == False:
					if self.board.location(self.mouse_position[0], self.mouse_position[1]).piece != None and self.board.location(self.mouse_position[0], self.mouse_position[1]).piece.color == self.turn:
						# wybranie pionka
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

				# podwojne bicie check
				if self.hop == True:
					if self.selected_piece != None and self.mouse_position in self.board.legal_moves_list(self.selected_piece[0], self.selected_piece[1], self.hop):
						self.board.move_piece(self.selected_piece[0], self.selected_piece[1], self.mouse_position[0], self.mouse_position[1])
						self.board.destroy_piece(self.selected_piece[0] + (self.mouse_position[0] - self.selected_piece[0]) // 2, self.selected_piece[1] + (self.mouse_position[1] - self.selected_piece[1]) // 2)

					if self.board.legal_moves_list(self.mouse_position[0], self.mouse_position[1], self.hop) == []:
							self.end_turn()
							#self.hop = False
							#print("CHECK")

					else:
						self.selected_piece = self.mouse_position

	def update(self):
		self.gui.update_display(self.board, self.available_legal_moves, self.selected_piece)

	def end_game(self):
		pygame.quit()
		sys.exit(0)

	def end_turn(self):
		# zmiana tury miedzy graczami
		if self.turn == self.player1_color:
			self.turn = self.player2_color
		else:
			self.turn = self.player1_color

		self.selected_piece = None
		self.available_legal_moves = []
		self.hop = False

		if self.check_for_end():
			if self.turn == self.player2_color:
				self.gui.draw_text("PLAYER 1 WINS!")
			else:
				self.gui.draw_text("PLAYER 2 WINS!")
			if(self.loop_mode):
				self.endit = True
			else:
				self.end_game()

	def check_for_end(self):
		for x in range(8):
			for y in range(8):
				if self.board.location(x, y).color == BLACK and self.board.location(x, y).piece != None and self.board.location(x, y).piece.color == self.turn:
					if self.board.legal_moves_list(x, y) != []:
						return False

		return True
	
	def run(self):
		self.setup()
		run = True
		bot = Bot(self)
		while run:
			if self.turn == self.player1_color:
				if self.player1_bot:
					print("bablbla")

				else:
					self.player_turn()

				self.update()

			if self.turn == self.player2_color:
				if self.player2_bot:	
					print("bablbla")

				else:
					self.player_turn()
				self.update()
		
class GUI:
	def __init__(self):
		self.caption = "Warcaby"
		self.window_size = 1016
		self.screen = pygame.display.set_mode((self.window_size, self.window_size))
		#self.screen.blit(self.background, (0,0))

		self.fps = 60
		self.clock = pygame.time.Clock()

		self.square_size = self.window_size // 8
		self.piece_size = self.square_size // 2
		self.message = False

	def setup_window(self, game_style):
		pygame.init()
		pygame.display.set_caption(self.caption)

		if game_style == "Classic":
			self.background = pygame.image.load('files/board_classic.png')
		elif game_style == "Black and white":
			self.background = pygame.image.load('files/board_blackandwhite.png')
		else:
			self.background = pygame.image.load('files/board_modern.png')

	def update_display(self, board, legal_moves, selected_piece):
		self.screen.blit(self.background, (0,0))

		self.highlight_squares(legal_moves, selected_piece)
		self.draw_board_pieces(board)

		if self.message:
			self.screen.blit(self.text_surface_obj, self.text_rect_obj)

		pygame.display.update()
		self.clock.tick(self.fps)

	def draw_board_squares(self, board):
		for x in range(8):
			for y in range(8):
				pygame.draw.rect(self.screen, board[x][y].color, (x * self.square_size, y * self.square_size, self.square_size, self.square_size), )

	def draw_board_pieces(self, board):
		for x in range(8):
			for y in range(8):
				if board.board_matrix[x][y].piece != None:
					pygame.draw.circle(self.screen, board.board_matrix[x][y].piece.color, tuple(map(int, self.pixel_coords((x, y)))), int(self.piece_size * 0.9))

					if board.location(x,y).piece.is_king == True:
						pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x, y)), int(self.piece_size * 0.9), int(self.piece_size // 16))


	def pixel_coords(self, board_coords):
		return (board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

	def board_coords(self, pixel_x, pixel_y):
		return (pixel_x // self.square_size, pixel_y // self.square_size)

	def highlight_squares(self, squares, origin):
		for square in squares:
			pygame.draw.rect(self.screen, HIGH, (square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))

		if origin != None:
			pygame.draw.rect(self.screen, HIGH, (origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

	def draw_text(self, message):
		self.message = True
		self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
		self.text_surface_obj = self.font_obj.render(message, True, HIGH, BLACK)
		self.text_rect_obj = self.text_surface_obj.get_rect()
		self.text_rect_obj.center = (self.window_size // 2, self.window_size // 2)

	def draw_menu_text(self, text, font, color, surface, x, y):
		text_obj = font.render(text, True, color)
		text_rect = text_obj.get_rect()
		text_rect.topleft = (x, y)
		surface.blit(text_obj, text_rect)

	def main_menu(self):
		font = pygame.font.SysFont(None, 40)
		player1_color = RED
		player2_color = BLUE
		player1_bot = False
		player2_bot = False
		game_style = "Classic"

		player_colors = [RED, BLUE, GRAY, PURPLE, GREEN]
		game_styles = ["Classic", "Modern", "Black and white"]

		while True:
			self.screen.fill(LIGHT_BLUE)

			self.draw_menu_text('Main Menu', font, BLACK, self.screen, self.window_size//2 - 100, 20)
			self.draw_menu_text('Player 1 Color:', font, BLACK, self.screen, self.window_size//2 - 200, 80)
			self.draw_menu_text('Player 2 Color:', font, BLACK, self.screen, self.window_size//2 - 200, 140)
			self.draw_menu_text('Player 1 Bot:', font, BLACK, self.screen, self.window_size//2 - 200, 200)
			self.draw_menu_text('Player 2 Bot:', font, BLACK, self.screen, self.window_size//2 - 200, 260)
			self.draw_menu_text('Game Style:', font, BLACK, self.screen, self.window_size//2 - 200, 320)

			self.draw_menu_text('Start Game', font, BLACK, self.screen, self.window_size//2 - 100, 480)

			pygame.draw.rect(self.screen, player1_color, (self.window_size//2 + 100, 80, 40, 40))
			pygame.draw.rect(self.screen, player2_color, (self.window_size//2 + 100, 140, 40, 40))
			self.draw_menu_text('Yes' if player1_bot else 'No', font, BLACK, self.screen, self.window_size//2 + 100, 200)
			self.draw_menu_text('Yes' if player2_bot else 'No', font, BLACK, self.screen, self.window_size//2 + 100, 260)
			self.draw_menu_text(game_style, font, BLACK, self.screen, self.window_size//2 + 100, 320)

			mx, my = pygame.mouse.get_pos()

			button_player1_color = pygame.Rect(self.window_size//2 + 100, 80, 40, 40)
			button_player2_color = pygame.Rect(self.window_size//2 + 100, 140, 40, 40)
			button_player1_bot = pygame.Rect(self.window_size//2 + 100, 200, 60, 40)
			button_player2_bot = pygame.Rect(self.window_size//2 + 100, 260, 60, 40)
			button_game_style = pygame.Rect(self.window_size//2 + 100, 320, 150, 40)
			button_start = pygame.Rect(self.window_size//2 - 100, 480, 200, 50)

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

			if button_game_style.collidepoint((mx, my)):
				if pygame.mouse.get_pressed()[0]:
					current_index = game_styles.index(game_style)
					game_style = game_styles[(current_index + 1) % len(game_styles)]
					pygame.time.wait(200)

			if button_start.collidepoint((mx, my)):
				if pygame.mouse.get_pressed()[0]:
					print(f"Starting game with Player 1 color: {player1_color}, Player 2 color: {player2_color}, Player 1 bot: {player1_bot}, Player 2 bot: {player2_bot}, Game style: {game_style}")
					pygame.time.wait(200)
					# Here you would transition to the game state
					return player1_color, player2_color, player1_bot, player2_bot, game_style

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
		matrix = [[None] * 8 for i in range(8)]

		for x in range(8):
			for y in range(8):
				if ((x % 2 != 0) and (y % 2 == 0)) or (x % 2 == 0) and (y % 2 != 0):
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

	def rel(self, dir, x, y):
		if dir == NORTHWEST:
			return (x - 1, y - 1)
		elif dir == NORTHEAST:
			return (x + 1, y - 1)
		elif dir == SOUTHWEST:
			return (x - 1, y + 1)
		elif dir == SOUTHEAST:
			return (x + 1, y + 1)
		else:
			return 0

	def adjacent(self, x, y):
		return [self.rel(NORTHWEST, x,y), self.rel(NORTHEAST, x,y),self.rel(SOUTHWEST, x,y),self.rel(SOUTHEAST, x,y)]

	def location(self, x, y):
		x = int(x)
		y = int(y)
		return self.board_matrix[x][y]

	def blind_legal_moves(self, x, y):
		if self.board_matrix[x][y].piece != None:

			if self.board_matrix[x][y].piece.is_king == False and self.board_matrix[x][y].piece.color == self.player2_color:
				blind_legal_moves = [self.rel(NORTHWEST, x, y), self.rel(NORTHEAST, x, y)]

			elif self.board_matrix[x][y].piece.is_king == False and self.board_matrix[x][y].piece.color == self.player1_color:
				blind_legal_moves = [self.rel(SOUTHWEST, x, y), self.rel(SOUTHEAST, x, y)]

			else:
				blind_legal_moves = [self.rel(NORTHWEST, x, y), self.rel(NORTHEAST, x, y), self.rel(SOUTHWEST, x, y), self.rel(SOUTHEAST, x, y)]

		else:
			blind_legal_moves = []

		return blind_legal_moves

	def legal_moves_list(self, x, y, hop = False):
		blind_legal_moves = self.blind_legal_moves(x, y)
		legal_moves = []

		if hop == False:
			for move in blind_legal_moves:
				#???? - check this
				if self.is_on_board(move[0], move[1]):
					if self.location(move[0], move[1]).piece == None:
						legal_moves.append(move)

					elif self.location(move[0], move[1]).piece.color != self.location(x, y).piece.color and self.is_on_board(move[0] + (move[0] - x), move[1] + (move[1] - y)) and self.location(move[0] + (move[0] - x), move[1] + (move[1] - y)).piece == None: # ???
						legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

		else:
			for move in blind_legal_moves:
				if self.is_on_board(move[0], move[1]) and self.location(move[0], move[1]).piece != None:
					if self.location(move[0], move[1]).piece.color != self.location(x, y).piece.color and self.is_on_board(move[0] + (move[0] - x), move[1] + (move[1] - y)) and self.location(move[0] + (move[0] - x), move[1] + (move[1] - y)).piece == None: # ???
						legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

		return legal_moves

	def destroy_piece(self, x, y):
		self.board_matrix[x][y].piece = None

	def move_piece(self, start_x, start_y, end_x, end_y):
		self.board_matrix[end_x][end_y].piece = self.board_matrix[start_x][start_y].piece
		self.destroy_piece(start_x, start_y)

		self.promotion(end_x, end_y)

	def is_end_square(self, coords):
		if coords[1] == 0 or coords[1] == 7:
			return True
		else:
			return False

	def is_on_board(self, x, y):
		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True

	def promotion(self, x, y):
		if self.location(x, y).piece != None:
			if (self.location(x, y).piece.color == self.player2_color and y == 0) or (self.location(x, y).piece.color == self.player1_color and y == 7):
				self.location(x, y).piece.crown()

class Bot:
    def __init__(self, game, depth=3):
        self.game = game
        self.depth = depth

    def get_best_move(self):
        best_move = None
        best_value = float('-inf') if self.game.turn == self.game.player2_color else float('inf')
        
        

