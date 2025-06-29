import tkinter as tk
from tkinter import messagebox
from modules.logic import log_task_and_get_pokemon, load_user_data, transfer_pokemon, level_up_pokemon
from modules.logic import save_user_data, DATA_PATH, log_task_and_get_item
from modules.pokemon_data import POKEMON_DATABASE
from modules.items_data import ITEMS_DATABASE

import os
import shutil
from tkinter import simpledialog

class FocusDexApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FocusDex")
        self.root.geometry("300x300")

        self.create_main_menu()
        self.active_window = None
        self.pokemon_window = None

    def close_active_window(self):
        if self.active_window and self.active_window.winfo_exists():
            self.active_window.destroy()
            self.active_window = None

    def set_window_closed(self, window):
        if window and window.winfo_exists():
            window.destroy()
        if self.active_window == window:
            self.active_window = None
        if self.pokemon_window == window:
            self.pokemon_window = None

    def refresh_pokemon_menu(self):
        if self.pokemon_window and self.pokemon_window.winfo_exists():
            self.pokemon_window.destroy()
        self.open_pokemon_menu()

    def create_main_menu(self):
        title = tk.Label(self.root, text="FocusDex Menu", font=("Helvetica", 16, "bold"))
        title.pack(pady=20)

        task_button = tk.Button(self.root, text="Tasks", width=20, command=self.open_task_menu)
        task_button.pack(pady=5)

        pokemon_button = tk.Button(self.root, text="Pokémon", width=20, command=self.open_pokemon_menu)
        pokemon_button.pack(pady=5)

        candies_button = tk.Button(self.root, text="Candies", width=20, command=self.open_candy_menu)
        candies_button.pack(pady=5)

        items_button = tk.Button(self.root, text="Items", width=20, command=self.open_items_menu)
        items_button.pack(pady=5) 

        breeding_button = tk.Button(self.root, text="Breeding", width=20, command=self.open_breeding_menu)
        breeding_button.pack(pady=5)

        options_button = tk.Button(self.root, text="Options", width=20, command=self.open_options_menu)
        options_button.pack(pady=5)

    def open_task_menu(self):
        self.close_active_window()

        task_window = tk.Toplevel(self.root)
        self.active_window = task_window
        task_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(task_window))

        task_window.title("Log Activity")
        task_window.geometry("400x300")

        current_activity = tk.StringVar(value="Exercise")

        # --- Knappene for valg ---
        button_frame = tk.Frame(task_window)
        button_frame.pack(pady=10)

        def update_activity(activity):
            current_activity.set(activity)
            if activity == "Exercise":
                exercise_btn.config(relief="sunken", bg="lightblue")
                work_btn.config(relief="raised", bg="SystemButtonFace")
                description_label.config(text="One Pokémon caught (80%) or one item found (20%)")
            else:
                work_btn.config(relief="sunken", bg="lightblue")
                exercise_btn.config(relief="raised", bg="SystemButtonFace")
                description_label.config(text="One hour of work = One Pokémon caught")

        exercise_btn = tk.Button(button_frame, text="Exercise", width=15,
                                command=lambda: update_activity("Exercise"))
        exercise_btn.grid(row=0, column=0, padx=10)

        work_btn = tk.Button(button_frame, text="Work", width=15,
                            command=lambda: update_activity("Work"))
        work_btn.grid(row=0, column=1, padx=10)

        # --- Beskrivelse ---
        description_label = tk.Label(task_window, text="One Pokémon caught (80%) or one item found (20%)",
                                    font=("Helvetica", 10), wraplength=300)
        description_label.pack(pady=10)

        # --- Utfør-knapp ---
        def submit_task():
            activity = current_activity.get()

            if activity == "Exercise":
                import random
                if random.random() < 0.2:
                    item = log_task_and_get_item("Exercise")
                    messagebox.showinfo("Nice!", f"You found a {item} from exercise!")
                else:
                    pokemon = log_task_and_get_pokemon("Exercise")
                    is_shiny = pokemon.get("shiny", False)
                    name = pokemon["name"]
                    if is_shiny:
                        messagebox.showinfo("Congratulations!", f"★ Congratulations! You just caught a SHINY {name}!", parent=task_window)
                    else:
                        messagebox.showinfo("Nice!", f"You caught a {name}!")
                    self.refresh_pokemon_menu()
            else:
                pokemon = log_task_and_get_pokemon("Work")
                is_shiny = pokemon.get("shiny", False)
                name = pokemon["name"]
                if is_shiny:
                    messagebox.showinfo("Congratulations!", f"★ Congratulations! You just caught a SHINY {name}!", parent=task_window)
                else:
                    messagebox.showinfo("Nice!", f"You caught a {name}!")

            task_window.destroy()
            self.refresh_pokemon_menu()

        execute_button = tk.Button(task_window, text="Execute", width=20, command=submit_task)
        execute_button.pack(pady=10)

        # --- Logg-knapp ---
        def show_log():
            log_data = load_user_data().get("task_log", [])
            if not log_data:
                tk.messagebox.showinfo("Log", "No activity has been logged yet.")
                return

            exercise_log = [entry for entry in log_data if entry["activity"] == "Exercise"]
            work_log = [entry for entry in log_data if entry["activity"] == "Work"]

            log_window = tk.Toplevel(task_window)
            log_window.title("Activity Log")
            log_window.geometry("500x400")

            canvas = tk.Canvas(log_window)
            scrollbar = tk.Scrollbar(log_window, orient="vertical", command=canvas.yview)
            scroll_frame = tk.Frame(canvas)

            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            def display_section(title, log_list):
                total = len(log_list)
                recent = log_list[-10:] if total > 10 else log_list

                header = f"{title} ({total} total)"
                tk.Label(scroll_frame, text=header, font=("Helvetica", 12, "bold")).pack(pady=(10, 2))

                for entry in reversed(recent):
                    text = f"{entry['date']} at {entry['time']} → {entry['pokemon']['name']}"
                    tk.Label(scroll_frame, text=text, anchor="w", padx=10).pack(fill="x", pady=1)

            display_section("Exercise", exercise_log)
            display_section("Work", work_log)

        log_button = tk.Button(task_window, text="View Log", width=20, command=show_log)
        log_button.pack(pady=5)

    def open_candy_menu(self):
        data = load_user_data()
        candy_data = data.get("candy", {})

        self.close_active_window()
        candy_window = tk.Toplevel(self.root)
        self.active_window = candy_window
        candy_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(candy_window))

        candy_window.title("Candy Storage")
        candy_window.geometry("300x400")

        label = tk.Label(candy_window, text="Your Pokémon Candies", font=("Helvetica", 12))
        label.pack(pady=10)

        if not candy_data:
            tk.Label(candy_window, text="No candy yet!").pack()
        else:
            for name, count in candy_data.items():
                frame = tk.Frame(candy_window)
                frame.pack(pady=2, fill="x")

                text = f"{name}: {count} candy"
                tk.Label(frame, text=text, anchor="w").pack(side="left", padx=5)

                def create_level_up_handler(poke_name):
                    return lambda: self.open_level_up_menu(poke_name)

                level_up_btn = tk.Button(frame, text="Use", command=create_level_up_handler(name))
                level_up_btn.pack(side="right", padx=5)

    def open_level_up_menu(self, name):
        data = load_user_data()
        matching_pokemon = [(i, p) for i, p in enumerate(data.get("pokemon", [])) if p["name"] == name]

        if not matching_pokemon:
            messagebox.showinfo("No Pokémon", f"You have no {name} Pokémon.")
            return

        level_window = tk.Toplevel(self.root)
        level_window.title(f"Level up {name}")
        level_window.geometry("300x300")

        tk.Label(level_window, text=f"Select a {name} to level up:", font=("Helvetica", 12)).pack(pady=10)

        for idx, poke in matching_pokemon:
            lvl = poke.get("level", 1)
            poke_id = poke["id"]
            text = f"{name} Lv {lvl}"

            def create_level_up_fn(pid=poke_id):
                def level_up_action():
                    success, msg = level_up_pokemon(pid)
                    messagebox.showinfo("Level Up", msg)
                    if success:
                        level_window.destroy()
                        self.open_candy_menu()
                        self.refresh_pokemon_menu()
                return level_up_action

            btn = tk.Button(level_window, text=text, command=create_level_up_fn())
            btn.pack(pady=3)

    def open_pokemon_detail(self, poke_id):
        data = load_user_data()
        pokemon = next((p for p in data.get("pokemon", []) if p["id"] == poke_id), None)

        if not pokemon:
            tk.messagebox.showerror("Error", "Pokémon not found.")
            return

        detail_window = tk.Toplevel(self.root)
        detail_window.title(pokemon["name"])
        detail_window.geometry("300x330")

        header = tk.Frame(detail_window)
        header.pack(pady=5)

        name_lbl = tk.Label(header, text=f"{pokemon['name']} Lv {pokemon['level']}", font=("Helvetica", 14))
        name_lbl.pack(side="left")
        if pokemon.get("shiny"):
            tk.Label(header, text="★", fg="gold", font=("Helvetica", 14, "bold")).pack(side="left", padx=5)

        # Pokedex-nummer
        dex_num = POKEMON_DATABASE.get(pokemon["name"], {}).get("dex")
        if dex_num:
            tk.Label(detail_window, text=f"#{dex_num}", font=("Helvetica", 10)).pack(pady=(0, 5))

        if pokemon.get("gender") == "Male":
            tk.Label(header, text="♂", fg="blue", font=("Helvetica", 14, "bold")).pack(side="left", padx=5)
        elif pokemon.get("gender") == "Female":
            tk.Label(header, text="♀", fg="red", font=("Helvetica", 14, "bold")).pack(side="left", padx=5)

        ivs = pokemon.get("iv", {})
        stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
        total = sum(ivs.get(stat, 0) for stat in stats)

        table = tk.Frame(detail_window)
        table.pack(pady=5)
        for i, stat in enumerate(stats):
            value = ivs.get(stat, 0)
            tk.Label(table, text=stat, width=10, anchor="w").grid(row=i, column=0)

            if value == 0:
                color = "red"
                font = ("Helvetica", 10)
            elif value == 31:
                color = "green"
                font = ("Helvetica", 10, "bold")
            else:
                color = "black"
                font = ("Helvetica", 10)

            tk.Label(table, text=str(value), width=10, anchor="e", fg=color, font=font).grid(row=i, column=1)

        tk.Label(table, text="Total", width=10, anchor="w", font=("Helvetica", 10, "bold")).grid(row=6, column=0)
        tk.Label(table, text=f"{total} / 186", width=10, anchor="e", font=("Helvetica", 10, "bold")).grid(row=6, column=1)

        nature = pokemon.get("nature", "Unknown")
        tk.Label(detail_window, text=f"Nature: {nature}", font=("Helvetica", 10)).pack(pady=2)

        caught_at = pokemon.get("caught_at", "Unknown")
        tk.Label(detail_window, text=f"Caught at: {caught_at}", font=("Helvetica", 10)).pack(pady=2)

        def confirm_transfer():
            success = transfer_pokemon(poke_id)
            if success:
                tk.messagebox.showinfo("Transferred", f"{pokemon['name']} got transferred! You received a {pokemon['name']} candy.")
                detail_window.destroy()
                self.refresh_pokemon_menu()
            else:
                tk.messagebox.showerror("Error", "Something went wrong.")

        transfer_btn = tk.Button(detail_window, text="Transfer Pokémon", command=confirm_transfer)
        transfer_btn.pack(pady=10)

    def open_pokemon_menu(self):
        data = load_user_data()
        pokemon_list = data.get("pokemon", [])

        self.close_active_window()

        poke_window = tk.Toplevel(self.root)
        self.active_window = poke_window
        self.pokemon_window = poke_window
        poke_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(poke_window))

        poke_window.title("Your Pokémon")
        poke_window.geometry("360x400")

        label = tk.Label(poke_window, text="Your Pokémon-box", font=("Helvetica", 12))
        label.pack(pady=10)

        canvas = tk.Canvas(poke_window, height=300)
        scrollbar = tk.Scrollbar(poke_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        self.poke_scroll_frame = scroll_frame

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, poke in enumerate(pokemon_list):
            name = poke["name"]
            level = poke["level"]
            poke_id = poke["id"]
            gender = poke.get("gender", "")
            gender_symbol = ""
            color = "black"
            if gender == "Male":
                gender_symbol = "♂"
                color = "blue"
            elif gender == "Female":
                gender_symbol = "♀"
                color = "red"

            is_shiny = poke.get("shiny", False)
            shiny_star = "★ " if is_shiny else ""
            display_text = f"{shiny_star}{name} Lv {level} {gender_symbol}"
            row = i // 3
            col = i % 3

            poke_box = tk.Button(
                scroll_frame,
                text=display_text,
                relief="groove",
                width=12,
                height=3,
                fg="gold" if is_shiny else color,
                command=lambda pid=poke_id: self.open_pokemon_detail(pid)
            )

            poke_box.grid(row=row, column=col, padx=5, pady=5)

    def refresh_pokemon_grid(self):
        for widget in self.poke_scroll_frame.winfo_children():
            widget.destroy()

        data = load_user_data()
        pokemon_list = data.get("pokemon", [])

        if not pokemon_list:
            empty_label = tk.Label(self.poke_scroll_frame, text="No Pokémon yet!")
            empty_label.grid(row=0, column=0, pady=10)
        else:
            for i, poke in enumerate(pokemon_list):
                name = poke["name"]
                level = poke.get("level", 1)
                poke_id = poke["id"]  # <-- Bruk ID som nøkkel
                display_text = f"{name} Lv {level}"
                row = i // 3
                col = i % 3
                poke_box = tk.Button(
                    self.poke_scroll_frame,
                    text=display_text,
                    relief="groove",
                    width=12,
                    height=3,
                    command=lambda pid=poke_id: self.open_pokemon_detail(pid)
                )
                poke_box.grid(row=row, column=col, padx=5, pady=5)

    def open_items_menu(self):
        self.close_active_window()
        item_window = tk.Toplevel(self.root)
        self.active_window = item_window
        item_window.title("Your Items")
        item_window.geometry("400x350")

        label = tk.Label(item_window, text="Your Items", font=("Helvetica", 12))
        label.pack(pady=10)

        data = load_user_data()
        user_items = data.get("items", {})

        for item_name, item_info in ITEMS_DATABASE.items():
            count = user_items.get(item_name, 0)
            frame = tk.Frame(item_window)
            frame.pack(pady=3, padx=10, fill="x")

            tk.Label(frame, text=f"{item_name} ({count})", anchor="w").pack(side="left")
            tk.Label(frame, text=item_info.get("description", ""), anchor="e", fg="gray").pack(side="right")

    def open_breeding_menu(self):
        self.close_active_window()

        breeding_window = tk.Toplevel(self.root)
        self.active_window = breeding_window
        breeding_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(breeding_window))

        breeding_window.title("Breeding")
        breeding_window.geometry("300x200")

        label = tk.Label(breeding_window, text="Breeding Center (coming soon!)", font=("Helvetica", 12))
        label.pack(pady=40)

    def open_options_menu(self):
        self.close_active_window()

        options_window = tk.Toplevel(self.root)
        self.active_window = options_window
        options_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(options_window))

        options_window.title("Options")
        options_window.geometry("300x250")

        label = tk.Label(options_window, text="Options", font=("Helvetica", 14, "bold"))
        label.pack(pady=20)

        def reset_all_data():
            confirm = tk.messagebox.askyesno("Confirm reset", "Are you sure you want to reset all data?")
            if confirm:
                with open(DATA_PATH, "w") as f:
                    f.write("{}")
                tk.messagebox.showinfo("Reset", "All data is now reset!")
                options_window.destroy()

        reset_button = tk.Button(options_window, text="Reset all data", fg="red", command=reset_all_data)
        reset_button.pack(pady=10)

        save_button = tk.Button(options_window, text="Save current progress", command=self.save_progress)
        save_button.pack(pady=5)

        load_button = tk.Button(options_window, text="Load saved progress", command=self.load_progress)
        load_button.pack(pady=5)

    def save_progress(self):
        save_name = simpledialog.askstring("Save Progress", "Enter a name for your save file:")
        if not save_name:
            return

        save_name = save_name.strip().replace(" ", "_")
        save_path = os.path.join("saves", f"{save_name}.json")

        try:
            shutil.copyfile(DATA_PATH, save_path)
            tk.messagebox.showinfo("Success", f"Progress saved as '{save_name}'!")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to save progress: {str(e)}")

    def load_progress(self):
        save_files = [f for f in os.listdir("saves") if f.endswith(".json")]
        if not save_files:
            tk.messagebox.showinfo("No Saves", "No saved files found.")
            return

        load_window = tk.Toplevel(self.root)
        load_window.title("Load Save")
        load_window.geometry("300x250")

        tk.Label(load_window, text="Select a save to load:", font=("Helvetica", 12)).pack(pady=10)

        for save_file in save_files:
            def load_selected(file=save_file):
                try:
                    src_path = os.path.join("saves", file)
                    with open(src_path, "r") as src, open(DATA_PATH, "w") as dst:
                        dst.write(src.read())
                    tk.messagebox.showinfo("Loaded", f"Loaded save: {file}")
                    load_window.destroy()
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to load save: {str(e)}")

            btn = tk.Button(load_window, text=save_file.replace(".json", ""), command=load_selected)
            btn.pack(pady=3)

    def run(self):
        self.root.mainloop()
