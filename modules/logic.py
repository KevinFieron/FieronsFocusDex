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
