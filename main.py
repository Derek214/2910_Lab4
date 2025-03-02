import requests
import time
import os

def search_card(card_name):
    # Searches for a card by name using Scryfall's fuzzy search as to not require exact matches
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name.replace(' ', '%20')}"
    response = requests.get(url)
    
    if response.status_code == 200:
        card_data = response.json()
        return card_data
    else:
        return "error: Card not found"
    
def print_formatted_card(card_data):
    if "error" in card_data:
        print(card_data)
    else:
        print(f"\n{card_data['name']} - {card_data['mana_cost']} ({card_data['type_line']})")
        print("------------------------")
        print(card_data['oracle_text'])
        print(f"${card_data['prices']['usd']}")
    
    
def deck_manager():
    
    # Create a file to store decks if it doesn't exist already
    if not os.path.exists("decks.txt"):
        with open("decks.txt", "w") as file:
            pass
        
    deck_name = input("Enter a deck name: ")
    found = False
    with open("decks.txt", 'r') as file:
        for line in file:
            if deck_name in line:
                found = True
    
    if not found:
        print(f"'{deck_name}' not found in the file.")
        create_new_deck = input(f"Would you like to create '{deck_name}'? (y/n): ")
        if create_new_deck == 'y':
            with open("decks.txt", 'a') as file:
                file.write(f"\n{deck_name}\n")
            found = True
        else:
            return
        
    if found:
        edit_deck = input(F"Would you like to edit '{deck_name}'? (y/n): ")
        if edit_deck == 'y':
            deck_editor(deck_name)
            
        view_deck = input(F"Would you like to view '{deck_name}'? (y/n): ")
        if view_deck == 'y':
            deck_viewer(deck_name)
            
            
def deck_editor(deck_name):
    with open("decks.txt", "r") as file:
        lines = file.readlines()

    updated_lines = []
    inside_deck = False

    for line in lines:
        # Identify where the deck starts
        if line == deck_name:
            inside_deck = True 
        
        elif inside_deck and line == "":  # Empty line indicates the end of a deck
            inside_deck = False
            updated_lines.append(line)  # Preserve the empty line
        
        updated_lines.append(line)  # Preserve all other lines

    # Add new cards
    new_cards = []
    while True:
        card_name = input("Enter card to add (or press enter to stop editing): ").strip()
        if not card_name:
            break
        card = search_card(card_name)
        if card:
            new_cards.append(f"{card['name']}\n")

    if new_cards:
        # Find the last occurrence of the deck section and insert cards there
        for i in range(len(updated_lines)):
            if updated_lines[i].strip() == deck_name:
                index = i + 1
                while index < len(updated_lines) and updated_lines[index].strip() != "":
                    index += 1
                updated_lines[index:index] = new_cards  # Insert cards before empty line

    # Write updated content back to the file
    with open("decks.txt", "w") as file:
        file.writelines(updated_lines)
    

def deck_viewer(deck_name):
    deck_contents = []
    start_reading = False
    with open("decks.txt", 'r') as file:
        for line in file:
            if start_reading:
                if line.strip() == "":  # Stop at an empty line to indicate end of deck
                    break
                deck_contents.append(line.strip())
            elif deck_name in line:
                start_reading = True
                
    for deck_card in deck_contents:
        time.sleep(0.5)
        card = search_card(deck_card)
        print_formatted_card(card)
            

def main():
    while True:
        print("\nMagic: The Gathering Deck Builder")
        print("1. Search for a card")
        print("2. Open Deck Manager")
        print("6. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            card_name = input("Enter card name: ")
            card = search_card(card_name)
            print_formatted_card(card)

        elif choice == "2":
            deck_manager()

        else:
            break
            
main()
