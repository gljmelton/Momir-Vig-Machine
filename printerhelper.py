import scryfall
import textwrap
import time
import struct
from thermalprinter.constants import Justify
from thermalprinter.constants import Command
from scryfall import Face

def printcard(printer, card):
    printcardface(printer, card, Face.FRONT)
    if scryfall.iscardtruedoubleface(card):
        printcardface(printer, card, Face.BACK)
    
    printer.feed(2)

def printcardface(printer, card, face):
    printer.feed()
    if face is Face.BACK:
        printer.out("-"*32)
    printer.out(scryfall.gettitlelineforcard(card), bold=True)
    if face is Face.FRONT:
        customimage(printer, scryfall.getimageforcard(card))
    printer.feed()
    printer.out(textwrap.fill(scryfall.gettypelineforcard(card), 32), bold=True)
    printer.feed()
    oracletext = scryfall.getoracletextforcard(card)
    for p in oracletext.splitlines():
        printer.out(textwrap.fill(p, 32))
        printer.feed()
    printer.feed()
    printer.out(scryfall.getstatlineforcard(card), justify=Justify.RIGHT)

def customimage(printer, image):
    bitmap = printer.image_chunks(image)
    width, height = image.size
    row_bytes = int((width + 7) / 8)  # Round up to next byte boundary

    printer.send_command(
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
        printer.write(struct.pack("B", bit), should_log=False)

    time.sleep(height / printer._line_spacing * printer._dot_print_time)