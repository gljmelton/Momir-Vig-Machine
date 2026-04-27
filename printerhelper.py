import scryfall
import textwrap
import time
import struct
from thermalprinter.constants import Command
from scryfall import Face

def print_card(printer, card):
    print_card_face(printer, card, Face.FRONT)
    if scryfall.is_card_true_double_face(card):
        print_card_face(printer, card, Face.BACK)
    
    printer.feed(2)

def print_card_face(printer, card, face):
    printer.feed()
    if face is Face.BACK:
        printer.out("-"*32)
    printer.out(scryfall.get_title_line_for_card(card, face), bold=True)
    if face is Face.FRONT:
        printer.image(scryfall.get_image_for_card(card))
    printer.feed()
    printer.out(textwrap.fill(scryfall.get_type_line_for_card(card, face), 32), bold=True)
    printer.feed()
    oracle_text = scryfall.get_oracle_text_for_card(card, face)
    for p in oracle_text.splitlines():
        printer.out(textwrap.fill(p, 32))
        printer.feed()
    printer.feed()
    printer.out(scryfall.get_set_and_stat_line_for_card(card, face))

def custom_image(printer, image):
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