from enum import Enum
import pygame

CELL_SIZE = 100
FPS = 30
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
FIELD_COLOR = 250, 10, 10

class Cell(Enum):
	VOID = 0
	CROSS = 1
	ZERO = 2

class Player:
	"""
	Class of gambleman
	"""
	def __init__(self, name, cell_type):
		self.name = name
		self.cell_type = cell_type

class PlayerView:
	"""
	Виджет игроков. Отображает состояние игроков на экране. 
	показывает чей сейчас ход
	"""
	pass


class GameField:
	def __init__(self, window, field_size=3):
		self.field_size = field_size
		self.cells = [[Cell.VOID] * self.field_size for i in range(self.field_size) ]
		self._field_widget = GameFieldView(self, window)

	def check_lines(self, current_value):
		count_lines = self.field_size * 2 + 2 
		lines = [current_value.value for i in range(count_lines)]
		for i in range(self.field_size):
			for j in range(self.field_size):
				lines[i] = lines[i] & self.cells[i][j].value
				lines[self.field_size + j] = lines[self.field_size + j] & self.cells[i][j].value
			lines[count_lines - 2] = lines[count_lines - 2] & self.cells[i][i].value
			lines[count_lines - 1] = lines[count_lines - 1] & self.cells[self.field_size-i-1][i].value
		print(lines)		
		for i in range(len(lines)):
			if lines[i] != 0:
				print(i)
				self._field_widget.draw_finish_line(i)
				return "done"
		return "change_player"


	def set_cell_value(self, cell_i, cell_j, value):
		if self.cells[cell_i][cell_j] == Cell.VOID:
			self.cells[cell_i][cell_j] = value
			self._field_widget.draw_object_in(cell_i, cell_j)
			return self.check_lines(value)
		else: 
			return False

	def get_coords(self, pos, button):
		return self._field_widget.get_coords(*pos, button)


class GameFieldView:
	"""
	Виджет игрового поля. Отображает поле на экране. 
	Определяет клетку в которую кликнули
	"""
	def __init__(self, field_to_observe, surface_to_draw):
		# отобразить поле, загрузть картинки клеток
		self._field = field_to_observe
		self._height = self._field.field_size * CELL_SIZE
		self._width = self._field.field_size * CELL_SIZE
		self.surface_to_draw = surface_to_draw
		self._window_size = surface_to_draw.get_width(), surface_to_draw.get_height()
		self.initial_draw()

	def initial_draw(self):
		self.cross_cell = pygame.Surface((CELL_SIZE-20, CELL_SIZE-20), pygame.SRCALPHA)
		self.cross_cell.fill(COLOR_BLACK)
		self.cross_cell.set_colorkey(COLOR_BLACK)
		self.cell_rectangle = self.cross_cell.get_rect()
		self.null_cell = self.cross_cell.copy()
		pygame.draw.line(self.cross_cell, COLOR_WHITE, (0, 0), (self.cell_rectangle.width, self.cell_rectangle.height))
		pygame.draw.line(self.cross_cell, COLOR_WHITE, (0, self.cell_rectangle.height), (self.cell_rectangle.width, 0))
		pygame.draw.circle(self.null_cell, COLOR_WHITE, self.cell_rectangle.center, (self.cell_rectangle.height/2))


		self.fieldview = pygame.Surface((self._height , self._width), pygame.SRCALPHA)  
		self.fieldview.fill(FIELD_COLOR)  # fill the rectangle / surface with specified color
		for i in range(1, self._field.field_size + 1): # draw grid
			pygame.draw.line(self.fieldview, COLOR_WHITE, (0, i*CELL_SIZE), (self._width, i*CELL_SIZE))
			pygame.draw.line(self.fieldview, COLOR_WHITE, (i*CELL_SIZE, 0), (i*CELL_SIZE, self._height))
		self.fieldview.set_colorkey(COLOR_BLACK)  
		self.rectangle = self.fieldview.get_rect()  # define rect for placing the rectangle at the desired position
		self.rectangle.center = (self._window_size[0]/2, self._window_size[1]/2)
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def draw_object_in(self, cell_i, cell_j):
		value = self._field.cells[cell_i][cell_j]
		if value != Cell.VOID:
			self.cell_rectangle.center = ((cell_i+1)*CELL_SIZE - CELL_SIZE/2, (cell_j+1)*CELL_SIZE - CELL_SIZE/2)
			print(self.cell_rectangle.center)
		if value == Cell.CROSS:
			self.fieldview.blit(self.cross_cell, self.cell_rectangle)
		elif value == Cell.ZERO:
			self.fieldview.blit(self.null_cell, self.cell_rectangle)
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def draw_finish_line(self, line):
		print ("finish line", line)
		if line < self._field.field_size:
			line_start = (line*CELL_SIZE + CELL_SIZE/2, 10)
			line_stop = (line*CELL_SIZE + CELL_SIZE/2, self._width-10)
			pass
		elif line >= self._field.field_size and line < self._field.field_size*2:
			line_start = (10, (line - self._field.field_size)*CELL_SIZE + CELL_SIZE/2)
			line_stop = (self._width-10, (line - self._field.field_size)*CELL_SIZE + CELL_SIZE/2)
			pass
		elif line == self._field.field_size*2:
			line_start = (10, 10)
			line_stop = (self._width-10, self._width-10)
			pass
		elif line == self._field.field_size*2 + 1:
			line_start = (self._width-10, 10)
			line_stop = (10, self._width-10)
			pass
		else:
			print("exeption")
			return False
		pygame.draw.line(self.fieldview, COLOR_WHITE, line_start, line_stop)
		self.surface_to_draw.blit(self.fieldview , self.rectangle) 



	def get_coords(self, x, y, button):
		# вернуть клетку в которую ткнули, если не попали, вернуть None
		cell = [None, None]
		if button == 1:
			for i in range(self._field.field_size):
				if x > self.rectangle.topleft[0] + i*CELL_SIZE and x < self.rectangle.topleft[0] + (i+1)*CELL_SIZE:
					cell[0] = i
		
			for i in range(self._field.field_size):
				if y > self.rectangle.topleft[1] + i*CELL_SIZE and y < self.rectangle.topleft[1] + (i+1)*CELL_SIZE:
					cell[1] = i
		return tuple(cell)


