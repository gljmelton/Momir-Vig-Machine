#https://thermalprinter.readthedocs.io/usage.html#instantiate-the-class
from thermalprinter import ThermalPrinter

printer = ThermalPrinter(port="/dev/serial0", baudrate=9600)

printer.out("Show time, here comes the demonstration!")
printer.feed()
printer.demo()