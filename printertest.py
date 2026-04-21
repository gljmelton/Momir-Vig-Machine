#https://thermalprinter.readthedocs.io/usage.html#instantiate-the-class
from thermalprinter import ThermalPrinter
import scryfall
import argparse
import printerhelper

imagecardid="0ab91962-ebad-46f6-9f90-7477c224d93d"
doublefacecardid="b3819a11-2f3e-4304-a1b0-6abf893c89c5"
adventurecardid="df9573a3-d013-4631-98ed-78418bf0bc78"
testcardid="6a0b230b-d391-4998-a3f7-7b158a0ec2cd"

parser = argparse.ArgumentParser("printer_test")
parser.add_argument("--image", help="Prints a test image", action="store_true")
parser.add_argument("--double_face", help="Prints a double-faced card", action="store_true")
parser.add_argument("--adventure", help="Prints an adventure for a pseudodoubleface card test", action="store_true")
parser.add_argument("--card", help="Prints a single-faced card", action="store_true")
args = parser.parse_args()

printer = ThermalPrinter(port="/dev/serial0", baudrate=9600, heat_time=160)

if args.image:
    imagecard = scryfall.getcardbyid(imagecardid)
    img = scryfall.getimageforcard(imagecard)
    printerhelper.customimage(printer, img)

if args.double_face:
    dfc = scryfall.getcardbyid(doublefacecardid)
    printerhelper.printcard(printer, dfc)

if args.adventure:
    adventure = scryfall.getcardbyid(adventurecardid)
    printerhelper.printcard(printer, adventure)

if args.card:
    card = scryfall.getcardbyid(testcardid)
    printerhelper.printcard(printer, card)