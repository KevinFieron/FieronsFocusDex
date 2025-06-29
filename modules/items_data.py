# modules/items_data.py

ITEMS_DATABASE = {
    "Rare Candy": {
        "description": "Instantly level up a Pokémon by 1 level."
    },
    "Everstone": {
        "description": "Used to pass on natures after breeding."
    },
    "Power Weight": {
        "description": "Used to pass on HP IVs after breeding."
    },
    "Power Bracer": {
        "description": "Used to pass on Attack IVs after breeding."
    },
    "Power Belt": {
        "description": "Used to pass on Defense IVs after breeding."
    },
    "Power Lens": {
        "description": "Used to pass on Sp.Atk IVs after breeding."
    },
    "Power Band": {
        "description": "Used to pass on Sp.Def IVs after breeding."
    },
    "Power Anklet": {
        "description": "Used to pass on Speed IVs after breeding."
    }
}

def get_random_item_name():
    import random
    return random.choice(list(ITEMS_DATABASE.keys()))
