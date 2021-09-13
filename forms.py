import pygame

COLOR_WHITE = 255, 255, 255
COLOR_KEY = 0, 0, 0

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

#default style
#if font not none, place font to programm folder or set full font path like /usr/share/fonts/truetype/msttcorefonts/Arial.ttf 
STYLE = {'padding':0, 'margin':0, 'border':0,'border_color':(255,255,255), 'bg_color':None, 'text_color':(255,255,255), 'text_align':'left', 'font':None, 'font_size':32}


class Form: #shapeless conteiner
	def __init__(self, surface_to_draw, name=''):
		self.surface_to_draw = surface_to_draw
		self._units = dict()
		self._data = dict()
		self._response = dict()

	def append_unit(self, unit_type, unit_name, position=(0,0), **kwargs):
		if unit_name not in self._units:
			self._units[unit_name] = unit_type(self.surface_to_draw, position, **kwargs)
		else:
			print("element with name ", unit_name, "is exist")

	def delete_unit(self, unit_name):
		if unit_name in self._units.keys():
			self._units[unit_name].clear()
			self._units.pop(unit_name, False)
		else:
			return False

	def get_unit(self, unit_name):
		if unit_name in self._units.keys():
			return self._units[unit_name]

	def set_style(self, unit_name, style):
		if unit_name in self._units.keys(): # add if list
			if type(self._units[unit_name]) is list:
				print("I don't know how set style for element with not unique name yet")
			else:
				self._units[unit_name].set_style(style)
		else:
			return False

	def on(self, unit_name, event, fn, *args, **kwargs):
		if type(unit_name) in (tuple, list):
			for name in unit_name:
				if name in self._units.keys():
					self._units[name].on(event, fn, *args, **kwargs)				
		else:
			if unit_name in self._units.keys():
				self._units[unit_name].on(event, fn, *args, **kwargs)
			else:
				return False

	def bind(self, unit_name, event, *args, **kwargs):
		def decorator(fn):
			self.on(unit_name, event, fn, *args, **kwargs)
			return fn
		return decorator

	def data_collect(self):
		for unit_name, unit in self._units.items():
			value = unit.get_value()
			if value != False:
				self._data[unit_name] = value
		return self._data

	def handle(self, event):
		self._response = dict()
		#for unit in self._units.values():
		#	unit.handle_event(event)
		unit_names = list(self._units.keys()) #duct tape for "RuntimeError: dictionary changed size during iteration"
		for name in unit_names:
			if name in self._units: #duct tape for delete unit on the go
				response = self._units[name].handle(event)
				if response:
					self._response[name] = response


class RadioGroup(Form):
	def __init__(self, surface_to_draw, name=''):
		super().__init__(surface_to_draw, name='')
		self._data = False

	def append_unit(self, unit_name, position=(0,0), **kwargs):
		super().append_unit(RadioButton, unit_name, position, **kwargs)
		if 'checked' in kwargs and kwargs['checked']:
			self.recheck(unit_name)

	def get_value(self):
		return self.data_collect()

	def data_collect(self):
		for unit_name, unit in self._units.items():
			value = unit.get_value()
			if value != False:
				self._data = value
		return self._data

	def clear(self):
		for unit in self._units.values():
			unit.clear()

	def recheck(self, unit_name):
		for name, unit in self._units.items():
			if name != unit_name:
				unit.uncheck()

	def handle(self, event):
		super().handle(event)
		if len(self._response) > 0:
			for unit_name, response in self._response.items():
				if response == 'checked':
					self.recheck(unit_name)


