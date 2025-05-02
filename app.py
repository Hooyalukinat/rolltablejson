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
                "Magical Items (Birthright 2e)", "Mundane Items", "Encounters",
                "Nations and Factions", "Tavern Drinks", "Biomes", "Monster Lairs"
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

    def roll(self, category, subtable, curio_subtable=None, subsubtable=None):
        category_lower = category.lower()
        try:
            table = self.tables[category]
            if subtable not in table:
                return f"Error: Subtable '{subtable}' not found in category '{category}'."
        except KeyError:
            return f"Error: Category '{category}' not found."

        # Navigate to the correct table
        if category_lower == "build an encounter":
            if subtable.lower() == "locations":
                locations_table = table["Locations"]
                if subsubtable:
                    if subsubtable not in locations_table:
                        return f"Error: Subsubtable '{subsubtable}' not found in {category} - {subtable}."
                    specific_locations = locations_table[subsubtable]
                    roll = random.randint(1, len(specific_locations))
                    selected_specific_loc = specific_locations[roll - 1].split(". ", 1)[1]
                    return f"{subsubtable}: {selected_specific_loc} (Roll {roll})"
                else:
                    environments = locations_table["Environment"]
                    env_roll = random.randint(1, len(environments))
                    selected_env = environments[env_roll - 1].split(". ", 1)[1]
                    
                    locations = locations_table["Location"]
                    loc_roll = random.randint(1, len(locations))
                    selected_loc_type = locations[loc_roll - 1].split(". ", 1)[1]
                    
                    specific_locations = locations_table[selected_loc_type]
                    specific_roll = random.randint(1, len(specific_locations))
                    selected_specific_loc = specific_locations[specific_roll - 1].split(". ", 1)[1]
                    
                    return (f"Environment: {selected_env} (Roll {env_roll})\n"
                            f"Location: {selected_loc_type} - {selected_specific_loc} (Roll {loc_roll}, Roll {specific_roll})")
            
            elif subtable.lower() == "threats":
                threats_table = table["Threats"]
                if subsubtable:
                    if subsubtable not in threats_table:
                        return f"Error: Subsubtable '{subsubtable}' not found in {category} - {subtable}."
                    specific_threats = threats_table[subsubtable]
                    roll = random.randint(1, len(specific_threats))
                    selected_specific_threat = specific_threats[roll - 1].split(". ", 1)[1]
                    return f"{subsubtable}: {selected_specific_threat} (Roll {roll})"
                else:
                    threats = threats_table["Threat"]
                    threat_roll = random.randint(1, len(threats))
                    selected_threat_type = threats[threat_roll - 1].split(". ", 1)[1]
                    
                    threat_type_map = {
                        "A single, mighty foe": "Single Mighty Foes",
                        "A horde of enemies": "Hordes of Enemies",
                        "A rival or enemy faction": "Rival or Enemy Faction",
                        "A natural disaster": "Natural Disasters"
                    }
                    subtable_key = threat_type_map[selected_threat_type]
                    
                    specific_threats = threats_table[subtable_key]
                    specific_roll_max = len(specific_threats)
                    specific_roll = random.randint(1, specific_roll_max)
                    selected_specific_threat = specific_threats[specific_roll - 1].split(". ", 1)[1]
                    
                    return (f"Threat: {selected_threat_type} - {selected_specific_threat} (Roll {threat_roll}, Roll {specific_roll})")
            
            table = table[subtable]

        # Handle "Found in a Curio Shop" under "Mundane Items"
        elif category_lower == "mundane items" and subtable.lower() == "found in a curio shop":
            try:
                curio_subtables = list(table[subtable].keys())
                if not curio_subtables:
                    return f"Error: No curio subtables found in {category} - {subtable}"
                # Randomly select a curio subtable
                selected_curio = random.choice(curio_subtables)
                table = table[subtable][selected_curio]
            except Exception as e:
                print(f"Debug: Error accessing curio subtables in {category} - {subtable}: {str(e)}")
                return f"Error: Failed to select curio subtable: {str(e)}"
        
        # Handle "Biomes" and "Monster Lairs"
        elif category_lower in ["biomes", "monster lairs"]:
            if subsubtable:
                try:
                    table = table[subtable][subsubtable]
                except KeyError:
                    return f"Error: Subsubtable '{subsubtable}' not found in {category} - {subtable}."
            else:
                return f"Error: Please select a subsubtable for {category} - {subtable}."
        else:
            table = table[subtable]

        # Handle description subtables
        if subtable.lower() == "description":
            return f"Description: {str(table)}"

        # Handle "Better Battles"
        if category_lower == "better battles":
            try:
                if not table or not isinstance(table, list):
                    print(f"Debug: Invalid table in {category} - {subtable}: {table}")
                    return f"Error: Invalid table structure in {subtable}"
                roll = random.randint(1, len(table)) if len(table) > 0 else 1
                self.better_battles_rolls[subtable] = roll
                entry = table[roll - 1]
                if isinstance(entry, str):
                    return f"{subtable}: {entry.split('. ', 1)[1] if '. ' in entry else entry}"
                elif isinstance(entry, dict):
                    event = entry.get('description', entry.get('value', 'No event description available'))
                    return f"{subtable}: {event}"
                else:
                    print(f"Debug: Unexpected entry type in {category} - {subtable}: {entry}")
                    return f"Error: Unsupported entry type in {subtable}"
            except Exception as e:
                print(f"Debug: Error in {category} - {subtable}: {str(e)}, Table: {table[:2]}")
                return f"Error: Failed to roll on {subtable}: {str(e)}"

        # Handle "Convoker Griffons"
        if category_lower == "convoker griffons":
            if subtable == "Companions":
                return self.roll_griffon_companions()
            elif subtable == "Name":
                return f"Griffon Name: {self.roll_griffon_name()}"

        # Handle "Convoker Missions"
        if category_lower == "convoker missions":
            if subtable == "Missions":
                return self.roll_convoker_missions()

        # Handle "Nations and Factions"
        if category_lower == "nations and factions":
            if subtable.lower() == "be a better faction master":
                try:
                    result = []
                    for key in ["Motivations", "Backgrounds", "Leaders", "Sigils"]:
                        items = table.get(key, [])
                        if isinstance(items, list) and items:
                            roll = random.randint(1, len(items))
                            result.append(f"{key}: {items[roll - 1]} (Roll {roll})")
                        else:
                            result.append(f"{key}: No valid entries")
                    description = ("\n\nBe a Better Faction Master\n\n"
                                   "Roll a d20 once to find a cohesive faction, or roll it four times to create an intriguing combination of aspects.")
                    return "\n".join(result) + description
                except Exception as e:
                    print(f"Debug: Error in {category} - {subtable}: {str(e)}, Table: {table}")
                    return f"Error: Failed to roll on {subtable}: {str(e)}"
            
            elif subtable.lower() == "faction name generator":
                try:
                    themes = [k for k in table.keys() if isinstance(table[k], dict) and "Prefixes" in table[k] and "Suffixes" in table[k]]
                    if not themes:
                        print(f"Debug: No valid themes in {category} - {subtable}: {list(table.keys())}")
                        return f"Error: No valid themes found in {subtable}"
                    theme_roll = random.randint(1, len(themes))
                    selected_theme = themes[theme_roll - 1]
                    theme_table = table[selected_theme]
                    prefixes = theme_table["Prefixes"]
                    suffixes = theme_table["Suffixes"]
                    prefix_roll = random.randint(1, len(prefixes))
                    suffix_roll = random.randint(1, len(suffixes))
                    prefix = prefixes[prefix_roll - 1]
                    suffix = suffixes[suffix_roll - 1]
                    faction_name = f"{prefix} {suffix}"
                    return (f"Theme: {selected_theme} (Roll {theme_roll})\n"
                            f"Faction Name: {faction_name}\n"
                            f"Prefix: {prefix} (Roll {prefix_roll})\n"
                            f"Suffix: {suffix} (Roll {suffix_roll})")
                except Exception as e:
                    print(f"Debug: Error in {category} - {subtable}: {str(e)}, Table: {table}")
                    return f"Error: Failed to roll on {subtable}: {str(e)}"

        # Handle "Tavern Drinks"
        if category_lower == "tavern drinks":
            try:
                if not table or not isinstance(table, list):
                    print(f"Debug: Invalid table in {category} - {subtable}: {table}")
                    return f"Error: Invalid table structure in {subtable}"
                roll = random.randint(1, len(table))
                entry = table[roll - 1]
                if isinstance(entry, dict) and all(key in entry for key in ['name', 'color', 'description', 'effect', 'cost']):
                    return (f"Roll {roll}: {entry['name']}\n"
                            f"Color: {entry['color']}\n"
                            f"Description: {entry['description']}\n"
                            f"Effect: {entry['effect']}\n"
                            f"Cost: {entry['cost']}")
                else:
                    print(f"Debug: Unexpected entry type in {category} - {subtable}: {entry}")
                    return f"Error: Unsupported entry type in {subtable}"
            except Exception as e:
                print(f"Debug: Error in {category} - {subtable}: {str(e)}, Table: {table}")
                return f"Error: Failed to roll on {subtable}: {str(e)}"

        # Generic rolling for other categories (including "Biomes" and "Monster Lairs" subtables)
        try:
            if isinstance(table, list) and table:
                if isinstance(table[0], str):
                    roll = random.randint(1, len(table))
                    return f"Roll {roll}: {table[roll - 1]}"
                elif isinstance(table[0], dict):
                    if 'min' in table[0] and 'max' in table[0]:
                        max_roll = max(entry['max'] for entry in table)
                        roll = random.randint(1, max_roll)
                        for entry in table:
                            if entry['min'] <= roll <= entry['max']:
                                if category_lower == "background" and subtable == "Siblings":
                                    return f"Roll {roll}: {self.process_siblings(entry['value'])}"
                                result = entry.get('description', entry.get('value', entry.get('name', entry.get('result', 'No description available'))))
                                return f"Roll {roll}: {result}"
                    elif all(key in table[0] for key in ['name', 'description']):
                        roll = random.randint(1, len(table))
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
                            "dice_label": f"1d{len(table)}",
                            "additional_info": additional_info
                        }
                    else:
                        roll = random.randint(1, len(table))
                        entry = table[roll - 1]
                        # Try to extract a displayable value
                        for key in ['name', 'description', 'value', 'result', 'text']:
                            if key in entry:
                                return f"Roll {roll}: {entry[key]}"
                        print(f"Debug: No displayable key in {category} - {subtable} entry: {entry}")
                        return f"Error: No displayable data in {subtable} entry"
                else:
                    print(f"Debug: Unexpected list entry type in {category} - {subtable}: {table[0]}")
                    return f"Error: Unsupported list entry type in {subtable}"
            elif isinstance(table, dict):
                # Try to find a rollable list within the dictionary
                for key, value in table.items():
                    if isinstance(value, list) and value and isinstance(value[0], str):
                        roll = random.randint(1, len(value))
                        return f"{key}: {value[roll - 1]} (Roll {roll})"
                print(f"Debug: Dictionary structure in {category} - {subtable}: {list(table.keys())}")
                return f"Error: No rollable list found in {subtable}"
            else:
                print(f"Debug: Invalid table structure in {category} - {subtable}: {table}")
                return f"Error: Invalid table structure in {subtable}"
        except Exception as e:
            print(f"Debug: Error in {category} - {subtable}: {str(e)}, Table: {table}")
            return f"Error: Failed to roll on {subtable}: {str(e)}"

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

        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(frame, text="Category:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        categories = list(self.table_manager.tables.keys())
        self.category_dropdown = ttk.Combobox(frame, textvariable=self.category_var, values=categories, state="readonly")
        self.category_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.category_dropdown.bind("<<ComboboxSelected>>", self.update_subtables)

        self.frame2 = tk.Frame(self.root, bg="#f0f0f0")
        self.frame2.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(self.frame2, text="Subtable:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.subtable_var = tk.StringVar()
        self.subtable_dropdown = ttk.Combobox(self.frame2, textvariable=self.subtable_var, state="readonly")
        self.subtable_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.subtable_dropdown.bind("<<ComboboxSelected>>", self.update_subsubtables)

        self.frame4 = tk.Frame(self.root, bg="#f0f0f0")
        self.frame4.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(self.frame4, text="Subsection:", bg="#f0f0f0").pack(side=tk.LEFT)
        self.subsubtable_var = tk.StringVar()
        self.subsubtable_dropdown = ttk.Combobox(self.frame4, textvariable=self.subsubtable_var, state="readonly")
        self.subsubtable_dropdown.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.frame4.pack_forget()

        # Removed curio dropdown (frame3) since we're auto-selecting for "Found in a Curio Shop"

        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=10)
        roll_button = tk.Button(button_frame, text="Roll", command=self.roll_table, bg="#4CAF50", fg="white", font=("Arial", 12))
        roll_button.pack(side=tk.LEFT, padx=5)
        show_table_button = tk.Button(button_frame, text="Show Table", command=self.show_table, bg="#2196F3", fg="white", font=("Arial", 12))
        show_table_button.pack(side=tk.LEFT, padx=5)
        self.subtable_button = tk.Button(button_frame, text="Roll on Subtable", command=self.roll_subtable, bg="#FF9800", fg="white", font=("Arial", 12))
        self.subtable_button.pack(side=tk.LEFT, padx=5)
        self.subtable_button.pack_forget()

        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.result_text = tk.Text(self.result_frame, height=10, width=60, wrap=tk.WORD, font=("Arial", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        self.result_text.config(state=tk.DISABLED)

        footer_frame = tk.Frame(self.root, bg="#f0f0f0")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)
        github_label = tk.Label(footer_frame, text="GitHub", fg="blue", cursor="hand2", bg="#f0f0f0")
        github_label.pack(side=tk.RIGHT, padx=5)
        github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/"))

        if categories:
            self.category_var.set(categories[0])
            self.update_subtables()

    def get_subsubtables(self, category, subtable):
        subtables = []
        
        def process_node(node, parent_key=''):
            if isinstance(node, list) and all(isinstance(item, str) for item in node):
                subtables.append(parent_key)
            elif isinstance(node, dict):
                for key, value in node.items():
                    process_node(value, key)
        
        try:
            data = self.table_manager.tables.get(category, {}).get(subtable, {})
            process_node(data)
        except Exception as e:
            print(f"Error in get_subsubtables: {e}")
        return subtables

    def update_subtables(self, event=None):
        category = self.category_var.get()
        if category:
            try:
                subtables = list(self.table_manager.tables[category].keys())
                if category.lower() == "background":
                    subtables = [s for s in subtables if s != "Note"]
                self.subtable_dropdown.config(values=subtables)
                if subtables:
                    self.subtable_var.set(subtables[0])
                else:
                    self.subtable_var.set("")
                self.update_subsubtables()
            except Exception as e:
                print(f"Error in update_subtables: {e}")
                self.subtable_var.set("")
                self.subtable_dropdown.config(values=[])
        else:
            self.subtable_var.set("")
            self.subtable_dropdown.config(values=[])
            self.subsubtable_var.set("")
            self.subsubtable_dropdown.config(values=[])

    def update_subsubtables(self, event=None):
        category = self.category_var.get()
        subtable = self.subtable_var.get()
        self.subsubtable_var.set("")
        self.frame4.pack_forget()
        
        if category and subtable:
            if category.lower() == "build an encounter" and subtable.lower() in ["locations", "threats"]:
                try:
                    subsubtables = self.get_subsubtables(category, subtable)
                    self.subsubtable_dropdown.config(values=subsubtables)
                    if subsubtables:
                        self.frame4.pack(pady=5, padx=10, fill=tk.X)
                        self.subsubtable_var.set(subsubtables[0])
                except Exception as e:
                    print(f"Error in update_subsubtables: {e}")
            elif category.lower() in ["biomes", "monster lairs"]:
                try:
                    # Check if the subtable (e.g., "Primal Forest" or "Troll Cave") contains further subtables
                    subtable_data = self.table_manager.tables.get(category, {}).get(subtable, {})
                    if isinstance(subtable_data, dict):
                        subsubtables = list(subtable_data.keys())
                        self.subsubtable_dropdown.config(values=subsubtables)
                        if subsubtables:
                            self.frame4.pack(pady=5, padx=10, fill=tk.X)
                            self.subsubtable_var.set(subsubtables[0])
                except Exception as e:
                    print(f"Error in update_subsubtables for {category}: {e}")

    def roll_table(self):
        category = self.category_var.get()
        subtable = self.subtable_var.get()
        subsubtable = self.subsubtable_var.get() if category.lower() in ["build an encounter", "biomes", "monster lairs"] else None

        if not category:
            self.display_result("Please select a category.")
            return
        if not subtable:
            self.display_result("Please select a subtable.")
            return
        if category.lower() in ["biomes", "monster lairs"] and not subsubtable:
            self.display_result("Please select a subsection.")
            return

        try:
            result = self.table_manager.roll(category, subtable, None, subsubtable)
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
        subsubtable = self.subsubtable_var.get() if category.lower() in ["build an encounter", "biomes", "monster lairs"] else None

        if not category:
            self.display_result("Please select a category.")
            return
        if not subtable:
            self.display_result("Please select a subtable.")
            return
        if category.lower() in ["biomes", "monster lairs"] and not subsubtable:
            self.display_result("Please select a subsection.")
            return

        try:
            if category.lower() in ["biomes", "monster lairs"] and subsubtable:
                table = self.table_manager.tables[category][subtable][subsubtable]
            else:
                table = self.table_manager.tables[category][subtable]
                # For "Found in a Curio Shop", randomly select a subtable to display
                if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop":
                    curio_subtables = list(table.keys())
                    if curio_subtables:
                        table = table[random.choice(curio_subtables)]
        except KeyError as e:
            self.display_result(f"Error: {str(e)} not found")
            return

        result = f"{category} - {subtable}"
        if category.lower() == "mundane items" and subtable.lower() == "found in a curio shop":
            result += f" - {random.choice(curio_subtables) if curio_subtables else 'Unknown Section'}"
        if subsubtable:
            result += f" - {subsubtable}"
        result += ":\n\n"

        try:
            if isinstance(table, list):
                if isinstance(table[0], str):
                    for i, item in enumerate(table, 1):
                        result += f"{i}. {item}\n"
                elif isinstance(table[0], dict):
                    if 'min' in table[0] and 'max' in table[0]:
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
                                result += f"Rolls {entry['min']} to {entry['max']}: {entry.get('description', entry.get('value', entry.get('name', 'No description')))}\n"
                    elif category.lower() == "tavern drinks":
                        result += "Roll | Drink Name          | Color               | Description / Effect / Cost\n"
                        result += "-----|---------------------|---------------------|----------------------------\n"
                        for i, entry in enumerate(table, 1):
                            name = entry.get('name', 'Unknown')
                            color = entry.get('color', 'Unknown')
                            desc = entry.get('description', 'No description')
                            effect = entry.get('effect', 'No effect')
                            cost = entry.get('cost', 'Unknown')
                            result += f"{i:<4} | {name:<19} | {color:<19} | Description: {desc}\n"
                            result += f"     |                     |                     | Effect: {effect}\n"
                            result += f"     |                     |                     | Cost: {cost}\n\n"
                    else:
                        for i, entry in enumerate(table, 1):
                            name = entry.get('name', 'No name')
                            desc = entry.get('description', 'No description')
                            result += f"{i}. {name}\n   Description: {desc}\n"
                            for key in ['gems', 'color_options', 'animal_options', 'spiders']:
                                if key in entry:
                                    result += f"   {key.capitalize()}:\n"
                                    if key == 'gems':
                                        result += "     Name            | Effect\n"
                                        result += "     ----------------|--------------------\n"
                                        for item in entry[key]:
                                            result += f"     {item.get('name', 'Unknown'):<15} | {item.get('effect', 'None')}\n"
                                    elif key == 'spiders':
                                        result += "     Type            | Ability\n"
                                        result += "     ----------------|--------------------\n"
                                        for item in entry[key]:
                                            result += f"     {item.get('type', 'Unknown'):<15} | {item.get('ability', 'None')}\n"
                                    else:
                                        for item in entry[key]:
                                            result += f"     {item}\n"
                            result += "\n"
                else:
                    result += f"Invalid entry structure: {table[0]}\n"
            elif isinstance(table, dict):
                for key, value in table.items():
                    result += f"\n{key}:\n"
                    if isinstance(value, list):
                        for i, item in enumerate(value, 1):
                            if isinstance(item, str):
                                result += f"{i}. {item}\n"
                            elif isinstance(item, dict):
                                result += f"{i}. {item.get('name', item.get('value', 'No name'))}\n"
                            else:
                                result += f"{i}. {str(item)}\n"
                    else:
                        result += f"{str(value)}\n"
            else:
                result += f"{str(table)}\n"
        except Exception as e:
            result += f"Error displaying table: {str(e)}\n"
            print(f"Debug: Error in show_table {category} - {subtable}: {str(e)}, Table: {table}")

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
            if '|' in line and any(header in line for header in ['SPELL', 'WEATHER/EFFECTS', 'Name', 'Type', 'Roll']):
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
        try:
            tree = ttk.Treeview(self.result_frame, show="headings")
            tree.pack(fill=tk.X, expand=False)

            headers = table_lines[0].split("|")
            headers = [h.strip() for h in headers if h.strip()]
            tree["columns"] = headers
            for header in headers:
                tree.heading(header, text=header)
                tree.column(header, width=len(header) * 10, stretch=True)

            for line in table_lines[1:]:
                if line.strip() and not all(c in "-|" for c in line.strip()):
                    values = [v.strip() for v in line.split("|") if v.strip()]
                    if len(values) == len(headers):
                        tree.insert("", tk.END, values=values)

            scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(xscrollcommand=scrollbar.set)
            scrollbar.pack(fill=tk.X)
        except Exception as e:
            print(f"Error rendering table: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TTRPGApp(root)
    root.mainloop()
