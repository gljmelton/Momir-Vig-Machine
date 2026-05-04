from thermalprinter.constants import Command
from thermalprinter import ThermalPrinter
import time
import struct

class Printer:
    def __init__(self):
        pass

    def feed(self, lines=1):
        pass

    def image(self, img):
        pass

    def out(self, text):
        pass

class ThermPrinter(Printer):
    def __init__(self):
        super().__init__()
        self.printer = ThermalPrinter(port="/dev/serial0", baudrate=9600, most_heated_point=3)
        time.sleep(2)

    def feed(self, lines=1):
        self.printer.feed(lines)

    def out(self, text, **kwargs):
        bold_override = kwargs.get("bold", False)
        self.printer.out(text, bold=bold_override)

    def image(self, img):
        self._custom_image(img)

    def _custom_image(self, image):
        bitmap = self.printer.image_chunks(image)
        width, height = image.size
        row_bytes = int((width + 7) / 8)  # Round up to next byte boundary

        self.printer.send_command(
            Command.GS,
            118,
            48,
            0,
            int(row_bytes % 256),
            int(row_bytes / 256),
            int(height % 256),
            int(height / 256),
        )
        print(" >>> WRITE %s bytes of image data", f"{len(bitmap):,}")
        for bit in bitmap:
            self.printer.write(struct.pack("B", bit), should_log=False)

        time.sleep(height / self.printer._line_spacing * self.printer._dot_print_time)

class CMDPrinter(Printer):
    def __init__(self):
        super().__init__()

    def out(self, text, **kwargs):
        print(">> " + text)