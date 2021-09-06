from enum import Enum
import pygame
import forms

CELL_SIZE = 100
FPS = 30
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
FIELD_COLOR = 250, 10, 10
COLOR_KEY = 0, 0, 0
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')


class Cell(Enum):
	VOID = 0
	CROSS = 1
	ZERO = 2

class Player:
	"""
	Class of gambleman
	"""
	def __init__(self, name, cell_type, window):
		self.name = name
		self.cell_type = cell_type
		self.score = 0
		self.position = "left"
		#self._player_widget = PlayerView(self, window)

	def win(self):
		self.score +=1
		return self.name, self.score

class PlayerView():
	"""
	Виджет игроков. Отображает состояние игроков на экране. 
	показывает чей сейчас ход
	"""
	def __init__(self, player_to_observe, surface_to_draw):
		self._player = player_to_observe
		self.surface_to_draw = surface_to_draw
		self._window_size = surface_to_draw.get_width(), surface_to_draw.get_height()
		self._height = 400#self._field.field_size * CELL_SIZE
		self._width = 200#self._field.field_size * CELL_SIZE

		self.initial_draw()

	def initial_draw(self):
		self.playerview = pygame.Surface((self._width, self._height), pygame.SRCALPHA)  
		self.playerview.fill(FIELD_COLOR)  # fill the rectangle / surface with specified color
		self.playerview.set_colorkey(COLOR_BLACK)  
		self.rectangle = self.playerview.get_rect()  # define rect for placing the rectangle at the desired position
		if self._player.position == "left":
			self.rectangle.topleft = (10, 10)
		else:
			self.rectangle.topright = (self._window_size[0] - 10, 10)
		self.surface_to_draw.blit(self.playerview , self.rectangle)



class GameField:
	def __init__(self, window, field_size=3):
		self.field_size = field_size
		self.cells = [[Cell.VOID] * self.field_size for i in range(self.field_size) ] #list comprehension
		self._field_widget = GameFieldView(self, window)
		self._field_sum = 0 # for fill field check

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
				self._field_widget.draw_finish_line(i)
				return "done"
		if self._field_sum == self.field_size ** 2:
			return "draw"
		return "change_player"


	def set_cell_value(self, cell_i, cell_j, value):
		if self.cells[cell_i][cell_j] == Cell.VOID:
			self.cells[cell_i][cell_j] = value
			self._field_widget.draw_object_in(cell_i, cell_j)
			self._field_sum += 1
			return self.check_lines(value)
		else: 
			return False


	def get_cell(self, position):
		return self._field_widget.get_cell(*position)


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
		self.cross_cell = pygame.Surface((CELL_SIZE - (CELL_SIZE/5), CELL_SIZE - (CELL_SIZE/5)), pygame.SRCALPHA)
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
		if value == Cell.CROSS:
			self.fieldview.blit(self.cross_cell, self.cell_rectangle)
		elif value == Cell.ZERO:
			self.fieldview.blit(self.null_cell, self.cell_rectangle)
		else:
			return False
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def draw_finish_line(self, line):
		print ("finish line", line)
		padding = 10
		if line < self._field.field_size:
			line_start = (line*CELL_SIZE + CELL_SIZE/2, padding)
			line_stop = (line*CELL_SIZE + CELL_SIZE/2, self._width - padding)
		elif line >= self._field.field_size and line < self._field.field_size*2:
			line_start = (padding, (line - self._field.field_size)*CELL_SIZE + CELL_SIZE/2)
			line_stop = (self._width - padding, (line - self._field.field_size)*CELL_SIZE + CELL_SIZE/2)
		elif line == self._field.field_size*2:
			line_start = (padding, padding)
			line_stop = (self._width - padding, self._width - padding)
		elif line == self._field.field_size*2 + 1:
			line_start = (self._width - padding, padding)
			line_stop = (padding, self._width - padding)
		else:
			print("exeption")
			return False
		pygame.draw.line(self.fieldview, COLOR_WHITE, line_start, line_stop)
		self.surface_to_draw.blit(self.fieldview , self.rectangle)
		self.state = "end_round"


	def get_cell(self, x, y):
		# вернуть клетку в которую ткнули, если не попали, вернуть None
		cell = [None, None]
		for i in range(self._field.field_size):
			if x > self.rectangle.topleft[0] + i*CELL_SIZE and x < self.rectangle.topleft[0] + (i+1)*CELL_SIZE:
				cell[0] = i
			if y > self.rectangle.topleft[1] + i*CELL_SIZE and y < self.rectangle.topleft[1] + (i+1)*CELL_SIZE:
				cell[1] = i		
		return tuple(cell)


