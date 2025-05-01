import tkinter as tk
from tkinter import ttk
import random
import json
import os
import sys
import re
import webbrowser

class TableManager:
    def __init__(self, json_path):
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, json_path)
        print(f"Attempting to load JSON from: {full_path}")
        if not os.path.exists(full_path):
            print(f"Error: JSON file not found at {full_path}")
            raise FileNotFoundError(f"JSON file not found: {full_path}")
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    print("Error: JSON file is empty")
                    raise ValueError("JSON file is empty")
                self.tables = json.loads(content)
            categories = list(self.tables.keys())
            print(f"Loaded {len(categories)} categories: {categories}")
            expected_tables = [
                "Background", "Random Trap", "Better Battles", "Minor Magical Items",
                "Convoker Missions", "Convoker Griffons", "Wayward Wanderers",
                "Magical Items (Birthright 2e)", "Mundane Items", "Found in a Curio Shop",
                "Encounters", "Nations and Factions"
            ]
            for table in expected_tables:
                if table in categories:
                    print(f"Confirmed: '{table}' found with subtables: {list(self.tables[table].keys())}")
                else:
                    print(f"Warning: '{table}' not found in JSON categories")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {full_path}. Details: {e}")
            print(f"File content (first 1000 chars): {content[:1000]}...")
            raise
        except Exception as e:
            print(f"Unexpected error while loading JSON: {e}")
            raise
        self.better_battles_rolls = {}

    def roll_dice(self, dice_notation):
        if not dice_notation:
            return 0
        match = re.match(r'(\d+)d(\d+)', dice_notation)
        if not match:
            return 0
        num_dice, die_size = map(int, match.groups())
        return sum(random.randint(1, die_size) for _ in range(num_dice))

    def process_siblings(self, value):
        if value == "No siblings":
            return value
        if "and" in value:
            siblings_part, half_siblings_part = value.split(" and ")
            siblings_roll = self.roll_dice(siblings_part.split()[0])
            half_siblings_roll = self.roll_dice(half_siblings_part.split()[0])
            return f"{siblings_roll} siblings and {half_siblings_roll} half-siblings"
        dice_part = value.split()[0]
        roll = self.roll_dice(dice_part)
        return f"{roll} siblings"

    def roll_griffon_name(self):
        category = "Convoker Griffons"
        prefixes = self.tables[category]["Name"]["Prefixes"]
        suffixes = self.tables[category]["Name"]["Suffixes"]
        prefix = random.choice(prefixes).split(". ", 1)[1]
        suffix = random.choice(suffixes).split(". ", 1)[1]
        return f"{prefix}{suffix}"

    def roll_griffon_companions(self):
        category = "Convoker Griffons"
        table = self.tables[category]["Companions"]
        max_roll = max(entry['max'] for entry in table)
        roll = random.randint(1, max_roll)
        for entry in table:
            if entry['min'] <= roll <= entry['max']:
                fur_color = entry.get('fur_color', 'Unknown fur color')
                feather_color = entry.get('feather_color', 'Unknown feather color')
                physical_trait = entry.get('physical_trait', 'No notable physical trait')
                disposition = entry.get('disposition', 'Unknown disposition')
                return (f"Roll {roll}:\n"
                        f"Fur Color: {fur_color}\n"
                        f"Feather Color: {feather_color}\n"
                        f"Physical Trait: {physical_trait}\n"
                        f"Disposition: {disposition}\n"
                        f"Griffon Name: {self.roll_griffon_name()}")

    def roll_convoker_missions(self):
        category = "Convoker Missions"
        table = self.tables[category]["Missions"]
        max_roll = max(entry['max'] for entry in table)
        roll = random.randint(1, max_roll)
        for entry in table:
            if entry['min'] <= roll <= entry['max']:
                antagonist = entry.get('antagonist', 'Unknown antagonist')
                trouble = entry.get('trouble', 'Unknown trouble')
                location = entry.get('location', 'Unknown location')
                obstacle = entry.get('obstacle', 'No obstacle')
                return (f"Roll {roll}:\n"
                        f"Antagonist: {antagonist}\n"
                        f"Trouble: {trouble}\n"
                        f"Location: {location}\n"
                        f"Obstacle: {obstacle}")

    def roll(self, category, subtable, curio_subtable=None):
        category_lower = category.lower()
        table = self.tables[category]

        # Special handling for "Encounters"
        if category_lower == "encounters":
            if subtable.lower() == "build an encounter - locations":
                locations_table = table["Build an Encounter"]["Locations"]
                # Roll for Environment (d12)
                environments = locations_table["Environment"]
                env_roll = random.randint(1, len(environments))
                selected_env = environments[env_roll - 1].split(". ", 1)[1]
                
                # Roll for Location type (d12)
                locations = locations_table["Location"]
                loc_roll = random.randint(1, len(locations))
                selected_loc_type = locations[loc_roll - 1].split(". ", 1)[1]
                
                # Roll for specific location (d4) based on the selected location type
                specific_locations = locations_table[selected_loc_type]
                specific_roll = random.randint(1, len(specific_locations))
                selected_specific_loc = specific_locations[specific_roll - 1].split(". ", 1)[1]
                
                return (f"Environment: {selected_env} (Roll {env_roll})\n"
                        f"Location: {selected_loc_type} - {selected_specific_loc} (Roll {loc_roll}, Roll {specific_roll})")
            
            elif subtable.lower() == "build an encounter - threats":
                threats_table = table["Build an Encounter"]["Threats"]
                # Roll for Threat type (d4)
                threats = threats_table["Threat"]
                threat_roll = random.randint(1, len(threats))
                selected_threat_type = threats[threat_roll - 1].split(". ", 1)[1]
                
                # Map threat type to its corresponding subtable
                threat_type_map = {
                    "A single, mighty foe": "Single Mighty Foes",
                    "A horde of enemies": "Hordes of Enemies",
                    "A rival or enemy faction": "Rival or Enemy Faction",
                    "A natural disaster": "Natural Disasters"
                }
                subtable_key = threat_type_map[selected_threat_type]
                
                # Roll on the corresponding subtable
                specific_threats = threats_table[subtable_key]
                specific_roll_max = len(specific_threats)  # d6 for most, d12 for Natural Disasters
                specific_roll = random.randint(1, specific_roll_max)
                selected_specific_threat = specific_threats[specific_roll - 1].split(". ", 1)[1]
                
                return (f"Threat: {selected_threat_type} - {selected_specific_threat} (Roll {threat_roll}, Roll {specific_roll})")
            
            # Handle other subtables under "Encounters" that aren't nested under "Build an Encounter"
            if subtable in table:
                table = table[subtable]
            else:
                return f"Error: Subtable '{subtable}' not found in category '{category}'."

        # Navigate to the subtable for other categories
        else:
            if subtable not in table:
                return f"Error: Subtable '{subtable}' not found in category '{category}'."
            table = table[subtable]

        # Special handling for "Found in a Curio Shop" under "Mundane Items"
        if category_lower == "mundane items" and subtable.lower() == "found in a curio shop" and curio_subtable:
            if curio_subtable not in table:
                return f"Error: Curio subtable '{curio_subtable}' not found in {category} - {subtable}."
            table = table[curio_subtable]

        if subtable.lower() == "description":
            return f"Description: {table}"

        if category_lower == "better battles":
            roll = random.randint(1, len(table))
            self.better_battles_rolls[subtable] = roll
            entry = table[roll - 1]
            if isinstance(entry, str):
                return f"{subtable}: {entry.split('. ', 1)[1]}"
            elif isinstance(entry, dict):
                event = 'No event description available'
                exclude_keys = {'min', 'max'}
                for key, value in entry.items():
                    if key not in exclude_keys and isinstance(value, str):
                        event = value
                        break
                return f"{subtable}: {event}"
            else:
                return f"Error: Unsupported entry type in {subtable}"

        if category_lower == "convoker griffons":
            if subtable == "Companions":
                return self.roll_griffon_companions()
            elif subtable == "Name":
                return f"Griffon Name: {self.roll_griffon_name()}"

        if category_lower == "convoker missions":
            if subtable == "Missions":
                return self.roll_convoker_missions()

        # Special handling for "Nations and Factions"
        if category_lower == "nations and factions":
            if subtable.lower() == "be a better faction master":
                motivations = table["Motivations"]
                backgrounds = table["Backgrounds"]
                leaders = table["Leaders"]
                sigils = table["Sigils"]
                
                # Roll independently for each category (d20 since there are 20 entries)
                motivation_roll = random.randint(1, len(motivations))
                background_roll = random.randint(1, len(backgrounds))
                leader_roll = random.randint(1, len(leaders))
                sigil_roll = random.randint(1, len(sigils))
                
                # Get the entries
                motivation = motivations[motivation_roll - 1]
                background = backgrounds[background_roll - 1]
                leader = leaders[leader_roll - 1]
                sigil = sigils[sigil_roll - 1]
                
                # Combine the results and append the description
                description = ("\n\nBe a Better Faction Master\n\n"
                               "Roll a d20 once to find a cohesive faction, or roll it four times to create an intriguing combination of aspects.")
                return (f"Motivation: {motivation} (Roll {motivation_roll})\n"
                        f"Background: {background} (Roll {background_roll})\n"
                        f"Leader: {leader} (Roll {leader_roll})\n"
                        f"Sigil: {sigil} (Roll {sigil_roll})"
                        f"{description}")
            
            elif subtable.lower() == "faction name generator":
                # List of themes (subtables)
                themes = list(table.keys())
                theme_roll = random.randint(1, len(themes))
                selected_theme = themes[theme_roll - 1]
                
                # Get the prefixes and suffixes for the selected theme
                theme_table = table[selected_theme]
                prefixes = theme_table["Prefixes"]
                suffixes = theme_table["Suffixes"]
                
                # Roll for prefix and suffix (d6 since there are 6 entries)
                prefix_roll = random.randint(1, len(prefixes))
                suffix_roll = random.randint(1, len(suffixes))
                
                # Get the entries
                prefix = prefixes[prefix_roll - 1]
                suffix = suffixes[suffix_roll - 1]
                
                # Combine into a faction name
                faction_name = f"{prefix} {suffix}"
                return (f"Theme: {selected_theme} (Roll {theme_roll})\n"
                        f"Faction Name: {faction_name}\n"
                        f"Prefix: {prefix} (Roll {prefix_roll})\n"
                        f"Suffix: {suffix} (Roll {suffix_roll})")

        # Handle "Magical Items (Birthright 2e)" and "Mundane Items" subtables
        if category_lower in ["magical items (birthright 2e)", "mundane items"]:
            # Check if the table is a list of strings (e.g., "Book Subjects", "Things found in Pockets (Generic)")
            if isinstance(table, list) and table and isinstance(table[0], str):
                table_length = len(table)
                dice_label = "1d100" if table_length == 100 else "1d20" if table_length in [20, 6] else f"1d{table_length}"
                roll = random.randint(1, table_length)
                return f"{dice_label}: {roll} - {table[roll - 1]}"
            # Check if the table is a list of dictionaries with 'name' and 'description'
            elif isinstance(table, list) and table and isinstance(table[0], dict) and 'name' in table[0] and 'description' in table[0]:
                table_length = len(table)
                dice_label = "1d100" if table_length == 100 else "1d20" if table_length in [20, 6] else f"1d{table_length}"
                roll = random.randint(1, table_length)
                entry = table[roll - 1]
                additional_info = ""
                if "color_options" in entry and "animal_options" in entry:
                    color = self.roll_subtable(entry, "color_options")
                    animal = self.roll_subtable(entry, "animal_options")
                    if color and animal:
                        if color == "Animal’s Natural":
                            additional_info = f"\nColor: {animal}'s Natural Color ({animal})"
                        else:
                            additional_info = f"\nColor: {color} {animal}"
                if "spiders" in entry:
                    spider = self.roll_subtable(entry, "spiders")
                    if spider:
                        additional_info = f"\nSpider: {spider['type']} (Ability: {spider['ability']})"
                return {
                    "roll": roll,
                    "entry": entry,
                    "dice_label": dice_label,
                    "additional_info": additional_info
                }
            else:
                return f"Error: Expected a list of strings or dictionaries with 'name' and 'description' in {category} - {subtable}"

        if isinstance(table, list) and table and isinstance(table[0], dict) and 'min' in table[0] and 'max' in table[0]:
            max_roll = max(entry['max'] for entry in table)
            roll = random.randint(1, max_roll)
            for entry in table:
                if entry['min'] <= roll <= entry['max']:
                    if category_lower == "background" and subtable == "Siblings":
                        return f"Roll {roll}: {self.process_siblings(entry['value'])}"
                    result = entry.get('description', entry.get('value', entry.get('mission', entry.get('text', entry.get('result', entry.get('gender', entry.get('task', entry.get('objective', entry.get('mission_description', entry.get('quest', entry.get('assignment', 'No description available')))))))))))
                    if result == 'No description available':
                        print(f"Debug: Entry structure for {category} - {subtable} (roll {roll}): {entry}")
                    return f"Roll {roll}: {result}"
            return "Error: No matching roll range found."

        if isinstance(table, list) and table and isinstance(table[0], str):
            roll = random.randint(1, len(table))
            return table[roll - 1]

        if isinstance(table, dict):
            return "Error: Nested dictionary structure not fully supported for rolling."

        return "Error: Unsupported subtable structure."

    def roll_subtable(self, entry, subtable_key):
        if subtable_key in entry:
            subtable = entry[subtable_key]
            roll = random.randint(0, len(subtable) - 1)
            return subtable[roll]
        return None

    def roll_color_and_animal(self, entry):
        color = self.roll_subtable(entry, "color_options")
        animal = self.roll_subtable(entry, "animal_options")
        if color and animal:
            return {"color": color, "animal": animal}
        return None

class TTRPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TTRPG Table Roller")
        self.table_manager = None
        try:
            self.table_manager = TableManager("tables.json")
        except Exception as e:
            print(f"Error starting application: {e}")
            self.root.destroy()
            return
        self.last_roll_result = None
        self.create_widgets()

    def create_widgets(self):
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")
        title_label = tk.Label(self.root, text="TTRPG Table Roller", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        # Category dropdown
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(frame, text="Category:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        categories = list(self.table_manager.tables.keys())
        self.category_dropdown = ttk.Combobox(frame, textvariable=self.category_var, values=categories, state="readonly")
        self.category_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.update_subtables)

        # Subtable dropdown (for all categories)
        self.frame2 = tk.Frame(self.root, bg="#f0f0f0")
        self.frame2.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(self.frame2, text="Subtable:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.subtable_var = tk.StringVar()
        self.subtable_dropdown = ttk.Combobox(self.frame2, textvariable=self.subtable_var, state="readonly")
        self.subtable_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.subtable_dropdown.bind("<<ComboboxSelected>>", self.update_curio_subtables)

        # Curio subtable dropdown (for "Found in a Curio Shop" under "Mundane Items")
        self.frame3 = tk.Frame(self.root, bg="#f0f0f0")
        self.frame3.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(self.frame3, text="Curio Section:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.curio_subtable_var = tk.StringVar()
        self.curio_subtable_dropdown = ttk.Combobox(self.frame3, textvariable=self.curio_subtable_var, state="readonly")
        self.curio_subtable_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.frame3.pack_forget()  # Hide by default

        # Buttons
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        roll_button = tk.Button(button_frame, text="Roll", command=self.roll_table, bg="#4CAF50", fg="white", font=("Arial", 12))
        roll_button.pack(side=tk.LEFT, padx=5)
        show_table_button = tk.Button(button_frame, text="Show Table", command=self.show_table, bg="#2196F3", fg="white", font=("Arial", 12))
        show_table_button.pack(side=tk.LEFT, padx=5)
        self.subtable_button = tk.Button(button_frame, text="Roll on Subtable", command=self.roll_subtable, bg="#FF9800", fg="white", font=("Arial", 12))
        self.subtable_button.pack(side=tk.LEFT, padx=5)
        self.subtable_button.pack_forget()

        # Result frame
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(self.result_frame, height=10, width=60, wrap=tk.WORD, font=("Arial", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)

        # Footer
        footer_frame = tk.Frame(self.root, bg="#f0f0f0")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        github_label = tk.Label(footer_frame, text="GitHub", fg="blue", cursor="hand2", bg="#f0f0f0")
        github_label.pack(side=tk.RIGHT, padx=5)
        github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/"))

        # Set a default category and update subtables
        if categories:
            self.category_var.set(categories[0])
            self.update_subtables()

    def update_subtables(self, event=None):
        category = self.category_var.get()
        if category:
            subtables = []
            if category.lower() == "encounters":
                # Special handling for "Encounters" to map nested subtables
                for key in self.table_manager.tables[category].keys():
                    if key == "Build an Encounter":
                        subtables.extend(["Build an Encounter - Locations", "Build an Encounter - Threats"])
                    else:
                        subtables.append(key)
            else:
                subtables = list(self.table_manager.tables[category].keys())
            
            if category.lower() == "background":
                subtables = [subtable for subtable in subtables if subtable != "Note"]
            
            self.subtable_dropdown.config(values=subtables)
            if subtables:
                self.subtable_var.set(subtables[0])
            else:
                self.subtable_var.set("")
            # Update the curio subtables based on the selected subtable
            self.update_curio_subtables()
        else:
            self.subtable_var.set("")
            self.subtable_dropdown.config(values=[])
            self.curio_subtable_var.set("")
            self.curio_subtable_dropdown.config(values=[])
        self.subtable_button.pack_forget()

    def update_curio_subtables(self, event=None):
        category = self.category_var.get()
        subtable = self.subtable_var.get()
        if category and subtable:
            if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop":
                self.frame3.pack(pady=5, padx=10, fill=tk.X)  # Show the curio subtable dropdown
                curio_subtables = list(self.table_manager.tables[category][subtable].keys())
                self.curio_subtable_dropdown.config(values=curio_subtables)
                if curio_subtables:
                    self.curio_subtable_var.set(curio_subtables[0])
                else:
                    self.curio_subtable_var.set("")
            else:
                self.frame3.pack_forget()  # Hide the curio subtable dropdown
        else:
            self.frame3.pack_forget()

    def roll_table(self):
        category = self.category_var.get()
        subtable = self.subtable_var.get()
        curio_subtable = self.curio_subtable_var.get() if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop" else None

        if not category:
            self.display_result("Please select a category.")
            return
        if not subtable:
            self.display_result("Please select a subtable.")
            return
        if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop" and not curio_subtable:
            self.display_result("Please select a curio section.")
            return

        try:
            result = self.table_manager.roll(category, subtable, curio_subtable)
            if isinstance(result, dict):
                self.last_roll_result = result
                roll = result["roll"]
                entry = result["entry"]
                dice_label = result.get("dice_label", "Roll")
                additional_info = result.get("additional_info", "")
                display_text = f"{dice_label}: {roll} - {entry['name']}\nDescription: {entry['description']}{additional_info}"
                self.display_result(display_text)
                if any(key in entry for key in ['gems', 'color_options', 'animal_options', 'spiders']):
                    self.subtable_button.pack(side=tk.LEFT, padx=5)
                else:
                    self.subtable_button.pack_forget()
            else:
                self.last_roll_result = None
                self.subtable_button.pack_forget()
                self.display_result(result)
        except Exception as e:
            self.display_result(f"Error: {e}")

    def roll_subtable(self):
        if not self.last_roll_result:
            self.display_result("Please roll an item first.")
            return
        entry = self.last_roll_result["entry"]
        if 'color_options' in entry and 'animal_options' in entry:
            result = self.table_manager.roll_color_and_animal(entry)
            if result:
                color = result['color']
                animal = result['animal']
                if color == "Animal’s Natural":
                    self.display_result(f"Color: {animal}'s Natural Color ({animal})")
                else:
                    self.display_result(f"Color: {color} {animal}")
            return
        if 'gems' in entry:
            result = self.table_manager.roll_subtable(entry, 'gems')
            if result:
                self.display_result(f"Gem: {result['name']} (Effect: {result['effect']})")
            return
        if 'spiders' in entry:
            result = self.table_manager.roll_subtable(entry, 'spiders')
            if result:
                self.display_result(f"Spider: {result['type']} (Ability: {result['ability']})")
            return
        self.display_result("No subtable found to roll on.")

    def show_table(self):
        category = self.category_var.get()
        subtable = self.subtable_var.get()
        curio_subtable = self.curio_subtable_var.get() if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop" else None

        if not category:
            self.display_result("Please select a category.")
            return
        if not subtable:
            self.display_result("Please select a subtable.")
            return
        if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop" and not curio_subtable:
            self.display_result("Please select a curio section.")
            return

        # Navigate to the correct table
        if category.lower() == "encounters":
            if subtable.lower() == "build an encounter - locations":
                table = self.table_manager.tables[category]["Build an Encounter"]["Locations"]
            elif subtable.lower() == "build an encounter - threats":
                table = self.table_manager.tables[category]["Build an Encounter"]["Threats"]
            else:
                if subtable not in self.table_manager.tables[category]:
                    self.display_result(f"Error: Subtable '{subtable}' not found in category '{category}'.")
                    return
                table = self.table_manager.tables[category][subtable]
        else:
            if subtable not in self.table_manager.tables[category]:
                self.display_result(f"Error: Subtable '{subtable}' not found in category '{category}'.")
                return
            table = self.table_manager.tables[category][subtable]

        if curio_subtable:
            if curio_subtable not in table:
                self.display_result(f"Error: Curio subtable '{curio_subtable}' not found in {category} - {subtable}.")
                return
            table = table[curio_subtable]

        result = f"{category} - {subtable}"
        if curio_subtable:
            result += f" - {curio_subtable}"
        result += ":\n\n"

        # Handle the display based on the table structure
        if isinstance(table, list):
            if isinstance(table[0], dict) and 'min' in table[0] and 'max' in table[0]:
                for entry in table:
                    if category.lower() == "convoker missions" and subtable == "Missions":
                        antagonist = entry.get('antagonist', 'Unknown antagonist')
                        trouble = entry.get('trouble', 'Unknown trouble')
                        location = entry.get('location', 'Unknown location')
                        obstacle = entry.get('obstacle', 'No obstacle')
                        result += (f"Rolls {entry['min']} to {entry['max']}:\n"
                                   f"Antagonist: {antagonist}\n"
                                   f"Trouble: {trouble}\n"
                                   f"Location: {location}\n"
                                   f"Obstacle: {obstacle}\n\n")
                    else:
                        result += f"Rolls {entry['min']} to {entry['max']}: {entry.get('description', entry.get('value', entry.get('mission', entry.get('text', entry.get('result', entry.get('gender', entry.get('task', entry.get('objective', entry.get('mission_description', entry.get('quest', entry.get('assignment', 'No description available')))))))))))}\n"
            elif category.lower() in ["magical items (birthright 2e)", "mundane items"]:
                if isinstance(table[0], str):  # Handle lists of strings
                    for i, item in enumerate(table, 1):
                        result += f"{i}. {item}\n"
                elif isinstance(table[0], dict) and 'name' in table[0] and 'description' in table[0]:
                    for i, entry in enumerate(table, 1):
                        result += f"{i}. {entry['name']}\n"
                        result += f"   Description: {entry['description']}\n"
                        if 'gems' in entry:
                            result += "   Gems:\n"
                            result += "     Name            | Effect\n"
                            result += "     ----------------|--------------------\n"
                            for gem in entry['gems']:
                                result += f"     {gem['name']:<15} | {gem['effect']}\n"
                        if 'color_options' in entry and 'animal_options' in entry:
                            result += "   Colors:\n"
                            result += "     Color\n"
                            result += "     ----------------\n"
                            for color in entry['color_options']:
                                result += f"     {color}\n"
                            result += "\n   Animals:\n"
                            result += "     Animal\n"
                            result += "     ----------------\n"
                            for animal in entry['animal_options']:
                                result += f"     {animal}\n"
                        if 'spiders' in entry:
                            result += "   Spiders:\n"
                            result += "     Type            | Ability\n"
                            result += "     ----------------|--------------------\n"
                            for spider in entry['spiders']:
                                result += f"     {spider['type']:<15} | {spider['ability']}\n"
                        result += "\n"
                else:
                    result += f"Invalid entry structure in {category} - {subtable}\n"
            else:
                for i, item in enumerate(table, 1):
                    if isinstance(item, str):
                        result += f"{item}\n"
                    elif isinstance(item, dict):
                        event = 'No event description available'
                        exclude_keys = {'min', 'max'}
                        for key, value in item.items():
                            if key not in exclude_keys and isinstance(value, str):
                                event = value
                                break
                        result += f"{event}\n"
                    else:
                        result += f"Unsupported entry type: {item}\n"
        elif isinstance(table, dict):
            # Handle specific dictionary structures
            if category.lower() == "convoker griffons" and subtable == "Name":
                result += "Prefixes:\n" + "\n".join(table["Prefixes"]) + "\n\n"
                result += "Suffixes:\n" + "\n".join(table["Suffixes"]) + "\n"
            elif category.lower() == "nations and factions":
                if subtable.lower() == "be a better faction master":
                    result += "Motivations:\n"
                    for i, item in enumerate(table["Motivations"], 1):
                        result += f"{i}. {item}\n"
                    result += "\nBackgrounds:\n"
                    for i, item in enumerate(table["Backgrounds"], 1):
                        result += f"{i}. {item}\n"
                    result += "\nLeaders:\n"
                    for i, item in enumerate(table["Leaders"], 1):
                        result += f"{i}. {item}\n"
                    result += "\nSigils:\n"
                    for i, item in enumerate(table["Sigils"], 1):
                        result += f"{i}. {item}\n"
                elif subtable.lower() == "faction name generator":
                    for theme, theme_table in table.items():
                        result += f"\n{theme}:\n"
                        result += "Prefixes:\n"
                        for i, prefix in enumerate(theme_table["Prefixes"], 1):
                            result += f"{i}. {prefix}\n"
                        result += "\nSuffixes:\n"
                        for i, suffix in enumerate(theme_table["Suffixes"], 1):
                            result += f"{i}. {suffix}\n"
            elif category.lower() == "encounters":
                if subtable.lower() == "build an encounter - locations":
                    # Display Environment
                    result += "Environment:\n"
                    for item in table["Environment"]:
                        result += f"{item}\n"
                    # Display Location Types and their specific locations
                    result += "\nLocation Types:\n"
                    for loc_type in table["Location"]:
                        loc_type_name = loc_type.split(". ", 1)[1]
                        result += f"{loc_type}\n"
                        result += f"  Specific {loc_type_name}:\n"
                        for specific_loc in table[loc_type_name]:
                            result += f"    {specific_loc}\n"
                elif subtable.lower() == "build an encounter - threats":
                    # Display Threat Types
                    result += "Threat Types:\n"
                    for threat in table["Threat"]:
                        result += f"{threat}\n"
                    # Display each threat category
                    for threat_type, items in table.items():
                        if threat_type != "Threat":
                            result += f"\n{threat_type}:\n"
                            for item in items:
                                result += f"{item}\n"
                else:
                    # Generic dictionary display for other Encounters subtables
                    for key, value in table.items():
                        result += f"\n{key}:\n"
                        if isinstance(value, list):
                            for item in value:
                                result += f"{item}\n"
                        else:
                            result += f"{value}\n"
            else:
                # Generic dictionary display for other categories
                for key, value in table.items():
                    result += f"\n{key}:\n"
                    if isinstance(value, list):
                        for item in value:
                            result += f"{item}\n"
                    else:
                        result += f"{value}\n"
        else:
            result += f"{table}\n"

        self.display_result(result)
        self.subtable_button.pack_forget()

    def display_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        for widget in self.result_frame.winfo_children():
            if isinstance(widget, (ttk.Treeview, ttk.Scrollbar)):
                widget.destroy()

        lines = text.split("\n")
        current_text = []
        table_lines = []
        in_table = False

        for line in lines:
            if '|' in line and any(header in line for header in ['SPELL', 'WEATHER/EFFECTS', 'Name', 'Type']):
                in_table = True
                if current_text:
                    current_text.append("")
                table_lines.append(line)
            elif in_table and ('|' in line or line.strip() == ""):
                table_lines.append(line)
            else:
                if in_table:
                    in_table = False
                    if table_lines:
                        self.render_table(table_lines)
                    table_lines = []
                current_text.append(line)

        self.result_text.insert(tk.END, "\n".join(current_text))
        if table_lines:
            self.render_table(table_lines)

        self.result_text.config(state=tk.DISABLED)

    def render_table(self, table_lines):
        tree = ttk.Treeview(self.result_frame, show="headings")
        tree.pack(fill=tk.X, expand=False)

        headers = table_lines[0].split("|")
        headers = [h.strip() for h in headers]
        tree["columns"] = headers
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, width=len(header) * 10, stretch=True)

        for line in table_lines[1:]:
            if line.strip() and not all(c in "-|" for c in line.strip()):
                values = [v.strip() for v in line.split("|")]
                tree.insert("", tk.END, values=values)

        scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscrollcommand=scrollbar.set)
        scrollbar.pack(fill=tk.X)

if __name__ == "__main__":
    root = tk.Tk()
    app = TTRPGApp(root)
    root.mainloop()