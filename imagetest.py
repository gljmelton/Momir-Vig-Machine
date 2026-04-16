from PIL import Image
from PIL import ImageStat
from io import BytesIO
import json
import scryfall
import requests
import configparser
import numpy

config = configparser.ConfigParser()
config.read('config.ini')

lightId="00d4d751-50df-4d8f-a6d9-4e76797c429a"
darkId="3baa08ac-9a94-4e22-91bb-c6966cd0a0de"

testId = "2c3549f6-25df-4ea7-84ad-922ccd4af6b2"
darkthreshold = 0.1
lightthreshold = 0.95
testcard = scryfall.getcardbyid(testId)[0]
lightcard = scryfall.getcardbyid(lightId)[0]
darkcard = scryfall.getcardbyid(darkId)[0]

def getimagebrightness(img):
    return ImageStat.Stat(img).mean[0]

def getimagethreshold(img):
    brightness = getimagebrightness(img)
    return numpy.interp(brightness, [0,255], [darkthreshold, lightthreshold])

def grabimageunfiltered(card, name):
    print(f"Grabbing unfiltered image for {name} card")
    request = requests.get(scryfall.getarturlforcard(card), stream=True)
    img = Image.open(BytesIO(request.content))
    img.save(f'test-image-unfiltered-{name}.png')

def grabimageandprocess(card, name):
    print(f"Grabbing and processing image for {name} card")
    request = requests.get(scryfall.getarturlforcard(card), stream=True)
    img = Image.open(BytesIO(request.content))
    img = img.resize((384, 280), 0)
    img = img.point( lambda p: 255 if p > (getimagethreshold(img)*255) else 0 )
    print(f"{name} image brightness: {getimagebrightness(img)}")
    img = img.convert("1")
    img.save(f'test-image-{name}.png')

grabimageunfiltered(testcard, "mid")
grabimageunfiltered(lightcard, "light")
grabimageunfiltered(darkcard, "dark")

grabimageandprocess(testcard, "mid")
grabimageandprocess(lightcard, "light")
grabimageandprocess(darkcard, "dark")