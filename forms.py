import pygame

COLOR_WHITE = 255, 255, 255
COLOR_KEY = 0, 0, 0

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

#default style
STYLE = {'padding':0, 'margin':0, 'border':0,'border_color':(255,255,255), 'bg_color':None, 'text_color':(255,255,255), 'text_align':'left', 'font':None, 'font_size':32}
#if font not none, place font to programm folder or set full font path like /usr/share/fonts/truetype/msttcorefonts/Arial.ttf 

class Form: #shapeless conteiner
	def __init__(self, surface_to_draw, name=''):
		self.surface_to_draw = surface_to_draw
		self._units = dict()
		self.data = dict()
		pass

	def append_unit(self, unit_type, unit_name, position=(0,0), size=(0,0), style={}, value='', placeholder=None):
		if unit_name not in self._units:
			self._units[unit_name] = unit_type(self.surface_to_draw, position, size, style, value = value, placeholder=placeholder)
		else:
			print("unit with name is exist")
			return False

	def set_style(self, unit_name, style):
		if unit_name in self._units.keys():
			self._units[unit_name].set_style(style)
		else:
			return False

	def on(self, unit_name, event, fn, to_return=False, *args):
		#TODO if unit_name is tuple map to all
		if unit_name in self._units.keys():
			self._units[unit_name].on(event, fn, to_return, *args)
		else:
			return False

	def data_collect(self):
		for unit_name, unit in self._units.items():
			self.data[unit_name] = unit.get_value()
		return self.data

	def handle(self, event):
		for unit in self._units.values():
			unit.handle_event(event)


class Input:
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='', placeholder=None):
		self.surface_to_draw = surface_to_draw
		self.style = dict(STYLE) # set base style
		if hasattr(self, 'default_style'): # set default style for children class
			self.style.update(self.default_style)
		self.style.update(style) # add user style
		
		self.value = value
		self.placeholder = placeholder
		self.focus = False
		self.down = False
		self.hover = False
		self.font = pygame.font.Font(self.style['font'], self.style['font_size'])

		self.on_click_args = list()
		self.on_mousedown_args = list()
		self.on_mouseup_args = list()
		self.on_keydown_args = list()
		self.on_keyup_args = list()
		self.on_mousein_args = list()
		self.on_mouseout_args = list()

		self.txt_surface = self.font.render(self.value, True, self.style['text_color'])
		width = self.txt_surface.get_width() + self.style['padding'] * 2 if size[0] == 0 else size[0]
		height = self.txt_surface.get_height() + self.style['padding'] * 2 if size[1] == 0 else size[1]
		self.surface = pygame.Surface((width,height))
		#self.surface.set_colorkey(COLOR_KEY) # fill issue
		self.rectangle = self.surface.get_rect()
		self.rectangle.topleft = position
		#self.draw()

	def handle_event(self, event):
		return False

	def get_value(self):
		return self.value

	#TODO make decorator
	def on(self, event, fn, *args):
		if event == "click":
			self.on_click_callback = fn
			self.on_click_args = args
		elif event == "mousedown":
			self.on_mousedown_callback = fn
			self.on_mousedown_args = args		
		elif event == "mouseup":
			self.on_mouseup_callback = fn
			self.on_mouseup_args = args
		elif event == "keydown":
			self.on_keydown_callback = fn
			self.on_keydown_args = args
		elif event == "keyup":
			self.on_keyup_callback = fn
			self.on_keyup_args = args
		elif event == "mousein":
			self.on_mousein_callback = fn
			self.on_mousein_args = args
		elif event == "mouseout":
			self.on_mouseout_callback = fn
			self.on_mouseout_args = args
		else:
			print ("Unknown event", event)
			return False

		"""
		click
		mousemove
		wheel
		hover
		mouseover
		mouseout
		focus (focusin)
		blur (focusout)
		change
		input (для текстовых элементов формы)
		select
		submit
		"""

	def on_click(self, mousebutton):
		if callable(self.on_click_callback):
			state = self.on_click_callback(*self.on_click_args)
			return state
	
	def on_click_callback(self, *args):
		return False

	def on_mousedown(self, mousebutton):
		if callable(self.on_mousedown_callback):
			state = self.on_mousedown_callback(*self.on_mousedown_args)
			return state

	def on_mousedown_callback(self, *args):
		return False

	def on_mouseup(self, mousebutton):
		if callable(self.on_mouseup_callback):
			state = self.on_mouseup_callback(*self.on_mouseup_args)
			return state

	def on_mouseup_callback(self, *args):
		return False

	def on_keydown(self):
		if callable(self.on_keydown_callback):
			state = self.on_keydown_callback(*self.on_keydown_args)
			return state
		
	def on_keydown_callback(self, *args):
		return False

	def on_keyup(self):
		if callable(self.on_keyup_callback):
			state = self.on_keyup_callback(*self.on_keyup_args)
			return state

	def on_keyup_callback(self, *args):
		return False

	def draw(self):
		# Fill background
		if 'bg_color_active' in self.style.keys() and self.down:
			bg_color = self.style['bg_color_active']
		elif 'bg_color_hover' in self.style.keys() and self.hover:
			bg_color = self.style['bg_color_hover']
		elif 'bg_color_focused' in self.style.keys() and self.focus:
			bg_color = self.style['bg_color_focused']
		else:
			bg_color = self.style['bg_color']
		if bg_color != None:
			self.surface.fill(bg_color)
		else:
			self.surface.fill(COLOR_KEY) 

		# Blit the border.
		if self.style['border'] > 0:
			if 'border_color_actve' in self.style.keys() and self.down:
				border_color = self.style['border_color_actve']
			elif 'border_color_hover' in self.style.keys() and self.hover:
				border_color = self.style['border_color_hover']
			elif 'border_color_focus' in self.style.keys() and self.focus:
				border_color = self.style['border_color_focus']
			else:
				border_color = self.style['border_color']
			pygame.draw.rect(self.surface, border_color, (0,0, self.rectangle.w, self.rectangle.h), self.style['border'])

		# Blit the text.
		if self.style['text_align'] == 'center':
			self.surface.blit(self.txt_surface, self.txt_surface.get_rect(center = (self.rectangle.w/2, self.rectangle.h/2)))
		elif self.style['text_align'] == 'right':
			pass
		else:
			self.surface.blit(self.txt_surface, (self.style['padding'], self.style['padding']))
		self.surface_to_draw.blit(self.surface, self.rectangle)
	# end class input

