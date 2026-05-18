import json
import sys
import time
import configparser
from enum import IntEnum
from PIL import Image
import GameMode

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

def match_exclusions(card, filter_data : GameMode.GameMode):
    if excluded_layouts:
        if compare_lists([card["layout"]], excluded_layouts):
            return False

    if card['layout'] in excluded_layouts:
        sys.exit(f"Card {card['name']} with layout {card['layout']} made it through layout filter!")

    #Exclude cards that are legal in exclude_legal
    if filter_data.filter.legal.exclude.inclusive:
        for legalities in filter_data.filter.legal.exclude.inclusive:
            if card['legalities'][legalities] == "not_legal":
                #print(f"card {card['name']} legality not included")
                return False

    if filter_data.filter.types.exclude.inclusive:
        # Include cards of the required type
        if 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            if not compare_lists(card['card_faces'][0]['type_line'].lower().split(' '), filter_data.filter.types.exclude.inclusive):
                return False

        elif 'type_line' in card:
            if not compare_lists(card['type_line'].lower().split(' '), filter_data.filter.types.include):
                return False

    return True

def match_inclusions(card, filter_data : GameMode.GameMode):
    if filter_data.filter.legal.include.inclusive:
        for legalities in filter_data.filter.legal.include.inclusive:
            if card['legalities'][legalities] == "not_legal":
                #print(f"card {card['name']} legality not included")
                return False

    #Include cards of the required type
    if filter_data.filter.types.include.inclusive:
        if 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            if not compare_lists(card['card_faces'][0]['type_line'].lower().split(' '), filter_data.filter.types.include.inclusive):
                return False

        elif 'type_line' in card:
            if not compare_lists(card['type_line'].lower().split(' '), filter_data.filter.types.include.inclusive):
                return False

    return True

def compare_lists(a, b, exact = False):
    if exact:
        if not list(set(a).difference(b)):
            #print(f"card {a} and card {b} have no differences")
            return True

    else:
        if list(set(a).intersection(b)):
            #print(f"card {a} and card {b} share at least one item")
            return True

    return False

def get_card_by_id(id):
    with open(bulk_data_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return [
        card for card in data if card['id'] == id                                          #Exclude cards based on type line of the front face
    ][0]

def get_filtered_cards(data_filter: GameMode.GameMode):
    start_time = time.time()
    with open(bulk_data_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print(f"Loading card data took {round(time.time() - start_time, 2)} seconds")

    return [
        card for card in data if match_exclusions(card, data_filter) and #Exclude cards based on layout and set type
                                 match_inclusions(card, data_filter) and
            (any(game in card['games'] for game in require_games))                               #Exclude cards based on type line of the front face
    ]
    
def get_card_id(card):
    return card["id"]

def get_art_url_for_card(card, face = Face.FRONT):
    if 'card_faces' in card and card['layout'] not in pseudo_double_faced_layouts:
        if not 'image_uris' in card['card_faces'][face.value]:
            return None
        return card['card_faces'][face.value]['image_uris']['art_crop']
    else:
        if not 'image_uris' in card:
            return None
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

def get_image_for_card(card, face = Face.FRONT):
    if face == Face.FRONT:
        return Image.open(f"{image_path}{card['id']}.{image_type}")
    else:
        return Image.open(f"{image_path}Backs/{card['id']}.{image_type}")

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