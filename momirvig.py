from enum import Enum

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

class State(Enum):
    Init = 0
    ChooseMode = 1
    ChooseCMC = 2
    SelectCard = 3
    PrintCard = 4

class MomirVig:
    target_cmc = 1
    min_cmc = 16
    max_cmc = 0
    display_handler = Display()
    input_handler = Input()
    printer_handler = Printer()
    game_mode_manager = GameModeManager()

    card_list = []
    current_state = State.Init
    state_change_callback = None
    selected_card = None

    def __init__(self):
        if args.cmd is True:
            print ("Creating CMD services")
            self.display_handler = CMDDisplay()
            self.input_handler = CMDInput()
            self.printer_handler = CMDPrinter()
        else:
            print("Creating hardware services")
            self.display_handler = LCDDisplay()
            self.input_handler = GPIOInput()
            self.printer_handler = ThermPrinter()

    #Helper functions
    def set_min_max_cmc(self):
        print(f"Total cards: {len(self.card_list)}")
        for card in self.card_list:
            if card.cmc > self.max_cmc:
                self.max_cmc = card.cmc
            elif card.cmc < self.min_cmc:
                self.min_cmc = card.cmc

        print(f"Max cmc: {self.max_cmc} | Min cmc: {self.min_cmc}")

    def get_random_card_for_cmc(self):
        valid_cmc_cards = [card for card in self.card_list if card.cmc == self.target_cmc]
        if len(valid_cmc_cards) == 0:
            print("No valid CMC card found!")
            return None

        return valid_cmc_cards[random.randint(0, len(valid_cmc_cards)-1)]

    def switch_state(self, new_state):
        #On exit functions
        if self.current_state == State.Init:
            pass
        elif self.current_state == State.ChooseCMC:
            self.exit_choose_cmc_state()
        elif self.current_state == State.SelectCard:
            pass
        elif self.current_state == State.PrintCard:
            pass

        print(f'Switching from state {self.current_state} to {new_state}...')

        #On enter functions
        if new_state == State.Init:
            pass
        elif new_state == State.ChooseMode:
            self.enter_choose_mode()
        elif new_state == State.ChooseCMC:
            self.enter_choose_cmc_state()
        elif new_state == State.SelectCard:
            self.select_card()
        elif new_state == State.PrintCard:
            self.print_card()

        self.current_state = new_state

        if self.state_change_callback is not None:
            self.state_change_callback(self.get_state_name())

    def get_state_name(self):
        return str(self.current_state)
    #####################

    #Init
    def init_vig(self):
        print("Initializing...")

        self.display_handler.update_display("Initializing...", 1)
        self.printer_handler.feed()
        self.printer_handler.out("Welcome to Momir Vig Machine!")
        self.printer_handler.feed(2)

        print('Initialization complete!')
        self.display_handler.update_display("Complete!", 2)

        self.switch_state(State.ChooseMode)
    ##############

    #Choose Mode state
    def enter_choose_mode(self):
        self.display_handler.update_display("Selected mode:", 1)
        self.display_handler.update_display(self.game_mode_manager.get_selected_game_mode_name(), 2)
        self.input_handler.up_pressed_callback = self.increment_game_mode
        self.input_handler.down_pressed_callback = self.decrement_game_mode
        self.input_handler.enter_pressed_callback = self.select_mode

    def increment_game_mode(self):
        self.game_mode_manager.increment_selected_mode()
        self.display_handler.update_display(self.game_mode_manager.get_selected_game_mode_name(), 2)

    def decrement_game_mode(self):
        self.game_mode_manager.decrement_selected_mode()
        self.display_handler.update_display(self.game_mode_manager.get_selected_game_mode_name(), 2)

    def select_mode(self):
        self.input_handler.up_pressed_callback = None
        self.input_handler.down_pressed_callback = None
        self.input_handler.enter_pressed_callback = None

        #Initialize card data
        self.display_handler.update_display("Building data...")
        self.card_list = scryfall.get_filtered_cards(self.game_mode_manager.get_game_mode())

        print(scryfall.cmc_analysis(self.card_list))

        printerhelper.print_rules(self.printer_handler, self.game_mode_manager.get_game_mode().rules)

        self.set_min_max_cmc()

        #then go to choosecmc
        self.switch_state(State.ChooseCMC)
    ##############

    #Choose CMC state
    def increase_target_cmc(self):
        if self.target_cmc < self.max_cmc:
            self.target_cmc += 1
        else:
            self.target_cmc = self.max_cmc

        print(f'Target CMC set to {int(self.target_cmc)}!')
        self.display_handler.clear()
        self.display_handler.update_display(f'Target CMC: {int(self.target_cmc)}  ', 1)

    def decrease_target_cmc(self):
        if self.target_cmc > self.min_cmc:
            self.target_cmc -= 1
        else:
            self.target_cmc = self.min_cmc

        print(f'Target CMC set to {int(self.target_cmc)}!')
        self.display_handler.clear()
        self.display_handler.update_display(f'Target CMC: {int(self.target_cmc)}  ', 1)

    def print_target_cmc(self):
        self.switch_state(State.SelectCard)

    def enter_choose_cmc_state(self):
        print("Entering choose CMC state...")

        self.display_handler.clear()
        self.display_handler.update_display(f'Target CMC: {int(self.target_cmc)}  ', 1)

        #Bind increase button
        self.input_handler.up_pressed_callback = self.increase_target_cmc
        self.input_handler.down_pressed_callback = self.decrease_target_cmc
        self.input_handler.enter_pressed_callback = self.print_target_cmc

    def exit_choose_cmc_state(self):
        print("Exiting choose CMC state...")
        self.input_handler.clear_callbacks()

    def choose_cmc(self):
        pass
    #################

    #Select card state
    def select_card(self):
        print("Entering select card state...")
        self.display_handler.clear()
        self.display_handler.update_display("Selecting card...", 1)
        self.selected_card = self.get_random_card_for_cmc()
        self.display_handler.clear()
        if self.selected_card is None:
            print(f'No cards at cmc {int(self.target_cmc)}!')
            self.display_handler.update_display(f"No cmc {int(self.target_cmc)} cards!", 1)
            time.sleep(3) #Pause a bit so we can see the message on screen
            self.switch_state(State.ChooseCMC)
        else:
            self.display_handler.update_display(f'Chosen card:', 1)
            self.display_handler.update_display(f'{self.selected_card.name}  ', 2)
            print(f'Chosen card: {self.selected_card.name}')
            self.switch_state(State.PrintCard)
    ######################

    #Print card state
    def print_card(self):
        print("Entering print card state...")
        #Print card here using printer library
        print("Sending print request to printer...")
        printerhelper.print_card(self.printer_handler, self.selected_card)
        print("Print sent!")
        self.switch_state(State.ChooseCMC)
    ##################

    def update(self):
        if self.current_state == State.Init:
            self.init_vig()
        #elif current_state == vig_states["ChooseCMC"]:
        #    pass

    def cleanup(self):
        print("Cleaning up...")
        self.display_handler.clear()

        self.display_handler.update_display("Goodbye!", 1)
        time.sleep(2)
        self.display_handler.clear()


def main(instance : MomirVig):
    while True:
        instance.update()

#Main loop
if __name__ == '__main__':
    momir_vig = MomirVig()
    try:
        main(momir_vig)
    except KeyboardInterrupt:
        momir_vig.cleanup()