import json
import os
import random
from datetime import datetime

DATA_PATH = "data/user_data.json"

# Sjeldne (20 % samlet)
RARE_POKEMON = ["Charmander", "Bulbasaur", "Squirtle", "Pikachu", "Eevee"]

# Vanlige (80 % samlet)
COMMON_POKEMON = ["Vulpix", "Growlithe", "Ponyta", "Slugma", "Houndour"]

def load_user_data():
    if not os.path.exists(DATA_PATH):
        return {"pokemon": [], "task_log": [], "candy": {}}

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    # Sørg for at alle nødvendige nøkler finnes
    if "pokemon" not in data:
        data["pokemon"] = []
    if "task_log" not in data:
        data["task_log"] = []
    if "candy" not in data:
        data["candy"] = {}

    return data

def save_user_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

def log_task_and_get_pokemon(activity):
    data = load_user_data()

    if random.random() < 0.2:
        name = random.choice(RARE_POKEMON)
    else:
        name = random.choice(COMMON_POKEMON)

    new_pokemon = {"name": name, "level": 1}

    if "pokemon" not in data:
        data["pokemon"] = []

    data["pokemon"].append(new_pokemon)

    if "task_log" not in data:
        data["task_log"] = []

    now = datetime.now()
    log_entry = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "activity": activity,
        "pokemon": name  # fortsatt bare navn i loggen
    }

    data["task_log"].append(log_entry)
    save_user_data(data)
    return name

def transfer_pokemon(name):
    data = load_user_data()

    for i, poke in enumerate(data["pokemon"]):
        if poke["name"] == name:
            del data["pokemon"][i]
            break
    else:
        return False  # Fant ingen Pokémon med det navnet

    # Candy-håndtering skjer kun hvis vi fant og slettet en Pokémon
    if "candy" not in data:
        data["candy"] = {}
    data["candy"][name] = data["candy"].get(name, 0) + 1
    save_user_data(data)
    return True

def level_up_pokemon(pokemon_name, pokemon_index):
    data = load_user_data()
    pokemon_list = data.get("pokemon", [])
    candy_data = data.get("candy", {})

    if pokemon_index >= len(pokemon_list):
        return False, "Invalid index"

    pokemon = pokemon_list[pokemon_index]

    if pokemon["name"] != pokemon_name:
        return False, "Pokémon mismatch"

    level = pokemon.get("level", 1)
    if level >= 100:
        return False, "Already at max level"

    # Bestem candy-kostnad basert på level
    if level < 20:
        cost = 1
    elif level < 40:
        cost = 2
    elif level < 60:
        cost = 3
    elif level < 80:
        cost = 4
    else:
        cost = 5

    current_candy = candy_data.get(pokemon_name, 0)
    if current_candy < cost:
        return False, f"Not enough {pokemon_name} candy (need {cost})"

    # Oppdater data
    pokemon["level"] += 1
    candy_data[pokemon_name] -= cost

    save_user_data(data)
    return True, f"{pokemon_name} is now level {pokemon['level']}!"