class GameRoundManager:
	"""
	game manager, run everyone
	"""
	def __init__(self, player1: Player, player2: Player, window):
		self._players = [player1, player2]
		self.current_player = 0
		self.field = GameField(window, 3)


	def done(self):
		#self._players[self.current_player].win()
		pass


	def change_player(self):
		if self.current_player == 0:
			self.current_player = 1
		elif self.current_player == 1:
			self.current_player = 0


	def handle_click(self, pos, button):
		cell_i, cell_j = self.field.get_coords(pos, button)
		if None in (cell_i, cell_j):
			return False
		what_to_do = self.field.set_cell_value(cell_i, cell_j, self._players[self.current_player].cell_type)
			#if self.field.check_lines(self._players[self.current_player].cell_type) != False:
		if what_to_do == "done":
			self.done()
			#return True
		elif what_to_do == "change_player":
			self.change_player()
		return False



class MainWindow:
	"""
	Contain field view, and recive event
	"""
	def __init__(self):
		self._size = 800,600
		self._screen = pygame.display.set_mode(self._size)
		self._clock = pygame.time.Clock()
		self._round_number =0
		pygame.init()
		pygame.display.set_caption("Крестики-Нолики")
		self._game_manager = GameRoundManager(Player("Piter",Cell.CROSS), Player("Vasian",Cell.ZERO), self._screen)
		#self._field_widget = GameFieldView(self._game_manager.field, self._screen)


	def init_game(self):
		pass


	def init_round(self):
		self._round_number += 1
		pass


	def end_round(self):
		pass


	def main_loop(self, tick):
		finished = False
		while not finished:
			self._clock.tick(tick)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					finished = True
				if event.type == pygame.MOUSEBUTTONUP:
					#if self.game_state == "round":
					if self._game_manager.handle_click(event.pos, event.button) == True:
						#self.end_round()
						pass
			pygame.display.flip()				


def main():
	window = MainWindow()
	window.main_loop(FPS)
	print("Game over!")

if __name__ == '__main__':
	main()