class Input:
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='', hidden=False):
		self.surface_to_draw = surface_to_draw
		self.style = dict(STYLE) # set base style
		if hasattr(self, 'default_style'): # set default style for children class
			self.style.update(self.default_style)
		self.style.update(style) # add user style
		
		self.value = value
		self.focused = False
		self.downed = False
		self.hovered = False
		self.callback = dict()
		self.callback_args = dict()
		self.callback_kwargs = dict()
		self.font = pygame.font.Font(self.style['font'], self.style['font_size'])
		self.txt_surface = self.font.render(str(self.value), True, self.style['text_color'])
		width = self.txt_surface.get_width() + self.style['padding'] * 2 if size[0] == 0 else size[0]
		height = self.txt_surface.get_height() + self.style['padding'] * 2 if size[1] == 0 else size[1]
		self.surface = pygame.Surface((width, height))
		#self.surface.set_colorkey(COLOR_KEY) #fill issue
		self.rectangle = self.surface.get_rect()
		self.rectangle.topleft = position
		#self.draw()

	def set_style(self, style):
		self.style.update(style)

	def clear(self):
		self.surface.fill(COLOR_KEY) 
		self.surface_to_draw.blit(self.surface, self.rectangle)

	def handle(self, event):
		response = False
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rectangle.collidepoint(event.pos):
				response = self.mousedown(event.button)
			elif self.focused:
				response = self.blur()
		if event.type == pygame.MOUSEBUTTONUP and self.downed == True:
				response = self.click(event.button)
				response = self.mouseup(event.button)
		if event.type == pygame.MOUSEMOTION:
			if self.rectangle.collidepoint(event.pos):
				if not self.hovered:
					response = self.mousein()
			else:
				if self.hovered:
					response = self.mouseout()
		if event.type == pygame.KEYDOWN and self.focused:
			response = self.keydown(event.key, event.unicode)
		self.draw()
		if response:
			return response 

	def get_value(self):
		return self.value

	def bind(self, unit_name, event, *args, **kwargs):
		def decorator(fn):
			self.on(event, fn, *args, **kwargs)
			return fn
		return decorator

	def on(self, event, fn, *args, **kwargs):
		if 'this' in kwargs:
			kwargs['this'] = self
		self.callback[event] = fn
		self.callback_args[event] = args
		self.callback_kwargs[event] = kwargs

		"""
		mousemove, wheel, change, input (для текстовых элементов формы), select, submit
		"""
	def click(self, mousebutton):
		#here maybe another code
		view_function = self.callback.get("click")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("click"), **self.callback_kwargs.get("click"))

	def mousedown(self, mousebutton):
		#here maybe another code
		self.downed = True
		if not self.focused:
			self.focus()
		view_function = self.callback.get("mousedown")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("mousedown"), **self.callback_kwargs.get("mousedown"))

	def mouseup(self, mousebutton):
		#here maybe another code
		self.downed = False
		view_function = self.callback.get("mouseup")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("mouseup"), **self.callback_kwargs.get("mouseup"))

	def mousein(self):
		#here maybe another code
		self.hovered = True
		view_function = self.callback.get("mousein")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("mousein"), **self.callback_kwargs.get("mousein"))

	def mouseout(self):
		#here maybe another code
		self.hovered = False
		self.downed = False
		view_function = self.callback.get("mouseout")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("mouseout"), **self.callback_kwargs.get("mouseout"))

	def keydown(self, key, unicode):
		#here maybe another code
		view_function = self.callback.get("keydown")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("keydown"), **self.callback_kwargs.get("keydown"))

	def keyup(self, key):
		#here maybe another code
		view_function = self.callback.get("keyup")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("keyup"), **self.callback_kwargs.get("keyup"))

	def focus(self):
		#here maybe another code
		self.focused = True
		view_function = self.callback.get("focus")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("focus"), **self.callback_kwargs.get("focus"))

	def blur(self):
		#here maybe another code
		self.focused = False
		self.downed = False
		view_function = self.callback.get("blur")
		if view_function and callable(view_function):
			return view_function(*self.callback_args.get("blur"), **self.callback_kwargs.get("blur"))

	def draw(self):
		# Fill background
		if 'bg_color_active' in self.style.keys() and self.downed:
			bg_color = self.style['bg_color_active']
		elif 'bg_color_hover' in self.style.keys() and self.hovered:
			bg_color = self.style['bg_color_hover']
		elif 'bg_color_focused' in self.style.keys() and self.focused:
			bg_color = self.style['bg_color_focused']
		else:
			bg_color = self.style['bg_color']
		if bg_color != None:
			self.surface.fill(bg_color)
		else:
			self.surface.fill(COLOR_KEY) 

		# Blit the border.
		if self.style['border'] > 0:
			if 'border_color_actve' in self.style.keys() and self.downed:
				border_color = self.style['border_color_actve']
			elif 'border_color_hover' in self.style.keys() and self.hovered:
				border_color = self.style['border_color_hover']
			elif 'border_color_focus' in self.style.keys() and self.focused:
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
		super().__init__(surface_to_draw, position, size, style, value)
		self.placeholder = placeholder
		self.draw()

	def keydown(self, key, unicode): # Re-render the text.
		super().keydown(key, unicode)
		if key == pygame.K_RETURN:
			self.blur()
		elif key == pygame.K_BACKSPACE:
			self.value = self.value[:-1]
		else:
			self.value += unicode
		self.txt_surface = self.font.render(self.value, True, self.style['text_color'])

	def update(self): # need refactoring
		# Resize the box if the text is too long.
		width = max(200, self.txt_surface.get_width()+10)
		self.rectangle.w = width


class Button(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='Button'):
		self.default_style = {'border':1, 'border_color_hover':COLOR_ACTIVE,'text_align':'center', 'bg_color': COLOR_INACTIVE, 'bg_color_active': COLOR_ACTIVE}
		super().__init__(surface_to_draw, position, size, style, value)
		self.draw()

