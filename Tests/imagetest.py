from PIL import Image, ImageStat, ImageEnhance
from io import BytesIO
import scryfall
import requests
import configparser
import numpy

config = configparser.ConfigParser()
config.read('config.ini')

lightId="00d4d751-50df-4d8f-a6d9-4e76797c429a"
darkId="d99869b4-0bb6-444a-bdc4-5916371c9d29"

testId = "2c3549f6-25df-4ea7-84ad-922ccd4af6b2"
darkthreshold = 0
lightthreshold = 0.85
testcard = scryfall.get_card_by_id(testId)
lightcard = scryfall.get_card_by_id(lightId)
darkcard = scryfall.get_card_by_id(darkId)

def getimagebrightness(img):
    return ImageStat.Stat(img).mean[0]

def getimagethreshold(img):
    brightness = getimagebrightness(img)
    return numpy.interp(brightness, [0,255], [darkthreshold, lightthreshold])

def grabimageunfiltered(card, name):
    print(f"Grabbing unfiltered image for {name} card")
    request = requests.get(scryfall.get_art_url_for_card(card), stream=True)
    img = Image.open(BytesIO(request.content))
    img.save(f'test-image-unfiltered-{name}.png')

def grabimageandprocess(card, name):
    print(f"Grabbing and processing image for {name} card")
    request = requests.get(scryfall.get_art_url_for_card(card), stream=True)
    img = Image.open(BytesIO(request.content))
    img = img.convert("L")
    print(f"{name} image brightness: {getimagebrightness(img)}")
    if getimagebrightness(img) < 60:
        enhancer = ImageEnhance.Brightness(img)
        print("Enhancing brightness")
        img = enhancer.enhance(1.5)

    img = img.resize((384, 280), 0)
    #img = ImageOps.posterize(img, 1)
    print(f"{name} image threshold: {getimagethreshold(img)*255}")
    img = img.point( lambda p: 255 if p > (getimagethreshold(img)*255) else 0 )
    img = img.convert("1")
    img.save(f'test-image-{name}.png')

grabimageunfiltered(testcard, "mid")
grabimageunfiltered(lightcard, "light")
grabimageunfiltered(darkcard, "dark")

grabimageandprocess(testcard, "mid")
grabimageandprocess(lightcard, "light")
grabimageandprocess(darkcard, "dark")