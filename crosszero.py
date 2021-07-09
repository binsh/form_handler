from enum import Enum
import pygame

CELL_SIZE = 50
FPS = 30

class Cell(Enum):
	VOID = 0
	CROSS = 1
	ZERO =2

class Player:
	"""
	Class of gambleman
	"""
	def __init__(self, name, cell_type):
		self.name = name
		self.cell_type = cell_type



class GameField:
	def __init__(self):
		self.height = 3
		self.width = 3
		self.cells = [[Cell.VOID]*self.width for i in range(self.height) ]


class GameFieldView:
	"""
	Витжет игрового поля. Отображает поле на экране. 
	Определяет клетку в которую кликнули
	"""
	def __init__(self, field_to_observe):
		# отобразить поле, загрузть картинки клеток
		self._field = field_to_observe
		self._height = field_to_observe.height * CELL_SIZE
		self._width = field_to_observe.width * CELL_SIZE

	def draw(self):
		pass

	def get_coords(self, x, y, button):
		# вернуть клетку в которую ткнули, если не попали, вернуть False
		print("click", x, y, button)
		return 0, 0


class GameRoundManager:
	"""
	game manager, run everyone
	"""
	def __init__(self, player1: Player, player2: Player):
		self._players = [player1, player2]
		self.current_player = 0
		self.field = GameField()


	def handle_click(self, x, y):
		#if 
		#while not game_over:
		#	player = self._players[current_player]
			# player click to field
		print ("handle_click")


class MainWindow:
	"""
	Contain field view, and recive event
	"""
	def __init__(self):
		self._size = width, height = 800,600
		self._screen = pygame.display.set_mode(self._size)
		self.done = False
		self._clock = pygame.time.Clock()
		pygame.init()
		pygame.display.set_caption("Крестики-Нолики")



		#players = []
		self._game_manager = GameRoundManager(Player("Piter",Cell.CROSS), Player("Vasian",Cell.ZERO))
		self._field_widget = GameFieldView(self._game_manager.field)


	def main_loop(self, tick):
		finished = False
		while not finished:
			self._clock.tick(tick)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					finished = True
				if event.type == pygame.MOUSEBUTTONUP:
					i, j = self._field_widget.get_coords(*event.pos, event.button)
					if False not in (i, j):
						self._game_manager.handle_click(event)
			pygame.display.flip()				


def main():
	window = MainWindow()
	window.main_loop(FPS)
	print("Game over!")

if __name__ == '__main__':
	main()