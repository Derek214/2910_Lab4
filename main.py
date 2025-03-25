import requests
import time
import os
import random
import re

def search_card(card_name):
    # Searches for a card by name using Scryfall's fuzzy search as to not require exact matches
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name.replace(' ', '%20')}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return "error: Card not found"
    
def get_random_card():
    # Fetches a completely random Magic card
    url = "https://api.scryfall.com/cards/random"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return "error: Failed to get a random card"

# This could be expanded to allow more parameters or reused for a non-random parameterized search
def parameterized_random_card(color=None, format=None):
    base_url = "https://api.scryfall.com/cards/search"
    
    # Build query parameters
    query = ""
    if color:
        query += f" c:{color}"  
    if format:
        query += f" f:{format}" 
        
    params = {"q": query.strip()}  # Remove extra spaces

    # Send request
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        card_data = response.json()
        
        # Extract names properly
        cards = [card['name'] for card in card_data.get("data", [])]

        if cards:  # Ensure there's at least one match
            return random.choice(cards)
        else:
            return "error: No Matching Cards Found"

    return f"error: API request failed with status {response.status_code}"

    
def print_formatted_card(card_data):
    
    if "error" in card_data:
        print(card_data)
    else:
        # Handle double-faced cards
        if 'card_faces' in card_data:
            # If the card has multiple faces, loop through them
            for face in card_data['card_faces']:
                mana_cost = face.get('mana_cost', 'N/A')  # Use 'N/A' if mana_cost is not available
                print(f"\n{face['name']} - {mana_cost} ({face['type_line']})")
                print("------------------------")
                print(face['oracle_text'])
                
            print(f"${card_data['prices']['usd']}")
        else:
            # Single-faced card
            print(f"\n{card_data['name']} - {card_data['mana_cost']} ({card_data['type_line']})")
            print("------------------------")
            print(card_data['oracle_text'])
            print(f"${card_data['prices']['usd']}")
    
def deck_manager(random):
    
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
    
    if random:
        with open("decks.txt", 'a') as file:
            
            color = input("Input a color for the deck (W, U, B, R, G): ")
            format = input("Input a format for the deck (standard, commander, modern, legacy, pauper): ")
            if format == "commander":
                for i in range(100):
                    time.sleep(0.3)
                    file.write(f"{parameterized_random_card(color, format)}\n")
            else:
                for i in range(60):
                    time.sleep(0.3)
                    file.write(f"{parameterized_random_card(color, format)}\n")

    
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
        if "error" in card:
            print(card)
        else:
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
        time.sleep(0.3)
        card = search_card(deck_card)
        print_formatted_card(card)
            
def import_deck(deck_name):
    deck_name = f"{deck_name}"
    deck_name = deck_name.replace(" ", "_")
    deck_contents = []        
    with open(f"{deck_name}.txt", 'r') as file:
        for line in file:
            parts = line.strip().split(" ")
            card_name = " ".join(parts[1:])  # Start after quantity
            card_name = re.sub(r"\(\w+\) \d+", "", card_name).strip()  # Remove set number
            card_name = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}', "", card_name).strip()

            card_class = parts[-1].strip("[]").lower()  # Extract classification
            
            if card_class != "land" and card_class != "commander{top}":
                deck_contents.append(f"{card_name}|{card_class}")  # Format as "Name|Category"
        
        filter = input("Remove by category (y/n): ")
        if filter == "y":
            category = input("Choose a Category (will differ depending on your deck's categories): ").lower()
            deck_contents = filter_by_category(deck_contents, category)
        
        card_names = [card.split("|")[0] for card in deck_contents]
        card_cutter(card_names)

            
def card_cutter(card_names):
        
    if len(card_names) == 1:
        print(f"Remove {card_names[0]}")
        return
    if len(card_names) == 0:
        print("The deck contains no cards with that category")
        return
        
    num1, num2 = random.sample(range(0, len(card_names)), 2)
    
    first_card = search_card(card_names[num1])
    second_card = search_card(card_names[num2])
    
    print_formatted_card(first_card)
    print_formatted_card(second_card)
    
    choice = input("\n\033[31mChoose the card you prefer (1 or 2): \033[0m")
    print("\033[31m=================================================================\033[0m")
    if choice == "1":
        del card_names[num1]
    elif choice == "2":
        del card_names[num2]
        
    card_cutter(card_names)
            
    
def filter_by_category(deck_contents, category):
    filtered_deck = [card for card in deck_contents if card.split("|")[1] == category]
    return filtered_deck

def main():
    while True:
        print("\nMagic: The Gathering Deck Builder")
        print("1. Search for a Card")
        print("2. Open Deck Manager")
        print("3. Search Random Card")
        print("4. Generate Random Deck")
        print("5. Cut Cards from an Imported Deck")
        print("6. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            card_name = input("Enter card name: ")
            card = search_card(card_name)
            print_formatted_card(card)

        elif choice == "2":
            deck_manager(random=False)
            
        elif choice == "3":
            card = get_random_card()
            print_formatted_card(card)
        
        elif choice == "4":
            deck_manager(random=True)
            
        elif choice == "5":
            deck_name = input("Enter the name of the deck that you would like to cut cards from: \n").lower()
            import_deck(deck_name)

        else:
            break
            
main()
