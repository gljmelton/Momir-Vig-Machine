import configparser
import gpiozero
import platform

is_windows = platform.system() == 'Windows'
if is_windows:
    try:
        import keyboard
    except ImportError:
        keyboard = None
else:
    keyboard = None

class Input:
    up_pressed_callback = None
    down_pressed_callback = None
    enter_pressed_callback = None

    def __init__(self):
        pass

    def up_pressed(self, *args):
        if self.up_pressed_callback:
            self.up_pressed_callback()

    def down_pressed(self, *args):
        if self.down_pressed_callback:
            self.down_pressed_callback()

    def enter_pressed(self, *args):
        if self.enter_pressed_callback:
            self.enter_pressed_callback()

    def clear_callbacks(self) -> None:
        self.up_pressed_callback = None
        self.down_pressed_callback = None
        self.enter_pressed_callback = None

class GPIOInput(Input):
    config = configparser.ConfigParser()
    config.read('config.ini')
    UP_BUTTON_PIN = config.getint('GPIO', 'up_button_pin')
    DOWN_BUTTON_PIN = config.getint('GPIO', 'down_button_pin')
    ENTER_BUTTON_PIN = config.getint('GPIO', 'enter_button_pin')
    BUTTON_BOUNCE_TIME = config.getfloat('GPIO', 'button_bounce_time')

    def __init__(self):
        super().__init__()
        self.up_button = gpiozero.Button(self.UP_BUTTON_PIN, bounce_time=self.BUTTON_BOUNCE_TIME)
        self.down_button = gpiozero.Button(self.DOWN_BUTTON_PIN, bounce_time=self.BUTTON_BOUNCE_TIME)
        self.enter_button = gpiozero.Button(self.ENTER_BUTTON_PIN, bounce_time=self.BUTTON_BOUNCE_TIME)

        self.up_button.when_pressed = self.up_pressed
        self.down_button.when_pressed = self.down_pressed
        self.enter_button.when_pressed = self.enter_pressed

class CMDInput(Input):
    def __init__(self):
        super().__init__()
        keyboard.on_press_key(keyboard.KEY_UP, self.up_pressed)
        keyboard.on_press_key(keyboard.KEY_DOWN, self.down_pressed)
        keyboard.on_press_key('right', self.enter_pressed)