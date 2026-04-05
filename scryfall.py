import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

bulkdataname = config.get('GENERAL', 'bulkdataname')
excludedsets = config.get('GENERAL', 'excludesets').split(', ')
excludedlayouts = config.get('GENERAL', 'excludelayouts').split(', ')
requiregames = config.get('GENERAL', 'requiregames').split(', ')
requiretypes = config.get('GENERAL', 'requiretypes').split(', ')
pseudodoublefacedlayouts = config.get('GENERAL', 'pseudodoublefacedlayouts').split(', ')

def matchexclusions(card):
    if card["set_type"] in excludedsets:
        return False
    if card["layout"] in excludedlayouts:
        return False
    
    return True
      

def matchfrontfacetype(card):
        if 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            return any (cardtype in card['card_faces'][0]['type_line'].lower().split(' ') for cardtype in requiretypes)
        elif 'type_line' in card:
            return any (cardtype in card['type_line'].lower().split(' ') for cardtype in requiretypes)
        return False

def getfilteredcards():
        with open(bulkdataname, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        return [
            card for card in data if matchexclusions(card) and               #Exclude cards based on layout and set type
            (any(game in card['games'] for game in requiregames) and             #Exclude cards based on game
            matchfrontfacetype(card))                                            #Exclude cards based on type line of the front face
        ]
    
    