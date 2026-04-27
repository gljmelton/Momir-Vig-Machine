import scryfall
import printerhelper
import random
import time
from Display import Display, LCDDisplay, CMDDisplay
from Input import Input, CMDInput, GPIOInput
from Printer import Printer, ThermPrinter, CMDPrinter
import argparse

parser = argparse.ArgumentParser("printer_test")
parser.add_argument("--cmd", help="Uses the commandline to display instead if screen", action="store_true")
args = parser.parse_args()

vig_states = {
    "Init": 0,
    "ChooseCMC": 1,
    "SelectCard": 2,
    "PrintCard": 3
}

target_cmc = 1
min_cmc = 1
max_cmc = 1
displayHandler = Display()
inputHandler = Input()
printerHandler = Printer()

card_list = []
current_state = vig_states["Init"]
selected_card = None

if args.cmd is True:
    print ("Creating CMD services")
    display = CMDDisplay()
    inputHandler = CMDInput()
    printerHandler = CMDPrinter()
else:
    print("Creating hardware services")
    display = LCDDisplay()
    inputHandler = GPIOInput()
    printerHandler = ThermPrinter()

#Helper functions
def set_max_cmc():
    global max_cmc
    for card in card_list:
        if 'cmc' in card and card['cmc'] > max_cmc:
            max_cmc = card['cmc']

def get_random_card_for_cmc():
    valid_cmc_cards = [card for card in card_list if 'cmc' in card and card['cmc'] == target_cmc]
    if len(valid_cmc_cards) == 0:
        print("No valid CMC card found!")
        return None

    return valid_cmc_cards[random.randint(0, len(valid_cmc_cards)-1)]

def switch_state(new_state):
    global current_state

    #On exit functions
    if current_state == vig_states["Init"]:
        pass
    elif current_state == vig_states["ChooseCMC"]:
        exit_choose_cmc_state()
    elif current_state == vig_states["SelectCard"]:
        pass
    elif current_state == vig_states["PrintCard"]:
        pass

    #On enter functions
    if new_state == vig_states["Init"]:
        pass
    elif new_state == vig_states["ChooseCMC"]:
        enter_choose_cmc_state()
    elif new_state == vig_states["SelectCard"]:
        select_card()
    elif new_state == vig_states["PrintCard"]:
        print_card()

    print(f'Switching from state {current_state} to {new_state}...')
    current_state = new_state
#####################

#Init
def init_vig():
    print("Initializing...")

    displayHandler.update_display("Initializing", 1)
    displayHandler.update_display("data...", 2)
    printerHandler.feed()
    printerHandler.out("Welcome to Momir Vig Machine!")
    printerHandler.feed(2)
    global card_list
    card_list = scryfall.get_filtered_cards()
    set_max_cmc()

    print('Initialization complete!')
    displayHandler.update_display("Complete!", 2)

    switch_state(vig_states["ChooseCMC"])
##############

#Choose CMC state
def increase_target_cmc():
    global target_cmc
    if target_cmc < max_cmc:
        target_cmc += 1
    else:
        target_cmc = max_cmc
    
    print(f'Target CMC set to {int(target_cmc)}!')
    displayHandler.clear()
    displayHandler.update_display(f'Target CMC: {int(target_cmc)}  ', 1)

def decrease_target_cmc():
    global target_cmc
    if target_cmc > min_cmc:
        target_cmc -= 1
    else:
        target_cmc = min_cmc
    
    print(f'Target CMC set to {int(target_cmc)}!')
    displayHandler.clear()
    displayHandler.update_display(f'Target CMC: {int(target_cmc)}  ', 1)

def print_target_cmc():
    switch_state(vig_states["SelectCard"])

def enter_choose_cmc_state():
    print("Entering choose CMC state...")
    
    displayHandler.clear()
    displayHandler.update_display(f'Target CMC: {int(target_cmc)}  ', 1)
    
    #Bind increase button
    inputHandler.up_pressed_callback = increase_target_cmc
    inputHandler.down_pressed_callback = decrease_target_cmc
    inputHandler.enter_pressed_callback = print_target_cmc
    
def exit_choose_cmc_state():
    print("Exiting choose CMC state...")
    inputHandler.clear_callbacks()

def choose_cmc():
    pass
#################

#Select card state
def select_card():
    print("Entering select card state...")
    displayHandler.clear()
    displayHandler.update_display("Selecting card...", 1)
    global selected_card
    selected_card = get_random_card_for_cmc()
    displayHandler.clear()
    if selected_card is None:
        print(f'No cards at cmc {int(target_cmc)}!')
        displayHandler.update_display("No cmc {int(target_cmc)} cards!", 1)
        switch_state(vig_states["ChooseCMC"])
    else:
        displayHandler.update_display(f'Chosen card:', 1)
        displayHandler.update_display(f'{selected_card["name"]}  ', 2)
        print(f'Chosen card: {selected_card["name"]}')
        switch_state(vig_states["PrintCard"])
######################

#Print card state
def print_card():
    print("Entering print card state...")
    #Print card here using printer library
    print("Sending print request to printer...")
    printerhelper.print_card(printerHandler, selected_card)
    print("Print sent!")
    switch_state(vig_states["ChooseCMC"])
##################

def update_vig():
    if current_state == vig_states["Init"]:
        init_vig()
    elif current_state == vig_states["ChooseCMC"]:
        pass


def main():
    while True:
        update_vig()

def cleanup():
    print("Cleaning up...")
    displayHandler.clear()

    displayHandler.update_display("Goodbye!", 1)
    time.sleep(2)
    displayHandler.clear()

#Main loop
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()