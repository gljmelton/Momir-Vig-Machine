import scryfall
import printerhelper
import random
import time
from Display import Display, LCDDisplay, CMDDisplay
from Input import Input, CMDInput, GPIOInput
from Printer import Printer, ThermPrinter, CMDPrinter
from GameMode import GameModeManager
import argparse

parser = argparse.ArgumentParser("printer_test")
parser.add_argument("--cmd", help="Uses the commandline to display instead if screen", action="store_true")
args = parser.parse_args()

vig_states = {
    "Init": 0,
    "ChooseMode": 1,
    "ChooseCMC": 2,
    "SelectCard": 3,
    "PrintCard": 4
}

target_cmc = 1
min_cmc = 0
max_cmc = 1
displayHandler = Display()
inputHandler = Input()
printerHandler = Printer()
game_mode_manager = GameModeManager()

card_list = []
current_state = vig_states["Init"]
selected_card = None

if args.cmd is True:
    print ("Creating CMD services")
    displayHandler = CMDDisplay()
    inputHandler = CMDInput()
    printerHandler = CMDPrinter()
else:
    print("Creating hardware services")
    displayHandler = LCDDisplay()
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
    elif new_state == vig_states["ChooseMode"]:
        enter_choose_mode()
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

    displayHandler.update_display("Initializing...", 1)
    printerHandler.feed()
    printerHandler.out("Welcome to Momir Vig Machine!")
    printerHandler.feed(2)

    print('Initialization complete!')
    displayHandler.update_display("Complete!", 2)

    switch_state(vig_states["ChooseMode"])
##############

#Choose Mode state
def enter_choose_mode():
    displayHandler.update_display("Selected mode:", 1)
    displayHandler.update_display(game_mode_manager.get_selected_game_mode_name(), 2)
    inputHandler.up_pressed_callback = increment_game_mode
    inputHandler.down_pressed_callback = decrement_game_mode
    inputHandler.enter_pressed_callback = select_mode

def increment_game_mode():
    game_mode_manager.increment_selected_mode()
    displayHandler.update_display(game_mode_manager.get_selected_game_mode_name(), 2)

def decrement_game_mode():
    game_mode_manager.decrement_selected_mode()
    displayHandler.update_display(game_mode_manager.get_selected_game_mode_name(), 2)

def select_mode():
    inputHandler.up_pressed_callback = None
    inputHandler.down_pressed_callback = None
    inputHandler.enter_pressed_callback = None

    #Initialize card data
    displayHandler.update_display("Building data...")
    global card_list
    card_list = scryfall.get_filtered_cards(game_mode_manager.get_filter())
    set_max_cmc()

    #then go to choosecmc
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
        time.sleep(3) #Pause a bit so we can see the message on screen
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
    #elif current_state == vig_states["ChooseCMC"]:
    #    pass


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