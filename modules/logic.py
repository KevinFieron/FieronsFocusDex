import json
import os
import random
import uuid
from datetime import datetime

DATA_PATH = "data/user_data.json"

# Sjeldne (20 % samlet)
RARE_POKEMON = ["Charmander", "Bulbasaur", "Squirtle", "Pikachu", "Eevee"]

# Vanlige (80 % samlet)
COMMON_POKEMON = ["Vulpix", "Growlithe", "Ponyta", "Slugma", "Houndour"]

NATURES = ["Modest", "Adamant", "Timid", "Jolly", "Calm", "Careful", "Bold", "Impish"]

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

    # Velg Pokémon
    if random.random() < 0.2:
        name = random.choice(RARE_POKEMON)
    else:
        name = random.choice(COMMON_POKEMON)

    now = datetime.now()

    iv = {
    "HP": random.randint(0, 31),
    "Attack": random.randint(0, 31),
    "Defense": random.randint(0, 31),
    "Sp. Atk": random.randint(0, 31),
    "Sp. Def": random.randint(0, 31),
    "Speed": random.randint(0, 31)
    }

    # Lag nytt Pokémon-objekt med unik ID, level og timestamp
    new_pokemon = {
        "id": str(uuid.uuid4()),
        "name": name,
        "level": 1,
        "iv": iv,
        "nature": random.choice(NATURES),
        "caught_at": now.strftime("%Y-%m-%d %H:%M")
    }

    if "pokemon" not in data:
        data["pokemon"] = []
    data["pokemon"].append(new_pokemon)

    if "task_log" not in data:
        data["task_log"] = []

    log_entry = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "activity": activity,
        "pokemon": new_pokemon
    }

    data["task_log"].append(log_entry)
    save_user_data(data)
    return new_pokemon

def transfer_pokemon(pokemon_id):
    data = load_user_data()

    for i, poke in enumerate(data["pokemon"]):
        if poke["id"] == pokemon_id:
            name = poke["name"]
            del data["pokemon"][i]
            break
    else:
        return False  # Fant ingen Pokémon med den ID-en

    if "candy" not in data:
        data["candy"] = {}
    data["candy"][name] = data["candy"].get(name, 0) + 1
    save_user_data(data)
    return True

def level_up_pokemon(pokemon_id):
    data = load_user_data()
    pokemon_list = data.get("pokemon", [])
    candy_data = data.get("candy", {})

    for poke in pokemon_list:
        if poke["id"] == pokemon_id:
            pokemon = poke
            break
    else:
        return False, "Pokémon not found"

    name = pokemon["name"]
    level = pokemon.get("level", 1)
    if level >= 100:
        return False, "Already at max level"

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

    current_candy = candy_data.get(name, 0)
    if current_candy < cost:
        return False, f"Not enough {name} candy (need {cost})"

    pokemon["level"] += 1
    candy_data[name] -= cost

    save_user_data(data)
    return True, f"{name} is now level {pokemon['level']}!"
