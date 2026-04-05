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