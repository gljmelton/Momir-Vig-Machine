from PIL import Image
from io import BytesIO
import json
import scryfall
import requests
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

testId = "2c3549f6-25df-4ea7-84ad-922ccd4af6b2"
threshold = 0.3
testcard = scryfall.getcardbyid(testId)[0]

request = requests.get(scryfall.getarturlforcard(testcard), stream=True)
img = Image.open(BytesIO(request.content))
img = img.resize((384, 280), 0)
img = img.point( lambda p: 255 if p > (threshold*255) else 0 )
img = img.convert("1")
img.save(f'test-image.png')