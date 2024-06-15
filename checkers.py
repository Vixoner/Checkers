import pygame, sys
from pygame.locals import *

class Piece:
	def __init__(self, color, isKing = False):
		self.color = color
		self.isKing = isKing
		self.value = 1

	def crown(self):
		self.king = True
		self.value = 2
		
class Game:
	def __init__(self, loop_mode):
		self.gui = GUI()
		
	def setup(self):
		self.gui.setup_window()

		
class GUI:
	def __init__(self):
		self.caption = "Warcaby"
		self.window_size = 1016
		self.screen = pygame.display.set_mode((self.window_size, self.window_size))
		self.background = pygame.image.load('files/board_classic.png')
		self.screen.blit(self.background, (0,0))

	def setup_window(self):
		pygame.init()
		pygame.display.set_caption(self.caption)
