class Piece:
	def __init__(self, color, isKing = False):
		self.color = color
		self.isKing = isKing
		self.value = 1

	def crown(self):
		self.king = True
		self.value = 2