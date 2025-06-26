import tkinter as tk
from tkinter import messagebox
from modules.logic import log_task_and_get_pokemon, load_user_data, transfer_pokemon
from modules.logic import save_user_data, DATA_PATH

class FocusDexApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FocusDex")
        self.root.geometry("300x300")

        self.create_main_menu()
        self.active_window = None

    def close_active_window(self):
        if self.active_window and self.active_window.winfo_exists():
            self.active_window.destroy()
            self.active_window = None

    def set_window_closed(self, window):
        if self.active_window == window:
            self.active_window = None
        window.destroy()

    def create_main_menu(self):
        title = tk.Label(self.root, text="FocusDex Menu", font=("Helvetica", 16, "bold"))
        title.pack(pady=20)

        task_button = tk.Button(self.root, text="Tasks", width=20, command=self.open_task_menu)
        task_button.pack(pady=5)

        pokemon_button = tk.Button(self.root, text="Pokémon", width=20, command=self.open_pokemon_menu)
        pokemon_button.pack(pady=5)

        candies_button = tk.Button(self.root, text="Candies", width=20, command=self.open_candy_menu)
        candies_button.pack(pady=5)

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
                description_label.config(text="One set of exercise = One Pokémon caught")
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
        description_label = tk.Label(task_window, text="One set of exercise = One Pokémon caught",
                                    font=("Helvetica", 10), wraplength=300)
        description_label.pack(pady=10)

        # --- Utfør-knapp ---
        def submit_task():
            activity = current_activity.get()
            pokemon = log_task_and_get_pokemon(activity)
            tk.messagebox.showinfo("Congratulations!", f"You got a {pokemon} for completing {activity.lower()}!")
            task_window.destroy()

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
                    text = f"{entry['date']} at {entry['time']} → {entry['pokemon']}"
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

        candy_window.title("Candy stack")
        candy_window.geometry("300x400")

        label = tk.Label(candy_window, text="Your Pokémon-candies", font=("Helvetica", 12))
        label.pack(pady=10)

        if not candy_data:
            tk.Label(candy_window, text="No candies yet!").pack()
        else:
            for name, count in candy_data.items():
                text = f"{name}: {count} candy"
                tk.Label(candy_window, text=text, anchor="w").pack(pady=2)    

    def open_pokemon_detail(self, name):
        detail_window = tk.Toplevel(self.root)
        detail_window.title(name)
        detail_window.geometry("250x150")

        label = tk.Label(detail_window, text=f"{name}", font=("Helvetica", 14))
        label.pack(pady=10)

        def confirm_transfer():
            success = transfer_pokemon(name)
            if success:
                tk.messagebox.showinfo("Transferred", f"{name} got transferred! You received a {name} candy.")
                detail_window.destroy()
                self.refresh_pokemon_grid()
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
        poke_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(poke_window))

        poke_window.title("Your Pokémon")
        poke_window.geometry("360x400")

        label = tk.Label(poke_window, text="Your Pokémon-box", font=("Helvetica", 12))
        label.pack(pady=10)

        # Lag canvas + scrollbar
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

        if not pokemon_list:
            empty_label = tk.Label(scroll_frame, text="No Pokémon yet!")
            empty_label.grid(row=0, column=0, pady=10)
        else:
            def on_click(poke_name):
                self.open_pokemon_detail(poke_name)

            for i, poke in enumerate(pokemon_list):
                name = poke["name"]
                level = poke["level"]
                display_text = f"{name} Lv {level}"
                row = i // 3  # 3 kolonner per rad
                col = i % 3

                poke_box = tk.Button(scroll_frame, text=display_text, relief="groove", width=12, height=3,
                    command=lambda n=name: on_click(n))
                poke_box.grid(row=row, column=col, padx=5, pady=5)

    def refresh_pokemon_grid(self):
        # Fjern eksisterende widgets
        for widget in self.poke_scroll_frame.winfo_children():
            widget.destroy()

        data = load_user_data()
        pokemon_list = data.get("pokemon", [])

        if not pokemon_list:
            empty_label = tk.Label(self.poke_scroll_frame, text="No Pokémon yet!")
            empty_label.grid(row=0, column=0, pady=10)
        else:
            def on_click(poke_name):
                self.open_pokemon_detail(poke_name)

            for i, name in enumerate(pokemon_list):
                row = i // 3
                col = i % 3
                poke_box = tk.Button(
                    self.poke_scroll_frame,
                    text=name,
                    relief="groove",
                    width=12,
                    height=3,
                    command=lambda n=name: on_click(n)
                )
                poke_box.grid(row=row, column=col, padx=5, pady=5)

    def open_options_menu(self):
        self.close_active_window()

        options_window = tk.Toplevel(self.root)
        self.active_window = options_window
        options_window.protocol("WM_DELETE_WINDOW", lambda: self.set_window_closed(options_window))

        options_window.title("Options")
        options_window.geometry("300x200")

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
     
    def run(self):
        self.root.mainloop()