class RadioButton(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=16, style={}, value='', checked=False):
		self.default_style = {'border':2, 'border_color':COLOR_INACTIVE, 'border_color_actve':COLOR_ACTIVE}
		super().__init__(surface_to_draw, position, (size, size), style, value)
		self._checked = checked
		self.draw()

	def uncheck(self):
		self._checked = False
		self.draw()

	def get_value(self):
		if self._checked:
			return self.value
		else:
			return False

	def mouseup(self, mousebutton):
		super().mouseup(mousebutton)
		if self._checked == False:
			self._checked = True
			return 'checked'

	def draw(self):
				# Fill background
		if 'bg_color_active' in self.style.keys() and self.downed:
			bg_color = self.style['bg_color_active']
		elif 'bg_color_hover' in self.style.keys() and self.hovered:
			bg_color = self.style['bg_color_hover']
		elif 'bg_color_focused' in self.style.keys() and self.focused:
			bg_color = self.style['bg_color_focused']
		else:
			bg_color = self.style['bg_color']
		if bg_color != None:
			self.surface.fill(bg_color)
		else:
			self.surface.fill(COLOR_KEY) 

		# Blit the border.
		if 'border_color_actve' in self.style.keys() and self.downed:
			border_color = self.style['border_color_actve']
		elif 'border_color_hover' in self.style.keys() and self.hovered:
			border_color = self.style['border_color_hover']
		elif 'border_color_focus' in self.style.keys() and self.focused:
			border_color = self.style['border_color_focus']
		else:
			border_color = self.style['border_color']
		pygame.draw.circle(self.surface, border_color, (self.rectangle.width/2, self.rectangle.height/2), (self.rectangle.height/2), width = self.style['border'])

		if self._checked:
			pygame.draw.circle(self.surface, border_color, (self.rectangle.width/2, self.rectangle.height/2), (self.rectangle.height/2 - self.style['border']*2) )
		self.surface_to_draw.blit(self.surface, self.rectangle)


class CheckBox(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=16, style={}, value='', checked=False):
		self.default_style = {'border':1, 'border_color':COLOR_INACTIVE, 'border_color_actve':COLOR_ACTIVE}
		super().__init__(surface_to_draw, position, (size, size), style, value)
		self._checked = checked
		check_size = size - (self.style['border']*4)
		self.check_surface = pygame.Surface((check_size, check_size))
		self.check_surface.set_colorkey(COLOR_KEY) #fill issue
		pygame.draw.line(self.check_surface, COLOR_WHITE, (0, int(check_size-check_size/3-2)), (int(check_size/3), check_size-2), width=2)
		pygame.draw.line(self.check_surface, COLOR_WHITE, (int(check_size/3), check_size-2), (check_size, int(check_size/3-2)), width=2)
		self.check_rectangle = self.check_surface.get_rect()
		self.check_rectangle.center = (size/2, size/2)
		self.draw()

	def get_value(self):
		return self._checked

	def mouseup(self, mousebutton):
		super().mouseup(mousebutton)
		self._checked = not self._checked 
		return 'checked'

	def draw(self):
		# Fill background
		if 'bg_color_active' in self.style.keys() and self.downed:
			bg_color = self.style['bg_color_active']
		elif 'bg_color_hover' in self.style.keys() and self.hovered:
			bg_color = self.style['bg_color_hover']
		elif 'bg_color_focused' in self.style.keys() and self.focused:
			bg_color = self.style['bg_color_focused']
		else:
			bg_color = self.style['bg_color']
		if bg_color != None:
			self.surface.fill(bg_color)
		else:
			self.surface.fill(COLOR_KEY) 

		if self._checked:
			pygame.draw.rect(self.surface, self.style['border_color_actve'], (0,0, self.rectangle.w, self.rectangle.h))
			self.surface.blit(self.check_surface, self.check_rectangle)
		else:
			# Blit the border.
			if self.style['border'] > 0:
				if 'border_color_actve' in self.style.keys() and self.downed:
					border_color = self.style['border_color_actve']
				elif 'border_color_hover' in self.style.keys() and self.hovered:
					border_color = self.style['border_color_hover']
				elif 'border_color_focus' in self.style.keys() and self.focused:
					border_color = self.style['border_color_focus']
				else:
					border_color = self.style['border_color']
				pygame.draw.rect(self.surface, border_color, (0,0, self.rectangle.w, self.rectangle.h), self.style['border'])
		self.surface_to_draw.blit(self.surface, self.rectangle)


class Label(Input):
	def __init__(self, surface_to_draw, position=(0,0), size=(0,0), style={}, value='Label'):
		self.default_style = {'border':0} # set base style
		super().__init__(surface_to_draw, position, size, style, value)
		self.draw()

	def get_value(self):
		return False

	def handle(self, event):
		return False

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

