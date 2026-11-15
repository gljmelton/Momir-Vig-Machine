import sys
import time
import configparser
import msgspec
from Card import Card, Legality, CardUtils
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

def match_exclusions(card : Card, filter_data : GameMode.GameMode):
    if excluded_layouts:
        if card.layout in excluded_layouts:
            #print(f"Rejecting card {card.name} due to layout {card.layout}")
            return False

    if card.layout in excluded_layouts:
        sys.exit(f"Card {card.name} with layout {card.layout} made it through layout filter!")


    #Exclude cards that are legal in exclude_legal
    if filter_data.filter.legal:
        for legalities in filter_data.filter.legal:
            if card.legalities.__getattribute__(legalities) == Legality.NOT_LEGAL:
                #print(f"Rejecting card {card.name} due to legality {legalities}")
                return False

    if filter_data.filter.types:
        # Include cards of the required type
        if card.card_faces and card.card_faces[0].type_line:
            if not compare_lists(CardUtils.get_type_list(card_face=card.card_faces[0]), filter_data.filter.types):
                #print(f"Rejecting card {card.name} due to face type")
                return False

        elif card.type_line:
            if not compare_lists(CardUtils.get_type_list(card=card), filter_data.filter.types):
                #print(f"Rejecting card {card.name} due to type")
                return False

    return True

def match_inclusions(card : Card, filter_data : GameMode.GameMode):
    if filter_data.filter.legal:
        for legalities in filter_data.filter.legal:
            if card.legalities.__getattribute__(legalities) == Legality.NOT_LEGAL:
                #print(f"card {card.name} legality not included")
                return False

    #Include cards of the required type
    if filter_data.filter.types:
        if card.card_faces and card.card_faces[0].type_line:
            if not compare_lists(CardUtils.get_type_list(card_face=card.card_faces[0]), filter_data.filter.types):
                #print(f"card {card.name} face does not have matching type")
                return False

        elif card.type_line:
            if not compare_lists(CardUtils.get_type_list(card=card), filter_data.filter.types):
                #print(f"card {card.name} does not have matching type")
                return False

    #Include cards of the required set code(s)
    if filter_data.filter.set:
        if not card.set in filter_data.filter.set:
            return False

    return True

def compare_lists(a : list[str], b : list[str], exact = False):
    if exact:
        if not list(set(a).difference(b)):
            #print(f"card {a} and card {b} have no differences")
            return True

    else:
        if list(set(a).intersection(b)):
            #print(f"card {a} and card {b} share at least one item")
            return True

    return False

def cmc_analysis(card_set : list[Card]):
    cmc_analysis_results : dict = {}

    for card in card_set:
        if card.cmc in cmc_analysis_results:
            cmc_analysis_results[card.cmc] += 1

        else:
            cmc_analysis_results[card.cmc] = 1

    cmc_analysis_results = dict(sorted(cmc_analysis_results.items()))
    return cmc_analysis_results


def get_card_by_id(id):
    # with open("gamemodes.json", 'rb') as file:
    #     self.game_mode_data = msgspec.json.decode(file.read(), type=list[GameMode])

    data = []
    with open(bulk_data_name, 'rb') as file:
        for line in file:
            card = msgspec.json.decode(line, type=Card, strict=False)
            data.append(card)
    return [
        card for card in data if card.id == id                                          #Exclude cards based on type line of the front face
    ][0]

def get_all_cards():
    start_time = time.time()

    data = []
    with open(bulk_data_name, 'rb') as file:
        for line in file:
            card = msgspec.json.decode(line, type=Card, strict=False)
            data.append(card)

    print(f"Loading card data took {round(time.time() - start_time, 2)} seconds")
    print(f"Loaded {len(data)} cards")
    return data

def get_filtered_cards(data_filter: GameMode.GameMode):
    start_time = time.time()

    data = []
    with open(bulk_data_name, 'rb') as file:
        for line in file:
            card = msgspec.json.decode(line, type=Card, strict=False)
            data.append(card)

    print(f"Loading card data took {round(time.time() - start_time, 2)} seconds")
    print(f"Loaded {len(data)} cards")

    #filtered_data = [card for card in data if match_exclusions(card, data_filter)] # match exclusions
    filtered_data = [card for card in data if match_inclusions(card, data_filter)] # Match inclusions
    filtered_data = [card for card in filtered_data if compare_lists([item.value for item in card.games], require_games)] #match game
    return filtered_data
    
def get_card_id(card):
    return card.id

def get_art_url_for_card(card : Card, face = Face.FRONT):
    if card.card_faces and card.layout not in pseudo_double_faced_layouts:
        if not card.card_faces[face.value].image_uris:
            return None
        return card.card_faces[face.value].image_uris.art_crop
    else:
        if not card.image_uris:
            return None
        return card.image_uris.art_crop

def get_name_for_card(card : Card, face = Face.FRONT):
    if card.card_faces and card.layout:
        return card.card_faces[face].name
    else:
        return card.name
    
def get_cmc_for_card(card : Card, face: int = Face.FRONT):
    if card.card_faces:
        return card.card_faces[face].mana_cost
    else:
        return card.mana_cost

def get_image_for_card(card : Card, face = Face.FRONT):
    if face == Face.FRONT:
        return Image.open(f"{image_path}{card.id}.{image_type}")
    else:
        return Image.open(f"{image_path}Backs/{card.id}.{image_type}")

def get_title_line_for_card(card : Card, face = Face.FRONT):
    return format_for_single_line(get_name_for_card(card, face), get_cmc_for_card(card, face))

def get_set_and_stat_line_for_card(card : Card, face = Face.FRONT):
    return format_for_single_line(get_set_code_for_card(card), get_stat_line_for_card(card, face))

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

def get_type_line_for_card(card : Card, face = Face.FRONT):
    text = ""
    if card.card_faces:
        text = card.card_faces[face].type_line
    else:
        text = card.type_line
    return text.replace('—','-')
    
def get_oracle_text_for_card(card : Card, face = Face.FRONT):
    text = ""
    if card.card_faces:
        text = card.card_faces[face].oracle_text
    else:
        text = card.oracle_text
    text = text.replace('•', '*')
    text = text.replace('—', '-')
    return text

def get_set_name_for_card(card : Card):
    return card.set_name

def get_set_code_for_card(card : Card):
    return card.set

def get_stat_line_for_card(card : Card, face = Face.FRONT):
    if card.card_faces and card.layout:
        return f"{card.card_faces[face].power}/{card.card_faces[face].toughness}"
    elif card.power and card.toughness:
        return f"{card.power}/{card.toughness}"
    else:
        return ""
####################

def is_card_true_double_face(card : Card):
    if card.card_faces and card.layout not in pseudo_double_faced_layouts:
        return True
    else:
        return False