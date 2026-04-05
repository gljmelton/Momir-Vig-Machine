#This standalone script is used to parse the oracle-cards.json file and download the card images. It filters out cards based on their set type and layout, as specified in the config.ini file. The images are saved in the 'Images' directory with the card ID as the filename.
import json
import os
import requests
import configparser
import glob
from io import BytesIO
from PIL import Image
import scryfall

config = configparser.ConfigParser()
config.read('config.ini')

requiretypes = config.get('GENERAL', 'requiretypes').split(', ')
pseudodoublefacedlayouts = config.get('GENERAL', 'pseudodoublefacedlayouts').split(', ')
imagepath = config.get('GENERAL', 'imagepath')
imagetype = config.get('GENERAL', 'imagetype')
deletetype = config.get('GENERAL', 'deletetype')
verbose = config.getboolean('GENERAL', 'verboselogging')
validate = config.getboolean('GENERAL', 'validatedata')
download = True

def printverbose(string):
    if verbose:
        print(string)

def requestandsaveimage(url, filename):
    request = requests.get(url, stream=True)
    img = Image.open(BytesIO(request.content)).convert('1')
    img.save(f'{imagepath}{filename}.{imagetype}')

def doesimageexist(card):
    return os.path.exists(f'{imagepath}{scryfall.getcardid(card)}.{imagetype}')

filtereddata = scryfall.getfilteredcards()

if deletetype == "hard":
    #Clear out existing images in the image path
    files = glob.glob(f'{imagepath}*')
    for f in files:    
        print(f'Removing existing images...')
        os.remove(f)

# Download card images from filtered data, convert to monochrome, and save
totalcards = len(filtereddata)
print(f'Found {totalcards} cards after filtering.')

if download:
    for i in range(len(filtereddata)):
        progress = (i+1) / totalcards * 100
        printverbose(f'Downloading images for {filtereddata[i]["name"]} ({i+1}/{totalcards}) {progress:.2f}%...')
    
        card = filtereddata[i]

        if doesimageexist(filtereddata[i]):
            printverbose(f'Image already exists for {filtereddata[i]["name"]}, skipping download.')
            continue

        requestandsaveimage(scryfall.getarturlforcard(card), scryfall.getcardid(card))
            
        print(f'Art crop downloaded for {filtereddata[i]["name"]}')

#Soft delete after downloading
if deletetype == "soft":
    #Soft delete images that no longer have a corresponding card in the filtered data
    print("Deleting images for cards not in filtered data...")

    

    existingimages = glob.glob(f'{imagepath}*')
    for i in range(len(existingimages)):
        print(f'\r{i+1}/{len(existingimages)} images processed...', end='')
        imageid = os.path.splitext(os.path.basename(existingimages[i]))[0]
        if not any((card["id"] == imageid) for card in filtereddata):
            print("")
            print(f'Deleting {existingimages[i]}...')
            os.remove(existingimages[i])
    
    print("")


if validate:
    print(f'Total cards: {len(filtereddata)} | Total images: {len(os.listdir(imagepath))}')
    print('Validating that all images exist...')
    for i in range(len(filtereddata)):
        if not "id" in filtereddata[i]:
            print(f'Card {filtereddata[i]["name"]} is missing an ID, skipping validation for this card.')
            continue

        card = filtereddata[i]

        if not os.path.exists(f'{imagepath}{scryfall.getcardid(card)}.{imagetype}'):
                print(f'Missing image for {card["name"]}!')
        
        printverbose(f'Validated image {i+1} of {totalcards} for {filtereddata[i]["name"]}!')
    
    print('Images exist for all cards!')

    print('Validating that all images are in card data...')
    existingimages = glob.glob(f'{imagepath}*')
    for i in range(len(existingimages)):
        imageid = os.path.splitext(os.path.basename(existingimages[i]))[0]
        if not any((('card_faces' in card) or ('card_faces' in card and card["id"] == imageid) or (card["id"] == imageid)) for card in filtereddata):
            print(f'Image {existingimages[i]} does not have a corresponding card in data!')
        
        printverbose(f'Validated image {i+1} of {len(existingimages)} for {existingimages[i]}!')

    print('Validating duplicate ids...')
   
    idlist = {}
    for i in range(len(filtereddata)):
        if not scryfall.getcardid(filtereddata[i]) in idlist:
            idlist[str(scryfall.getcardid(filtereddata[i]))] = 1
        else:
            print(f'Duplicate id {scryfall.getcardid(filtereddata[i])} found for {filtereddata[i]["name"]}!')
            idlist[str(scryfall.getcardid(filtereddata[i]))] += 1

    for i in range(len(idlist)):
        if list(idlist.values())[i] > 1:
            print(f'Duplicate id {list(idlist.keys())[i]} found for {idlist[list(idlist.keys())[i]]} cards!')

    print('Duplicate validation complete!')
    print('Validating card types...')
    for i in range(len(filtereddata)):
        card = filtereddata[i]
        if 'type_line' in card:
            if not any (cardtype in card['type_line'].lower().split(' ') for cardtype in requiretypes):
                print(f'Card {card["name"]} does not match required types!')
        elif 'card_faces' in card and 'type_line' in card['card_faces'][0]:
            if not any (cardtype in card['card_faces'][0]['type_line'].lower().split(' ') for cardtype in requiretypes):
                print(f'Card {card["name"]} does not match required types!')

    print('Card type validation complete!')