class GameManager:
	def __init__(self, window):
		pass

	def handle(self, event):
		return False


class GameRoundManager:
	"""
	game manager, run everyone
	"""
	def __init__(self, players: Player, window):
		self._players = players
		self.current_player = 0
		window.fill(COLOR_BLACK)
		self.field = GameField(window, 3)


	def done(self):
		self._players[self.current_player].win()
		#TODO init form, block gamefield, handle form event - start new round or exit naher
		pass


	def change_player(self):
		#self._players[self.current_player].unset()
		self.current_player = int(not self.current_player)
		#self._players[self.current_player].set()


	def handle(self, event):
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				if self.handle_click(event.pos) == True:
					#return self.end_round()
					#return "end_round"
					pass
		return False


	def handle_click(self, pos):
		cell = self.field.get_cell(pos)
		if None in cell:
			return False
		what_to_do = self.field.set_cell_value(*cell, self._players[self.current_player].cell_type)
		if what_to_do == "done":
			self.done()
			#return True
		elif what_to_do == "change_player":
			self.change_player()
		return False


class GameInitManager:
	def __init__(self, players, window):
		self._state = False
		self._screen = window

		self.new_player_form = forms.Form(window, name="players")
		self.new_player_form.append_unit(forms.InputBox, 'input_player1', (300, 100), (140, 32), {'padding':5}, placeholder="Input name")
		self.new_player_form.append_unit(forms.InputBox, 'input_player2', (300, 200), (140, 32), {'padding':5}, placeholder="Input name")
		self.new_player_form.append_unit(forms.Button, 'start_button', (100, 300), (120, 0), {'padding':5, 'bg_color':COLOR_INACTIVE}, value="Start")
		self.new_player_form.append_unit(forms.Button, 'quit_button', (300, 300), (120, 0), {'padding':5, 'bg_color':COLOR_INACTIVE}, value="Quit game")
		self.new_player_form.append_unit(forms.Label, 'label1', (100,100), style={'padding':5}, value='Player 1 for X')
		self.new_player_form.append_unit(forms.Label, 'label2', (100,200), style={'padding':5}, value='Player 2 for 0')

		def create_user(players):
			data = self.new_player_form.data_collect()
			players[0] = Player(data['input_player1'], Cell.CROSS, self._screen)
			players[1] = Player(data['input_player2'], Cell.ZERO, self._screen)
			print("hello", players[0].name, players[1].name)
			self._state = "init_round"
		self.new_player_form.on("start_button", "click", create_user, (players))
		self.new_player_form.on("quit_button", "click", pygame.event.post, (pygame.event.Event(pygame.QUIT)))

	def handle(self, event):
		self.new_player_form.handle(event)
		return self._state
	

class MainWindow:
	"""
	Contain field view, and recive event
	"""
	def __init__(self):
		self._size = 800,600
		self._screen = pygame.display.set_mode(self._size)
		self._screen.fill(0)
		self._clock = pygame.time.Clock()
		self._round_number = 0
		self.players = [None, None]
		pygame.init()
		pygame.display.set_caption("Крестики-Нолики")
		self.router("init_game")

	def router(self, state):
		if state == "init_game":
			self._handler = GameInitManager(self.players, self._screen)
		elif state == "init_round":
			self._round_number += 1
			self._handler  = GameRoundManager(self.players, self._screen)
		elif state == "end_round":
			self.end_round()
		else:
			return False


	def end_round(self):
		pass


	def handle(self, event):
		state = self._handler.handle(event)
		if state != False:
			self.router(state)

	def main_loop(self, tick):
		quit = False
		while not quit:
			self._clock.tick(tick)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					quit = True
				elif event.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
					self.handle(event)
			pygame.display.flip()				


def main():
	window = MainWindow()
	window.main_loop(FPS)
	print("Game over!")

if __name__ == '__main__':
	main()


