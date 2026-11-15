from LCD import LCD

class Display:
    update_display_callback = None
    clear_callback = None

    def __init__(self):
        pass

    def update_display(self, text, line=1):
        if self.update_display_callback:
            self.update_display_callback(text, line)

    def clear(self):
        if self.clear_callback:
            self.clear_callback()

class LCDDisplay(Display):
    def __init__(self):
        super().__init__()
        self.lcd = LCD(i2c_addr = 0x27, backlight=True)

    def update_display(self, text, line=1):
        self.lcd.message(text, line)
    
    def clear(self):
        self.lcd.clear()

class CMDDisplay(Display):
    def update_display(self, text, line=1):
        print(f"{line}: {text}")