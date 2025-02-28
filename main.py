import requests

def search_card(card_name):
    """Searches for a card by name using Scryfall's fuzzy search."""
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name.replace(' ', '%20')}"
    response = requests.get(url)
    
    if response.status_code == 200:
        card_data = response.json()
        return card_data
    else:
        return {"error": "Card not found"}
    
card = search_card("brushwagg")
print(card["name"], "-", card["mana_cost"])
