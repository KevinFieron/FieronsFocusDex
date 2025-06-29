import json
import os
import random
import uuid
from datetime import datetime
from modules.pokemon_data import POKEMON_DATABASE
from modules.items_data import ITEMS_DATABASE, get_random_item_name


DATA_PATH = "data/user_data.json"

NATURES = ["Modest", "Adamant", "Timid", "Jolly", "Calm", "Careful", "Bold", "Impish", "Brave", "Relaxed", "Quiet", "Sassy", "Hasty", "Naive"]

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

def get_random_pokemon_name():
    from modules.pokemon_data import POKEMON_DATABASE

    rarity_pool = {
        "common": [],
        "rare": [],
        "legendary": []
    }

    for name, props in POKEMON_DATABASE.items():
        rarity = props.get("rarity", "common")
        if rarity in rarity_pool:
            rarity_pool[rarity].append(name)

    rand = random.random()
    if rand < 0.01:
        rarity = "legendary"
    elif rand < 0.11:
        rarity = "rare"
    else:
        rarity = "common"

    return random.choice(rarity_pool[rarity])

def log_task_and_get_pokemon(activity):
    data = load_user_data()

    name = get_random_pokemon_name()
    now = datetime.now()

    iv = {
    "HP": random.randint(0, 31),
    "Attack": random.randint(0, 31),
    "Defense": random.randint(0, 31),
    "Sp. Atk": random.randint(0, 31),
    "Sp. Def": random.randint(0, 31),
    "Speed": random.randint(0, 31)
    }

    gender = assign_gender(name)

    is_shiny = random.random() < 0.001  # 0.1% shiny-sjanse

    # Lag nytt Pokémon-objekt med unik ID, level og timestamp
    new_pokemon = {
        "id": str(uuid.uuid4()),
        "name": name,
        "level": 1,
        "nature": random.choice(NATURES),
        "iv": iv,
        "caught_at": now.strftime("%Y-%m-%d %H:%M"),
        "gender": gender,
        "shiny": is_shiny
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

def log_task_and_get_item(activity):
    data = load_user_data()

    # Velg tilfeldig item via funksjonen
    item = get_random_item_name()

    # Oppdater brukerens item-beholdning
    if "items" not in data:
        data["items"] = {}
    data["items"][item] = data["items"].get(item, 0) + 1

    # Logg aktivitet
    now = datetime.now()
    log_entry = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "activity": activity,
        "item": item
    }

    if "task_log" not in data:
        data["task_log"] = []
    data["task_log"].append(log_entry)

    save_user_data(data)
    return item

def assign_gender(name):
    from modules.pokemon_data import POKEMON_DATABASE
    group = POKEMON_DATABASE.get(name, {}).get("gender_ratio", "B")  # Default til "B"

    roll = random.random()

    if group == "A":  # 87.5% Male
        return "Male" if roll < 0.875 else "Female"
    elif group == "B":  # 50/50
        return "Male" if roll < 0.5 else "Female"
    elif group == "C":  # 25% Male
        return "Male" if roll < 0.25 else "Female"
    elif group == "D":  # 75% Male
        return "Male" if roll < 0.75 else "Female"
    elif group == "E":  # 12.5% Male
        return "Male" if roll < 0.125 else "Female"
    elif group == "genderless":
        return "Genderless"
    else:
        return "Male" if roll < 0.5 else "Female"  # Default fallback

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

import shutil

SAVES_DIR = "saves"

def save_current_data(save_name):
    os.makedirs(SAVES_DIR, exist_ok=True)
    target_path = os.path.join(SAVES_DIR, f"{save_name}.json")
    shutil.copy(DATA_PATH, target_path)

def load_saved_data(save_name):
    target_path = os.path.join(SAVES_DIR, f"{save_name}.json")
    if os.path.exists(target_path):
        shutil.copy(target_path, DATA_PATH)
        return True
    return False

def list_saves():
    if not os.path.exists(SAVES_DIR):
        return []
    return [f[:-5] for f in os.listdir(SAVES_DIR) if f.endswith(".json")]
