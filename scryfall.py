import json
import textwrap
import configparser
from enum import IntEnum
from PIL import Image

config = configparser.ConfigParser()
config.read('config.ini')

bulkdataname = config.get('GENERAL', 'bulkdataname')
excludedsets = config.get('GENERAL', 'excludesets').split(', ')
excludedlayouts = config.get('GENERAL', 'excludelayouts').split(', ')
excludeplaytest = config.getboolean('GENERAL', 'excludeplaytest')
requiregames = config.get('GENERAL', 'requiregames').split(', ')
requiretypes = config.get('GENERAL', 'requiretypes').split(', ')
pseudodoublefacedlayouts = config.get('GENERAL', 'pseudodoublefacedlayouts').split(', ')
imagepath = config.get('GENERAL', 'imagepath')
imagetype = config.get('GENERAL', 'imagetype')

class Face(IntEnum):
    FRONT = 0
    BACK = 1

def matchexclusions(card):
    if card["set_type"] in excludedsets:
        return False
    if card["layout"] in excludedlayouts:
        return False
    if excludeplaytest == True and 'promo_types' in card and 'playtest' in card['promo_types']:
        return False
    
    return True
      
def matchfrontfacetype(card):
        if 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            return any (cardtype in card['card_faces'][0]['type_line'].lower().split(' ') for cardtype in requiretypes)
        elif 'type_line' in card:
            return any (cardtype in card['type_line'].lower().split(' ') for cardtype in requiretypes)
        return False

def getcardbyid(id):
    with open(bulkdataname, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return [
        card for card in data if card['id'] == id                                          #Exclude cards based on type line of the front face
    ][0]

def getfilteredcards():
    with open(bulkdataname, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return [
        card for card in data if matchexclusions(card) and               #Exclude cards based on layout and set type
        (any(game in card['games'] for game in requiregames) and             #Exclude cards based on game
        matchfrontfacetype(card))                                            #Exclude cards based on type line of the front face
    ]
    
def getcardid(card):
    return card["id"]

def getarturlforcard(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][face.value]['image_uris']['art_crop']
    else:
        return card['image_uris']['art_crop']

#Single Sided Cards
def getnameforcard(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][face]['name']
    else:
        return card['name']
    
def getcmcforcard(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][face]['mana_cost']
    else:
        return card['mana_cost']

def getimageforcard(card):
    return Image.open(f"{imagepath}{card['id']}.{imagetype}")

def gettitlelineforcard(card, face = Face.FRONT):
    print("Getting name line..")
    name = getnameforcard(card, face)
    print(f"Name: {name}")
    cmc = getcmcforcard(card, face)
    print(f"CMC: {cmc}")
    linelen = 32
    namecap = ".. "
    title = ""

    if linelen - len(cmc) < len(name):
        title = (name[:linelen - len(cmc) - len(namecap)] + namecap) + cmc
    
    elif len(cmc) + len(name) < linelen:
        title = name + str(" " * (linelen - (len(cmc) + len(name)))) + cmc

    return title

def gettypelineforcard(card, face = Face.FRONT):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][face]['type_line']
    else:
        text = card['type_line']
    return text.replace('—','-')
    
def getoracletextforcard(card, face = Face.FRONT):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][face]['oracle_text']
    else:
        text = card['oracle_text']
    text = text.replace('•', '*')
    text = text.replace('—', '-')
    return text
    
def getstatlineforcard(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return f"{card['card_faces'][face]['power']}/{card['card_faces'][face]['toughness']}"
    elif 'power' in card and 'toughness' in card:
        return f"{card['power']}/{card['toughness']}"
    else:
        return ""
####################

def iscardtruedoubleface(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return True
    else:
        return False