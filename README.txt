1. Download bulk oracle data from Scryfall API
2. Start python venv in project directory and grab requirements
    - python -m venv env
    - source ./env/bin/activate
    - pip install -r reqirements.txt
3. Place bulk data in project direction on same level as scryfall.py
4. Match file name for bulk to match bulkdataname in config
5. Run parsescryfalldata.py
    - This is a standalone script that will grab all eligible Momir Basic creature cards and download their card images as monochrome pngs.
    - Eligible cards are determined by set tags and card layouts. Set types that are excluded can be change in excludesets in config.ini. YMMV with some changes and be careful with changing excludelayouts and pseudodoublefacedlayouts as undesirable behavior may occur.
6. 

parsescryfalldata.py
- This is a standalone script. 
- Parameters are in GENERAL config section.
- This script will clean the imagepath, filter json to match filter parameters, 

momirvig.py - runs automatically on raspberry pi
    - Accepts gpio input from buttons.
        - 3 buttons
            - + cmc
            - - cmc
            - print
    - Fetches card info from bulk data based on cmc
        - searches data for random card that matches cmc
        - fetches image from image folder with matching scryfall card id name
    - Sends info to thermal printer
        Creature Name | cmc
        Image
        Type line
        Oracle text
        power/toughness