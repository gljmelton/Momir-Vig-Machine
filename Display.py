from LCD import LCD

class Display:
    def __init__(self):
        pass

    def update_display(self, text, line=1):
        pass

    def clear(self):
        pass

class LCDDisplay(Display):
    def __init__(self):
        self.lcd = LCD(i2c_addr = 0x27, backlight=True)
        super().__init__()

    def update_display(self, text, line=1):
        self.lcd.message(text, line)
    
    def clear(self):
        self.lcd.clear()

class CMDDisplay(Display):
    def update_display(self, text, line=1):
        print(f"{line}: {text}")