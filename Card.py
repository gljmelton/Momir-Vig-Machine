import msgspec
from enum import Enum

class Layout(Enum):
    NORMAL = "normal"
    SPLIT = "split"
    FLIP = "flip"
    TRANSFORM = "transform"
    MDFC = "modal_dfc"
    MELD = "meld"
    LEVELER = "leveler"
    CLASS = "class"
    CASE = "case"
    SAGA = "saga"
    ADVENTURE = "adventure"
    PREPARE = "prepare"
    MUTATE = "mutate"
    PROTOTYPE = "prototype"
    BATTLE = "battle"
    PLANAR = "planar"
    SCHEME = "scheme"
    VANGUARD = "vanguard"
    TOKEN = "token"
    DOUBLE_FACE_TOKEN = "double_faced_token"
    EMBLEM = "emblem"
    AUGMENT = "augment"
    HOST = "host"
    ART_SERIES = "art_series"
    REVERSIBLE = "reversible_card"
    FRONT_CARD = "front_card"

class Colors(Enum):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"

class Legality(Enum):
    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    BANNED = "banned"
    RESTRICTED = "restricted"

class Games(Enum):
    PAPER = "paper"
    MTGO = "mtgo"
    ARENA = "arena"
    ASTRAL = "astral"
    SEGA = "sega"

class ImageUri(msgspec.Struct):
    art_crop: str

class Legalities(msgspec.Struct):
    standard: Legality
    future: Legality
    historic: Legality
    timeless: Legality
    gladiator: Legality
    pioneer: Legality
    modern: Legality
    legacy: Legality
    pauper: Legality
    vintage: Legality
    penny: Legality
    commander: Legality
    oathbreaker: Legality
    standardbrawl: Legality
    brawl: Legality
    alchemy: Legality
    paupercommander: Legality
    duel: Legality
    oldschool: Legality
    premodern: Legality
    predh: Legality

class Prices(msgspec.Struct):
    usd: str | None = None

class CardFace(msgspec.Struct):
    name: str
    type_line: str | None = None
    oracle_text: str | None = None
    mana_cost: str | None = None
    image_uris: ImageUri | None = None
    keywords: list | None = None
    power: str | None = None
    toughness: str | None = None

class Card(msgspec.Struct):
    id: str
    name: str
    released_at: str
    layout: Layout
    cmc: float
    keywords: list
    legalities: Legalities
    games: list[Games]
    set: str
    set_name: str
    type_line: str | None = None
    colors: list | None = None
    oracle_text: str | None = None
    mana_cost: str | None = None
    image_uris: ImageUri | None = None
    power: str | None = None
    toughness: str | None = None
    prices: Prices | None = None
    card_faces: list[CardFace] = None


class CardUtils:
    @staticmethod
    def get_type_list(card:Card=None, card_face:CardFace=None) -> list[str]:
        result = []
        if card and card.type_line:
            result = str.split(card.type_line.lower())

        elif card_face and card_face.type_line:
            result = str.split(card_face.type_line.lower())

        return result