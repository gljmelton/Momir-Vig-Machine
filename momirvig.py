import scryfall
import random
import time
import gpiozero
from LCD import LCD
import configparser

#CONFIG
config = configparser.ConfigParser()
config.read('config.ini')
BUTTON1PIN = config.getint('GPIO', 'button1pin')
BUTTON2PIN = config.getint('GPIO', 'button2pin')
BUTTON3PIN = config.getint('GPIO', 'button3pin')
BUTTONBOUNCETIME = config.getfloat('GPIO', 'buttonbouncetime')

#Button inputs
button1 = gpiozero.Button(BUTTON1PIN, bounce_time=BUTTONBOUNCETIME)
button2 = gpiozero.Button(BUTTON2PIN, bounce_time=BUTTONBOUNCETIME)
button3 = gpiozero.Button(BUTTON3PIN, bounce_time=BUTTONBOUNCETIME)

vigstates = {
    "Init": 0,
    "ChooseCMC": 1,
    "SelectCard": 2,
    "PrintCard": 3
}

cardlist = scryfall.getfilteredcards()

targetcmc = 1
mincmc = 1
maxcmc = 1
LCD = LCD(i2c_addr = 0x27, backlight=True)

filteredcards = []
currentstate = vigstates["Init"]

#Helper functions
def setmaxcmc():
    global maxcmc
    for card in cardlist:
        if 'cmc' in card and card['cmc'] > maxcmc:
            maxcmc = card['cmc']

def getrandomcardforcmc():
    validcmccards = [card for card in cardlist if 'cmc' in card and card['cmc'] == targetcmc]
    return validcmccards[random.randint(0, len(validcmccards)-1)]

def switchstate(newstate):
    global currentstate

    #On exit functions
    if currentstate == vigstates["Init"]:
        pass
    elif currentstate == vigstates["ChooseCMC"]:
        exitchoosecmcstate()
    elif currentstate == vigstates["SelectCard"]:
        pass
    elif currentstate == vigstates["PrintCard"]:
        pass

    #On enter functions
    if newstate == vigstates["Init"]:
        pass
    elif newstate == vigstates["ChooseCMC"]:
        enterchoosecmcstate()
    elif newstate == vigstates["SelectCard"]:
        selectcard()
    elif newstate == vigstates["PrintCard"]:
        printcard()

    print(f'Switching from state {currentstate} to {newstate}...')
    currentstate = newstate
#####################

#Init
def initvig():
    print("Initializing...")
    LCD.message("Initializing...", 1)
    
    print("Initializing data...")
    LCD.message("Initializing data...", 2)
    setmaxcmc()
    global filteredcards
    filteredcards = scryfall.getfilteredcards()
    
    print('Initialization complete!')
    LCD.message("Complete!", 2)

    switchstate(vigstates["ChooseCMC"])
##############

#Choose CMC state
def increasetargetcmc():
    global targetcmc
    if targetcmc < maxcmc:
        targetcmc += 1
    else:
        targetcmc = maxcmc
    
    print(f'Target CMC set to {int(targetcmc)}!')
    LCD.clear()
    LCD.message(f'Target CMC: {int(targetcmc)}  ', 1)

def decreasetargetcmc():
    global targetcmc
    if targetcmc > mincmc:
        targetcmc -= 1
    else:
        targetcmc = mincmc
    
    print(f'Target CMC set to {int(targetcmc)}!')
    LCD.clear()
    LCD.message(f'Target CMC: {int(targetcmc)}  ', 1)

def printtargetcmc():
    switchstate(vigstates["SelectCard"])

def enterchoosecmcstate():
    print("Entering choose CMC state...")
    
    LCD.clear()
    LCD.message(f'Target CMC: {int(targetcmc)}  ', 1)
    
    #Bind increase button
    button1.when_pressed = increasetargetcmc
    button2.when_pressed = decreasetargetcmc
    button3.when_pressed = printtargetcmc
    
def exitchoosecmcstate():
    print("Exiting choose CMC state...")
    button1.when_pressed = None
    button2.when_pressed = None
    button3.when_pressed = None

def choosecmc():
    pass
#################

#Select card state
def selectcard():
    print("Entering select card state...")
    LCD.clear()
    LCD.message("Selecting card...", 1)
    card = getrandomcardforcmc()
    LCD.clear()
    LCD.message(f'Chosen card:', 1)
    LCD.message(f'{card["name"]}  ', 2)
    print(f'Chosen card: {card["name"]}')
    time.sleep(5) #Delete when this will actually go to the printer
    switchstate(vigstates["PrintCard"])
######################

#Print card state
def printcard():
    print("Entering print card state...")
    #Print card here using printer library
    switchstate(vigstates["ChooseCMC"])
##################

def updatevig():
    if currentstate == vigstates["Init"]:
        initvig()
    elif currentstate == vigstates["ChooseCMC"]:
        pass

#Main loop
while True:
    updatevig()