class InputBox(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='', placeholder=None):
		self.default_style = {'border':1, 'border_color':COLOR_INACTIVE, 'border_color_focus':COLOR_ACTIVE}
		super().__init__(surface_to_draw, position, size, style, value, placeholder)
		self.draw()

	def on_keydown(self, key, unicode): # Re-render the text.
		if key == pygame.K_RETURN:
			self.focus = False
		elif key == pygame.K_BACKSPACE:
			self.value = self.value[:-1]
		else:
			self.value += unicode
		self.txt_surface = self.font.render(self.value, True, self.style['text_color'])
		super().on_keydown()

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the input_box rect.
			if self.rectangle.collidepoint(event.pos):
				# Toggle the active variable.
				self.focus = True
				#self.on_focus()
			else:
				self.focus = False
				#self.on_blur()
		if event.type == pygame.KEYDOWN:
			if self.focus:
				self.on_keydown(event.key, event.unicode)
		self.draw()

	def update(self):
		# Resize the box if the text is too long.
		width = max(200, self.txt_surface.get_width()+10)
		self.rectangle.w = width


class Button(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='', placeholder=None):
		self.default_style = {'border':1, 'text_align':'center', 'bg_color': COLOR_INACTIVE, 'bg_color_active': COLOR_ACTIVE}
		super().__init__(surface_to_draw, position, size, style, value)
		self.draw()

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rectangle.collidepoint(event.pos):
				# If the user clicked on the button rect.
				# Toggle the active variable.
				self.on_mousedown(event.button)
				self.down = True
			else:
				self.down = False

		if event.type == pygame.MOUSEBUTTONUP and (self.down == True or self.rectangle.collidepoint(event.pos)):
				#when the user released the button, it is necessary to call the processing of some event
				self.down = False
				self.on_click(event.button)
				#self.on_moseup(event.button)

		if event.type == pygame.MOUSEMOTION:
			if self.rectangle.collidepoint(event.pos):
				if self.hover == False:
					#self.on_mousein()
					self.hover = True
			else:
				if self.down == True:
					# If the user move out from button rect with downed button.
					self.down = False
				if self.hover == True:
					#self.on_mouseout()
					self.hover = False
		self.draw()


class Label(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='', placeholder=None):
		self.default_style = {'border':0} # set base style
		super().__init__(surface_to_draw, position, size, style, value)
		self.draw()

	def get_value(self):
		return None

	def set_value(self, value):
		self.value = value
		position = self.rectangle.topleft
		self.txt_surface = self.font.render(self.value, True, self.style['text_color'])
		width = self.txt_surface.get_width() + self.style['padding'] * 2 if size[0] == 0 else size[0]
		height = self.txt_surface.get_height() + self.style['padding'] * 2 if size[1] == 0 else size[1]
		self.surface = pygame.Surface((width, height))
		self.surface.set_colorkey(COLOR_KEY)
		self.rectangle = self.surface.get_rect()
		self.rectangle.topleft = position
		self.draw()

