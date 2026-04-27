import json
import textwrap
import configparser
from enum import IntEnum
from PIL import Image

config = configparser.ConfigParser()
config.read('config.ini')

bulk_data_name = config.get('GENERAL', 'bulk_data_name')
excluded_sets = config.get('GENERAL', 'exclude_sets').split(', ')
excluded_layouts = config.get('GENERAL', 'exclude_layouts').split(', ')
exclude_playtest = config.getboolean('GENERAL', 'exclude_playtest')
require_games = config.get('GENERAL', 'require_games').split(', ')
require_types = config.get('GENERAL', 'require_types').split(', ')
pseudo_double_faced_layouts = config.get('GENERAL', 'pseudo_double_faced_layouts').split(', ')
image_path = config.get('GENERAL', 'image_path')
image_type = config.get('GENERAL', 'image_type')

class Face(IntEnum):
    FRONT = 0
    BACK = 1

def match_exclusions(card):
    if card["set_type"] in excluded_sets:
        return False
    if card["layout"] in excluded_layouts:
        return False
    if exclude_playtest == True and 'promo_types' in card and 'playtest' in card['promo_types']:
        return False
    
    return True
      
def match_front_face_type(card):
        if 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            return any (cardtype in card['card_faces'][0]['type_line'].lower().split(' ') for cardtype in require_types)
        elif 'type_line' in card:
            return any (cardtype in card['type_line'].lower().split(' ') for cardtype in require_types)
        return False

def get_card_by_id(id):
    with open(bulk_data_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return [
        card for card in data if card['id'] == id                                          #Exclude cards based on type line of the front face
    ][0]

def get_filtered_cards():
    with open(bulk_data_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    return [
        card for card in data if match_exclusions(card) and  #Exclude cards based on layout and set type
                                 (any(game in card['games'] for game in require_games) and  #Exclude cards based on game
                                  match_front_face_type(card))                                            #Exclude cards based on type line of the front face
    ]
    
def get_card_id(card):
    return card["id"]

def get_art_url_for_card(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudo_double_faced_layouts:
        return card['card_faces'][face.value]['image_uris']['art_crop']
    else:
        return card['image_uris']['art_crop']

def get_name_for_card(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout']:
        return card['card_faces'][face]['name']
    else:
        return card['name']
    
def get_cmc_for_card(card, face = Face.FRONT):
    if 'card_faces' in card:
        return card['card_faces'][face]['mana_cost']
    else:
        return card['mana_cost']

def get_image_for_card(card):
    return Image.open(f"{image_path}{card['id']}.{image_type}")

def get_title_line_for_card(card, face = Face.FRONT):
    return format_for_single_line(get_name_for_card(card, face), get_cmc_for_card(card, face))

def get_set_and_stat_line_for_card(card, face = Face.FRONT):
    return format_for_single_line(get_set_name_for_card(card), get_stat_line_for_card(card, face))

def format_for_single_line(first, second):
    line_len = 32
    first_cap = ".. "
    result = ""
    if line_len - len(second) < len(first):
        result = (first[:line_len - len(second) - len(first_cap)] + first_cap) + second
    
    elif len(second) + len(first) < line_len:
        result = first + str(" " * (line_len - (len(second) + len(first)))) + second

    else:
        result = first + second

    return result

def get_type_line_for_card(card, face = Face.FRONT):
    text = ""
    if 'card_faces' in card:
        text = card['card_faces'][face]['type_line']
    else:
        text = card['type_line']
    return text.replace('—','-')
    
def get_oracle_text_for_card(card, face = Face.FRONT):
    text = ""
    if 'card_faces' in card:
        text = card['card_faces'][face]['oracle_text']
    else:
        text = card['oracle_text']
    text = text.replace('•', '*')
    text = text.replace('—', '-')
    return text

def get_set_name_for_card(card):
    return card["set_name"]

def get_set_code_for_card(card):
    return card["set"]

def get_stat_line_for_card(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout']:
        return f"{card['card_faces'][face]['power']}/{card['card_faces'][face]['toughness']}"
    elif 'power' in card and 'toughness' in card:
        return f"{card['power']}/{card['toughness']}"
    else:
        return ""
####################

def is_card_true_double_face(card):
    if 'card_faces' in card and card['layout'] not in pseudo_double_faced_layouts:
        return True
    else:
        return False