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
        super().__init__()
        self.lcd = LCD(i2c_addr = 0x27, backlight=True)

    def update_display(self, text, line=1):
        print("Updating lcd display")
        self.lcd.message(text, line)
    
    def clear(self):
        self.lcd.clear()

class CMDDisplay(Display):
    def update_display(self, text, line=1):
        print(f"{line}: {text}")