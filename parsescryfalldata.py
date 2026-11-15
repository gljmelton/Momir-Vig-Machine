#This standalone script is used to parse the oracle-cards.json file and download the card images. It filters out cards based on their set type and layout, as specified in the config.ini file. The images are saved in the 'Images' directory with the card ID as the filename.
import os
import requests
import configparser
import glob
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageStat, ImageOps
import numpy
import scryfall
from scryfall import Face, Card

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

    headers = {
        "User-Agent": "ProxyBuilder",
        "Accept": "*/*"
    }
    request = requests.get(url, stream=True, headers=headers)
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

def does_image_exist(c : Card, face = Face.FRONT):
    if face == Face.FRONT:
        path = Path(f'{imagepath}{c.id}.{imagetype}')
        #print(f"Image for {c.name} exists = {path.exists()}")
        return path.exists()
    else:
        path = Path(f'{imagepath}Backs/{c.id}.{imagetype}')
        #print(f"Image for {c.name} back exists = {path.exists()}")
        return path.exists()

def does_card_have_back_image(c):
    return scryfall.is_card_true_double_face(c)

card_data : list[Card] = scryfall.get_all_cards()

delete_all = input("Delete all images? (y,N): ")
download_missing_images = input("Download missing images? (Y,n): ")
delete_orphaned_images = input("Delete orphaned images for cards not in database? (Y,n): ")

if delete_all.lower() == "y":
    #Clear out existing images in the image path
    print("Deleting all images...")
    files = glob.glob(f'{imagepath}**/*png', recursive=True)
    for f in files:
        os.remove(f)
    
    print("Delete all images complete!")

# Download card images from filtered data, convert to monochrome, and save
total_cards = len(card_data)
print(f'Found {total_cards} cards after filtering.')

if download_missing_images.lower() == "y" or download_missing_images.lower() == "":
    for i in range(len(card_data)):
        progress = (i+1) / total_cards * 100
        printverbose(f'Downloading images for {card_data[i].name} ({i+1}/{total_cards}) {progress:.2f}%...')
    
        card = card_data[i]
        front_image_exists = does_image_exist(card_data[i])
        if not front_image_exists:
            request_and_save_image(scryfall.get_art_url_for_card(card), scryfall.get_card_id(card))
            print(f'({i + 1}/{total_cards}|{progress:.2f}%) Downloaded {card_data[i].name}')
        else:
            print(f'({i + 1}/{total_cards}|{progress:.2f}%) Already have {card_data[i].name}')

        if scryfall.is_card_true_double_face(card):
            if not does_image_exist(card_data[i], Face.BACK):
                request_and_save_image(scryfall.get_art_url_for_card(card, Face.BACK), scryfall.get_card_id(card), Face.BACK)
                print(f'({i + 1}/{total_cards}|{progress:.2f}%) Downloaded {card_data[i].name} back')
            else:
                print(f'({i + 1}/{total_cards}|{progress:.2f}%) Already have {card_data[i].name} back')



print("")

#Soft delete after downloading
if delete_orphaned_images.lower() == "y" or delete_orphaned_images.lower() == "":
    #Soft delete images that no longer have a corresponding card in the filtered data
    print("Deleting images for cards not in filtered data...")
    existing_images = glob.glob(f'{imagepath}**/*.png', recursive=True)
    for i in range(len(existing_images)):
        print(f'\r{i+1}/{len(existing_images)} images processed...', end='')
        imageid = os.path.splitext(os.path.basename(existing_images[i]))[0]
        if not any((card.id == imageid) for card in card_data):
            print("")
            print(f'Deleting {existing_images[i]}...')
            os.remove(existing_images[i])
    
    print("")

####VALIDATION
print(f'Total cards: {len(card_data)} | Total images: {len(os.listdir(imagepath))}')
print('Validating that all images exist...')
for i in range(len(card_data)):
    if card_data[i].id:
        print(f'Card {card_data[i].name} is missing an ID, skipping validation for this card.')
        continue

    card = card_data[i]

    if not os.path.exists(f'{imagepath}{scryfall.get_card_id(card)}.{imagetype}'):
            print(f'Missing image for {card.name}!')
    
    printverbose(f'Validated image {i+1} of {total_cards} for {card_data[i].name}!')

print('Images exist for all cards!')

print('Validating that all images are in card data...')
existing_images = glob.glob(f'{imagepath}*')
for i in range(len(existing_images)):
    imageid = os.path.splitext(os.path.basename(existing_images[i]))[0]
    if not any(((card.card_faces is None) or (card.card_faces is None and card.id == imageid) or (card.id == imageid)) for card in card_data):
        print(f'Image {existing_images[i]} does not have a corresponding card in data!')
    
    printverbose(f'Validated image {i+1} of {len(existing_images)} for {existing_images[i]}!')

print('Validating duplicate ids...')

id_list = {}
for i in range(len(card_data)):
    if not scryfall.get_card_id(card_data[i]) in id_list:
        id_list[str(scryfall.get_card_id(card_data[i]))] = 1
    else:
        print(f'Duplicate id {scryfall.get_card_id(card_data[i])} found for {card_data[i].name}!')
        id_list[str(scryfall.get_card_id(card_data[i]))] += 1

for i in range(len(id_list)):
    if list(id_list.values())[i] > 1:
        print(f'Duplicate id {list(id_list.keys())[i]} found for {id_list[list(id_list.keys())[i]]} cards!')

print('Duplicate validation complete!')