import scryfall
import random
import time
import RPi.GPIO as GPIO
from LCD import LCD

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
    
    print("Initializing GPIO...")
    LCD.message("Initializing GPIO...", 2)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 11 to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 12 to be an input pin and set initial value to be pulled low (off)
    
    print("Initializing data...")
    LCD.message("Initializing data...", 2)
    setmaxcmc()
    global filteredcards
    filteredcards = scryfall.getfilteredcards()
    switchstate(vigstates["ChooseCMC"])
    print('Initialization complete!')
    LCD.message("Complete!", 2)
##############

#Choose CMC state
def increasetargetcmc():
    global targetcmc
    if targetcmc < maxcmc:
        targetcmc += 1
    else:
        targetcmc = maxcmc
    
    print(f'Target CMC set to {targetcmc}!')
    LCD.clear()
    LCD.message(f'Target CMC: {targetcmc}  ', 1)

def decreasetargetcmc():
    global targetcmc
    if targetcmc > mincmc:
        targetcmc -= 1
    else:
        targetcmc = mincmc
    
    print(f'Target CMC set to {targetcmc}!')
    LCD.clear()
    LCD.message(f'Target CMC: {targetcmc}  ', 1)

def printtargetcmc():
    switchstate(vigstates["SelectCard"])

def enterchoosecmcstate():
    print("Entering choose CMC state...")
    #Bind increase button
    GPIO.add_event_detect(10,GPIO.RISING,callback=increasetargetcmc) # Setup event on pin 10 rising edge
    #Bind decrease button
    GPIO.add_event_detect(11,GPIO.RISING,callback=decreasetargetcmc) # Setup event on pin 10 rising edge
    #Bind print button
    GPIO.add_event_detect(12,GPIO.RISING,callback=decreasetargetcmc) # Setup event on pin 10 rising edge

def exitchoosecmcstate():
    print("Exiting choose CMC state...")
    GPIO.remove_event_detect(10) # Clean up event on pin 10
    GPIO.remove_event_detect(11) # Clean up event on pin 11
    switchstate(vigstates["SelectCard"])

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