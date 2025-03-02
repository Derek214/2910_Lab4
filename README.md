# 2910_Lab4
A console app that will make use of the Scryfall API to allow MTG deckbuilding.

## Issues
If a card is not found during a search then attempting to access its properties will cause an error (resolved using check in print_formatted_card function).  
No good way to display card images with a GUI (resolved by formatting important card information into text output which makes for the cleanest output with the current implementation).  
Implementation altered from plan: viewing deck will make API call for card information so only card names are stored locally  
Double-faced cards cause an error with the mana_cost property  
The Scryfall API random function does not work with filters  
