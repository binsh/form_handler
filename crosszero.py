from enum import Enum
import pygame
import forms

CELL_SIZE = 100
FIELD_GEOMETRIC_SIZE = 300
FPS = 30
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
FIELD_COLOR = 250, 10, 10
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')


def draw_cross_zero(cell_type, cell_size) -> pygame.Surface:
	cell = pygame.Surface((cell_size - (cell_size/5), cell_size - (cell_size/5)), pygame.SRCALPHA)
	cell.fill(COLOR_BLACK)
	cell.set_colorkey(COLOR_BLACK)
	cell_rectangle = cell.get_rect()
	if cell_type == Cell.CROSS:
		pygame.draw.line(cell, COLOR_WHITE, (0, 0), (cell_rectangle.width, cell_rectangle.height), width=2)
		pygame.draw.line(cell, COLOR_WHITE, (0, cell_rectangle.height), (cell_rectangle.width, 0), width=2)
	elif cell_type == Cell.ZERO:
		pygame.draw.circle(cell, COLOR_WHITE, (cell_rectangle.width/2, cell_rectangle.height/2), (cell_rectangle.height/2), width=2)
	else:
		return False
	return cell


class Cell(Enum):
	VOID = 0
	CROSS = 1
	ZERO = 2

class Player:
	"""
	Class of gambleman
	"""
	def __init__(self, name, cell_type, surface_to_draw):
		self.name = name
		self.cell_type = cell_type
		self.score = 0
		self._player_widget = PlayerView(self, surface_to_draw)
		self._turn = 0

	def win(self):
		self.score +=1
		return self.name, self.score

	def set(self, turn):
		self._turn = turn
		self._player_widget.draw()


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
		self.bg_color = (100,100,255)
		self.initial_draw()

	def initial_draw(self):
		self.playerview = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
		self.playerview.fill(self.bg_color)  # fill the rectangle / surface with specified color
		self.playerview.set_colorkey(COLOR_BLACK)  
		self.rectangle = self.playerview.get_rect()  # define rect for placing the rectangle at the desired position
		if self._player.cell_type == Cell.CROSS:
			self.rectangle.topleft = (10, 10)
			self.cell = draw_cross_zero(Cell.CROSS, 50)
		else:
			self.rectangle.topright = (self._window_size[0] - 10, 10)
			self.cell = draw_cross_zero(Cell.ZERO, 50)
		self.cell_rectangle = self.cell.get_rect()
		self.playerview.blit(self.cell, (10,10))

		self.font = pygame.font.Font(None, 32)
		self.txt_surface = self.font.render(self._player.name, True, COLOR_WHITE)
		self.playerview.blit(self.txt_surface, (10 + CELL_SIZE, 10 + CELL_SIZE/2 - 16))

	def draw(self):
		if self._player._turn:
			pygame.draw.rect(self.playerview, COLOR_WHITE, (0,0, self.rectangle.w-2, self.rectangle.h-2), 4)
		else:
			pygame.draw.rect(self.playerview, self.bg_color, (0,0, self.rectangle.w-2, self.rectangle.h-2), 4)
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
	Gamefield winget. Show field on screen. 
	Track clicked cell
	"""
	def __init__(self, field_to_observe, surface_to_draw):
		# show field,
		self._field = field_to_observe
		self._height = FIELD_GEOMETRIC_SIZE #self._field.field_size * CELL_SIZE
		self._width = FIELD_GEOMETRIC_SIZE #self._field.field_size * CELL_SIZE
		self._cell_size = int(FIELD_GEOMETRIC_SIZE / self._field.field_size)
		self.surface_to_draw = surface_to_draw
		self._window_size = surface_to_draw.get_width(), surface_to_draw.get_height()

		self.initial_draw()

	def initial_draw(self):
		self.cross_cell = draw_cross_zero(Cell.CROSS, self._cell_size)
		self.null_cell = draw_cross_zero(Cell.ZERO, self._cell_size)
		self.cell_rectangle = self.cross_cell.get_rect()

		self.fieldview = pygame.Surface((self._height , self._width), pygame.SRCALPHA)  
		self.fieldview.fill(FIELD_COLOR)  # fill the rectangle / surface with specified color
		for i in range(1, self._field.field_size + 1): # draw grid
			pygame.draw.line(self.fieldview, COLOR_WHITE, (0, i*self._cell_size), (self._width, i*self._cell_size))
			pygame.draw.line(self.fieldview, COLOR_WHITE, (i*self._cell_size, 0), (i*self._cell_size, self._height))
		self.fieldview.set_colorkey(COLOR_BLACK)  
		self.rectangle = self.fieldview.get_rect()  # define rect for placing the rectangle at the desired position
		self.rectangle.center = (self._window_size[0]/2, self._window_size[1]/2)
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def draw_object_in(self, cell_i, cell_j):
		value = self._field.cells[cell_i][cell_j]
		if value != Cell.VOID:
			self.cell_rectangle.center = ((cell_i+1)*self._cell_size - self._cell_size/2, (cell_j+1)*self._cell_size - self._cell_size/2)
		if value == Cell.CROSS:
			self.fieldview.blit(self.cross_cell, self.cell_rectangle)
		elif value == Cell.ZERO:
			self.fieldview.blit(self.null_cell, self.cell_rectangle)
		else:
			return False
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def draw_finish_line(self, line):
		padding = 5
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
		pygame.draw.line(self.fieldview, (150,150,150), line_start, line_stop, width=8)
		self.surface_to_draw.blit(self.fieldview , self.rectangle)


	def get_cell(self, x, y):
		# return clicked cell, if miss, return None
		cell = [None, None]
		for i in range(self._field.field_size):
			if x > self.rectangle.topleft[0] + i*CELL_SIZE and x < self.rectangle.topleft[0] + (i+1)*CELL_SIZE:
				cell[0] = i
			if y > self.rectangle.topleft[1] + i*CELL_SIZE and y < self.rectangle.topleft[1] + (i+1)*CELL_SIZE:
				cell[1] = i		
		return tuple(cell)


class GameRoundManager:
	"""
	game manager, run everyone
	"""
	def __init__(self, players: Player, field_size, window):
		self._state = False
		self._players = players
		self.current_player = 0
		window.fill(COLOR_BLACK)
		self.field = GameField(window, field_size)
		self._players[self.current_player].set(True)
		self._players[int(not self.current_player)].set(False)

	def change_player(self):
		self._players[self.current_player].set(False)
		self.current_player = int(not self.current_player)
		self._players[self.current_player].set(True)

	def get_winner(self):
		if self._state == "done":
			return self.current_player
		else:
			return None

	def handle(self, event):
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				if self.handle_click(event.pos) == True:
					return "end_round"
					pass
		return False

	def handle_click(self, pos):
		cell = self.field.get_cell(pos)
		if None in cell:
			return False
		self._state = self.field.set_cell_value(*cell, self._players[self.current_player].cell_type)
		if self._state == "done":
			self._players[self.current_player].win()
		if self._state == "done" or self._state == "draw":
			return True
		elif self._state == "change_player":
			self.change_player()
		return False


class GameInitManager:
	def __init__(self, players, window):
		self._state = False
		self._screen = window
		self.field_size = 3

		self.new_player_form = forms.Form(window, name="players")
		self.new_player_form.append_unit(forms.InputBox, 'input_player1', (260, 100), size=(200, 32), style={'padding':5}, placeholder="Input name")
		self.new_player_form.append_unit(forms.InputBox, 'input_player2', (260, 150), size=(200, 32), style={'padding':5}, placeholder="Input name")
		self.new_player_form.append_unit(forms.Button, 'start_button', (100, 300), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Start")
		self.new_player_form.append_unit(forms.Button, 'quit_button', (300, 300), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Quit game")
		self.new_player_form.append_unit(forms.Label, 'label1', (100,100), style={'padding':5}, value='Player 1 for X')
		self.new_player_form.append_unit(forms.Label, 'label2', (100,150), style={'padding':5}, value='Player 2 for 0')
		self.new_player_form.append_unit(forms.RadioGroup, 'radio')
		self.new_player_form.get_unit('radio').append_unit('radio1', (260,208), checked=True, value=3)
		self.new_player_form.get_unit('radio').append_unit('radio2', (360,208), value=4)
		self.new_player_form.get_unit('radio').append_unit('radio3', (460,208), checked=False, value=5)
		self.new_player_form.append_unit(forms.Label, 'fielsize', (100,200), style={'padding':5}, value='Field size:')
		self.new_player_form.append_unit(forms.Label, 'radio3x3', (280,200), style={'padding':5}, value='3x3')
		self.new_player_form.append_unit(forms.Label, 'radio4x4', (380,200), style={'padding':5}, value='4x4')
		self.new_player_form.append_unit(forms.Label, 'radio5x5', (480,200), style={'padding':5}, value='5x5')

		@self.new_player_form.bind('start_button', 'click', players)
		def create_user(players):
			data = self.new_player_form.data_collect()
			print (data['radio'])
			if len(data['input_player1']) > 2 and len(data['input_player2']) > 2:
				players[0] = Player(data['input_player1'], Cell.CROSS, self._screen)
				players[1] = Player(data['input_player2'], Cell.ZERO, self._screen)
				print("hello", players[0].name, players[1].name)
				self._state = "init_round"
				self.field_size = data['radio']
				return "init_round"
			else:
				self.new_player_form.append_unit(forms.Label, 'error_message', (100,250), style={'padding':5,'text_color':(255,0,0),}, value='Input Player names')

		@self.new_player_form.bind(('input_player1', 'input_player2'), 'blur', this=True)
		def check_form(this=True):
			if len(this.value) < 3:
				this.set_style({'border_color':(255, 0, 0)})
			else:
				this.set_style({'border_color':(255, 255, 255)})

		@self.new_player_form.bind(('input_player1', 'input_player2'), 'focus')
		def reset_error_message():
			self.new_player_form.delete_unit('error_message')

		self.new_player_form.on("quit_button", "click", pygame.event.post, (pygame.event.Event(pygame.QUIT)))
		
	def handle(self, event): 
		self.new_player_form.handle(event)
		return self._state
	

class EndRoundManager:
	def __init__(self, players, winner, window):
		self._state = False
		self._screen = window
		if winner != None:
			label = "Game over! " + players[winner].name + " Win!"
		else:
			label = "Draw game!"

		self.end_round_form = forms.Form(window, name="endround")
		self.end_round_form.append_unit(forms.Button, 'start_button', (100, 500), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Restart")
		self.end_round_form.append_unit(forms.Button, 'quit_button', (300, 500), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Quit game")
		self.end_round_form.append_unit(forms.Label, 'label1', (100,450), style={'padding':5}, value=label)

		@self.end_round_form.bind('start_button', 'click', )
		def restart():
			self._state = "init_round"
			return "init_round"

		self.end_round_form.on("quit_button", "click", pygame.event.post, (pygame.event.Event(pygame.QUIT)))
		
	def handle(self, event): 
		self.end_round_form.handle(event)
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
		self.field_size = int()
		self.players = [None, None]
		pygame.init()
		pygame.display.set_caption("Cross and Zero")
		self.router("init_game")

	def router(self, state):
		if state == "init_game":
			self._handler = GameInitManager(self.players, self._screen)
		elif state == "init_round":
			if type(self._handler) == GameInitManager: #duct tape
				self.field_size = self._handler.field_size
			self._round_number += 1
			print(self.field_size)
			self._handler = GameRoundManager(self.players, self.field_size, self._screen)
		elif state == "end_round":
			winner = self._handler.get_winner()
			self._handler = EndRoundManager(self.players, winner, self._screen)
		else:
			return False

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

