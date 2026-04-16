import json
import textwrap
import configparser
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
    ]

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

def getarturlforcard(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][0]['image_uris']['art_crop']
    elif 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][0]['image_uris']['art_crop']
    else:
        return card['image_uris']['art_crop']

#Single Sided Cards
def getnameforcard(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][0]['name']
    else:
        return card['name']
    
def getcmcforcard(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][0]['mana_cost']
    else:
        return card['mana_cost']

def getimageforcard(card):
    return Image.open(f"{imagepath}{card['id']}.{imagetype}")

def gettypelineforcard(card):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][0]['type_line']
    else:
        text = card['type_line']
    return text.replace('—','-')
    
def getoracletextforcard(card):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][0]['oracle_text']
    else:
        text = card['oracle_text']
    text = text.replace('•', '*')
    text = text.replace('—', '-')
    paragraphs = text.splitlines()
    text = "\n".join([textwrap.fill(text, 32) for p in paragraphs])
    return text
    
def getstatlineforcard(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return f"{card['card_faces'][0]['power']}/{card['card_faces'][0]['toughness']}"
    elif 'power' in card and 'toughness' in card:
        return f"{card['power']}/{card['toughness']}"
    else:
        return ""
####################

#Double Sided Card Back
def getnameforcardback(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][1]['name']
    else:
        return ""


def getcmcforcardback(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return card['card_faces'][1]['mana_cost']
    else:
        return ""

def gettypelineforcardback(card):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][1]['type_line']
    else:
        text = card['type_line']
    return text.replace('—','-')
    
def getoracletextforcardback(card):
    text = ""
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        text = card['card_faces'][1]['oracle_text']
    else:
        text = card['oracle_text']
    return text.replace('—', '-')
    
def getstatlineforcardback(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return f"{card['card_faces'][1]['power']}/{card['card_faces'][0]['toughness']}"
    elif 'power' in card and 'toughness' in card:
        return f"{card['power']}/{card['toughness']}"
    else:
        return ""
#######################

def iscardtruedoubleface(card):
    if 'card_faces' in card and card['layout'] not in pseudodoublefacedlayouts:
        return True
    else:
        return False