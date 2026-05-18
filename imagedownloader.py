#This standalone script is used to parse the oracle-cards.json file and download the card images. It filters out cards based on their set type and layout, as specified in the config.ini file. The images are saved in the 'Images' directory with the card ID as the filename.
import os
import requests
import configparser
import glob
from io import BytesIO
from PIL import Image, ImageStat, ImageOps
import numpy
import scryfall
from scryfall import Face
import GameMode

config = configparser.ConfigParser()
config.read('config.ini')

bulk_data_name = config.get('GENERAL', 'bulk_data_name')
pseudodoublefacedlayouts = config.get('GENERAL', 'pseudo_double_faced_layouts').split(', ')
imagepath = config.get('GENERAL', 'image_path')
imagetype = config.get('GENERAL', 'image_type')
verbose = config.getboolean('GENERAL', 'verbose_logging')
download = True

darkthreshold = 0
lightthreshold = 0.85

def printverbose(string):
    if verbose:
        print(string)

def get_image_brightness(img):
    return ImageStat.Stat(img).mean[0]

def get_image_threshold(img):
    brightness = get_image_brightness(img)
    return numpy.interp(brightness, [0,255], [darkthreshold, lightthreshold])

def request_and_save_image(url, filename, face = Face.FRONT):
    if not url:
        return
    request = requests.get(url, stream=True)
    img = Image.open(BytesIO(request.content))
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.resize((384, 280), 0)
    img = img.point(lambda p: 255 if p > (get_image_threshold(img) * 255) else 0)
    img = img.convert("1")

    if face == Face.FRONT:
        img.save(f'{imagepath}{filename}.{imagetype}')

    else:
        img.save(f'{imagepath}Backs/{filename}.{imagetype}')

def does_image_exist(card, face = Face.FRONT):
    if face == Face.FRONT:
        return os.path.exists(f'{imagepath}{scryfall.get_card_id(card)}.{imagetype}')
    else:
        return os.path.exists(f'{imagepath}Backs/{scryfall.get_card_id(card)}.{imagetype}')

def does_card_have_back_image(card):
    return scryfall.is_card_true_double_face(card)

filter = GameMode.Filter("Downloads")
print(filter.type_include)
card_data = scryfall.get_filtered_cards(filter)

deleteall = input("Delete all images? (y,N): ")
downloadmissingimages = input("Download missing images? (Y,n): ")
deleteorphanedimages = input("Delete orphaned images for cards not in database? (Y,n): ")

if deleteall.lower() == "y":
    #Clear out existing images in the image path
    print("Deleting all images...")
    files = glob.glob(f'{imagepath}**/*png', recursive=True)
    for f in files:
        os.remove(f)
    
    print("Delete all images complete!")

# Download card images from filtered data, convert to monochrome, and save
totalcards = len(card_data)
print(f'Found {totalcards} cards after filtering.')

if downloadmissingimages.lower() == "y" or downloadmissingimages.lower() == "":
    for i in range(len(card_data)):
        progress = (i+1) / totalcards * 100
        printverbose(f'Downloading images for {card_data[i]["name"]} ({i+1}/{totalcards}) {progress:.2f}%...')
    
        card = card_data[i]

        if not does_image_exist(card_data[i]):
            request_and_save_image(scryfall.get_art_url_for_card(card), scryfall.get_card_id(card))

        if scryfall.is_card_true_double_face(card) and not does_image_exist(card_data[i], Face.BACK):
            request_and_save_image(scryfall.get_art_url_for_card(card, Face.BACK), scryfall.get_card_id(card), Face.BACK)

        print(f'({i+1}/{totalcards}|{progress:.2f}%) Downloaded {card_data[i]["name"]}')

print("")

#Soft delete after downloading
if deleteorphanedimages.lower() == "y" or deleteorphanedimages.lower() == "":
    #Soft delete images that no longer have a corresponding card in the filtered data
    print("Deleting images for cards not in filtered data...")
    existingimages = glob.glob(f'{imagepath}**/*.png', recursive=True)
    for i in range(len(existingimages)):
        print(f'\r{i+1}/{len(existingimages)} images processed...', end='')
        imageid = os.path.splitext(os.path.basename(existingimages[i]))[0]
        if not any((card["id"] == imageid) for card in card_data):
            print("")
            print(f'Deleting {existingimages[i]}...')
            os.remove(existingimages[i])
    
    print("")

####VALIDATION
print(f'Total cards: {len(card_data)} | Total images: {len(os.listdir(imagepath))}')
print('Validating that all images exist...')
for i in range(len(card_data)):
    if not "id" in card_data[i]:
        print(f'Card {card_data[i]["name"]} is missing an ID, skipping validation for this card.')
        continue

    card = card_data[i]

    if not os.path.exists(f'{imagepath}{scryfall.get_card_id(card)}.{imagetype}'):
            print(f'Missing image for {card["name"]}!')
    
    printverbose(f'Validated image {i+1} of {totalcards} for {card_data[i]["name"]}!')

print('Images exist for all cards!')

print('Validating that all images are in card data...')
existingimages = glob.glob(f'{imagepath}*')
for i in range(len(existingimages)):
    imageid = os.path.splitext(os.path.basename(existingimages[i]))[0]
    if not any((('card_faces' in card) or ('card_faces' in card and card["id"] == imageid) or (card["id"] == imageid)) for card in card_data):
        print(f'Image {existingimages[i]} does not have a corresponding card in data!')
    
    printverbose(f'Validated image {i+1} of {len(existingimages)} for {existingimages[i]}!')

print('Validating duplicate ids...')

idlist = {}
for i in range(len(card_data)):
    if not scryfall.get_card_id(card_data[i]) in idlist:
        idlist[str(scryfall.get_card_id(card_data[i]))] = 1
    else:
        print(f'Duplicate id {scryfall.get_card_id(card_data[i])} found for {card_data[i]["name"]}!')
        idlist[str(scryfall.get_card_id(card_data[i]))] += 1

for i in range(len(idlist)):
    if list(idlist.values())[i] > 1:
        print(f'Duplicate id {list(idlist.keys())[i]} found for {idlist[list(idlist.keys())[i]]} cards!')

print('Duplicate validation complete!')