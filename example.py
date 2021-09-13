import pygame
import forms

def main():
	FPS = 30
	COLOR_INACTIVE = pygame.Color('lightskyblue3')
	COLOR_ACTIVE = pygame.Color('dodgerblue2')
	size = 800,600
	window = pygame.display.set_mode(size)
	window.fill(0)
	clock = pygame.time.Clock()
	pygame.init()
	data = dict()

	form = forms.Form(window, name='form')
	form.append_unit(forms.InputBox, 'input1', (260, 100), size=(200, 32), style={'padding':5}, placeholder="Input name")
	form.append_unit(forms.InputBox, 'input2', (260, 150), size=(200, 32), style={'padding':5}, placeholder="Input name")
	form.append_unit(forms.Button, 'start_button', (100, 300), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Start")
	form.append_unit(forms.Button, 'quit_button', (300, 300), size=(120, 0), style={'padding':5, 'bg_color':COLOR_INACTIVE}, value="Quit game")
	form.append_unit(forms.Label, 'label1', (100,100), style={'padding':5}, value='Value 1')
	form.append_unit(forms.Label, 'label2', (100,150), style={'padding':5}, value='Value 2')
	form.append_unit(forms.RadioGroup, 'radio')
	form.get_unit('radio').append_unit('radio1', (260,208), checked=True, value=3)
	form.get_unit('radio').append_unit('radio2', (360,208), value=4)
	form.get_unit('radio').append_unit('radio3', (460,208), checked=False, value=5)
	form.append_unit(forms.Label, 'fielsize', (100,200), style={'padding':5}, value='Field size:')
	form.append_unit(forms.Label, 'radio3x3', (280,200), style={'padding':5}, value='3x3')
	form.append_unit(forms.Label, 'radio4x4', (380,200), style={'padding':5}, value='4x4')
	form.append_unit(forms.Label, 'radio5x5', (480,200), style={'padding':5}, value='5x5')
	form.append_unit(forms.CheckBox, 'check', (100,350))

	@form.bind('start_button', 'click', data)
	def create_user(players):
		data = form.data_collect()
		if len(data['input1']) > 2 and len(data['input2']) > 2:
			text = "Hello " + data['input1'] + " and " + data['input2'] + ". selected = " + str(data['radio'])
			form.append_unit(forms.Label, 'error_message', (100,250), style={'padding':5,'text_color':(0,255,0)}, value=text)	
		else:
			form.append_unit(forms.Label, 'error_message', (100,250), style={'padding':5,'text_color':(255,0,0)}, value='Input values')

	@form.bind(('input1', 'input2'), 'blur', this=True)
	def check_form(this=True):
		if len(this.value) < 3:
			this.set_style({'border_color':(255, 0, 0)})
		else:
			this.set_style({'border_color':(255, 255, 255)})

	@form.bind(('input1', 'input2'), 'focus')
	def reset_error_message():
		form.delete_unit('error_message')

	form.on("quit_button", "click", pygame.event.post, (pygame.event.Event(pygame.QUIT)))

	quit = False
	while not quit:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
			elif event.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
				form.handle(event)
		pygame.display.flip()	
	print("Game over!")

if __name__ == '__main__':
	main()  
