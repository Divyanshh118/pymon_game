"""
Pymon game
@author: Divyansh Singh

This Pymon game implements a Pokémon-inspired battle system using an object-oriented design. Key features include: 
(1) location-based movement with energy constraints using an interconnected node structure, 
(2) a rock-paper-scissors battle system with statistical tracking, 
(3) inventory management with consumable and non-consumable items, and 
(4) Data loading CSV-based for easy content editing. The implementation uses custom exceptions for error handling and uses 
dictionary-based storage for efficient data access. 
The game maintains balance through an energy system, random item/creature distribution, and a Pymon backup mechanism. 
A modular design with a clear separation of game logic (Operation) and data management (Record) 
enables easy expansion of functions. 
The main issues being addressed include implementing persistent data storage via CSV, balancing game mechanics, 
and keeping code organized with proper class hierarchy.

"""
import sys
import datetime
import random



# Custom exception for handling invalid movement directions.
class InvalidDirectionException(Exception):

    def __init__(self, direction):
        
        self.direction = direction
        self.message = f"Error: Direction - {direction} does not contain any location"
        super().__init__(self.message)

# Custom exception for handling invalid CSV file formats.
class InvalidInputFileFormat(Exception):

    def __init__(self, filename):

        self.filename = filename
        self.message = f"Error: {filename} Csv file has invalid content or in incorrect format."
        super().__init__(self.message)

# Tracks and manages battle statistics for Pymons.
class BattleStats:
    def __init__(self):

        # Dictionary to store battle history for each Pymon
        self.battles = {} 


    # Records new battle outcome for a Pymon.  
    def add_battle(self, pymon_name, opponent, wins, draws, losses):

        if pymon_name not in self.battles:
            self.battles[pymon_name] = []
            
        battle_time = datetime.datetime.now()
        battle = {
            'timestamp': battle_time,
            'opponent': opponent,
            'wins': wins,
            'draws': draws,
            'losses': losses
        }
        self.battles[pymon_name].append(battle)

    # Generate battle stats for each Pymon.  
    def stats_generate(self):

        for pymon_name, battles in self.battles.items():

            print(f"\nPymon Nickname: \"{pymon_name}\"")
            total_wins = 0
            total_draws = 0
            total_losses = 0
            
            for battle in battles:
                print(f"Battle {len(battles)}, {battle['timestamp'].strftime('%d/%m/%Y %I:%M%p')} "
                      f"Opponent: \"{battle['opponent']}\", W: {battle['wins']} "
                      f"D: {battle['draws']} L: {battle['losses']}")
                      
                total_wins += battle['wins']
                total_draws += battle['draws']
                total_losses += battle['losses']
                
            print(f"Total: W: {total_wins} D: {total_draws} L: {total_losses}")


# Represents a location in the game world.
class Location:

    # Initialize a new location.
    def __init__(self, name = "New room", description = "", w = None, n = None , e = None, s = None):
        self.name = name
        self.description = description
        self.doors = {}
        self.doors["west"] = w
        self.doors["north"] = n
        self.doors["east"] = e
        self.doors["south"] = s
        self.creatures = [] # List of creatures in this location
        self.items = []  # List of items in this location

    # Adds a creature to the location
    def add_creature(self, creature):
        self.creatures.append(creature)
        
        
    # Adds a item to the location    
    def add_item(self, item):
        self.items.append(item)
        
    # Connects the location to another location    
    def connect(self, direction, another_room):

        opposite_directions = {"west": "east", "east": "west", "north": "south", "south": "north"}
        
        
        self.doors[direction] = another_room
        
        if direction in opposite_directions:
            opposite = opposite_directions[direction]
            another_room.doors[opposite] = self
        
    def get_name(self):
        return self.name

    def get_creatures(self):
        return self.creatures

    def get_doors(self):
        return self.doors

    def get_items(self):
        return self.items


# Represents an item in the game that can be collected and used by Pymons.
class Item:

    # Initialize a new item.
    def __init__(self, name, description, pick_up_items, consumable):
        self._name = name
        self._description = description
        self.pick_up_items = pick_up_items
        self.consumable = consumable

    def name(self):
        return self._name
    
    def pick_up_items(self):
        return self.pick_up_items
    
    def is_consumable(self):
        return self.consumable



# Represents creature in the game
class Creature:
    def __init__(self, nickname, description, location, adoptable = False):
        self.nickname = nickname
        self.description = description
        self.location = location 
        self.adoptable = adoptable

    def get_adoptable(self):
        return self.adoptable
    
    def get_location(self):
        return self.location


# Represents the player controlled Pymon character.
class Pymon(Creature):

    enery_max = 3 # Maximum energy level for any Pymon

    # Initialize a new Pymon.
    def __init__(self, name="The player", description="Default Pymon character", current_location=None):

        super().__init__(nickname=name, description=description, location=current_location)
        self.current_location = current_location  
        self.energy = 3  # Starting energy level
        self._inventory = [] # List of picked items
        self.pets = [] # List of captured Pymons
        self.track_moves = 0 # Movement-based energy consumption
        self.immunity = False # Battle immunity status
        self.battle_stats = BattleStats()   
    
    # Moves the Pymon in the specified direction.
    def move(self, direction=None):
        try:
            if direction not in ["west", "north", "east", "south"]:
                raise InvalidDirectionException(direction)
                
            if self.current_location is not None:
                if direction in self.current_location.doors and self.current_location.doors[direction] is not None:
                    new_location = self.current_location.doors[direction]
                    
                
                    if self in self.current_location.creatures:
                        self.current_location.creatures.remove(self)
                        
                    new_location.add_creature(self) 
                    self.current_location = new_location  
                    print("You moved to: ", self.current_location.name)

                    self.track_moves += 1
                    if self.track_moves >= 2:
                        self.track_moves = 0
                        self.energy -= 1
                        print(f"Your pymon energy decreased by 1. Current Energy: {self.energy}")

                        if self.energy <= 0:
                            self.random_escape()
                else:
                    raise InvalidDirectionException(direction)
        except InvalidDirectionException as e:
            print(f"Error: {e}")

    
    def random_escape(self):

        # Moving the pymon to a random location when energy is depleted.
        random_location = random.choice(self.current_location.doors.values())
        self.current_location.creatures.remove(self)
        random_location.add_creature(self)
        self.current_location = random_location
        print(f"{self.nickname} has escaped to a random location due to lack of energy.")
    
    
    def use_item(self, item_name):

        # Uses the item available in the inventory.
        item = next((i for i in self._inventory if i._name.lower() == item_name.lower()), None)
        if not item:
            print(f"This {item_name} is not in your inventory.")
            return
        
        if item._name.lower() == "apple":

            if self.energy < Pymon.enery_max:
                self.energy += 1
                self._inventory.remove(item)

                print("Your pymon ate the apple. Energy increased by 1")

            else:

                print("Energy is already at maximum.")

        elif item._name.lower() == "magic potion":
            self.immunity = True
            self._inventory.remove(item)  
            print("Drinked a magic potion. Temporary immunity activated for the next battle")

        elif item._name.lower() == "binocular":
            self.use_binocular()
            self._inventory.remove(item) 
            print("Binocular has been removed from inventory after use.")

    # Provide information of the adjacent or current location to the player.
    def use_binocular(self):

        direction = input("Choose a direction to look using your binocular. (current, west, north, east, south): ").lower()

        if direction == "current":
            print(f"In the current location, you see: {self.location_description()}")

        elif direction in self.current_location.doors and self.current_location.doors[direction]:
            connected_location = self.current_location.doors[direction]
            print(f"In the {direction} direction, there are {connected_location.description}.")

            if connected_location.creatures or connected_location.items:
                print("Creatures and items in this location: ")

                for creature in connected_location.creatures:
                    print(f" - Creature: {creature.nickname}")

                for item in connected_location.items:
                    print(f" - Item: {item._name}")
            else:
                print("No creatures or items in this location.")
        else:
            print(f"This direction ({direction}) leads nowhere.")

    # Return information of the creatures and items available in that location.
    def location_description(self):
        
        creatures = ', '.join([creature.nickname for creature in self.current_location.creatures if creature != self])

        items = ', '.join([item._name for item in self.current_location.items])

        return f"Creatures: {creatures}; Items: {items}" if creatures or items else "nothing."

    # Pick up the available items in the current location.
    def pick_item(self, name):

        # Looks for available items in the current location.
        item = next((item for item in self.current_location.items if item._name.lower() == name.lower()), None)
        
        if item:
            if item.pick_up_items:
                self._inventory.append(item)  
                self.current_location.items.remove(item)  
                print(f"{name} has been added to your inventory.")
            else:
                print(f"{name} cannot be picked up.")
        else:
            print(f"{name} is not available here.")

    # Display all the items in your inventory.
    def show_inventory(self):
      
        if self._inventory:
            print("Inventory items: ")
            for item in self._inventory:
                print(f" - {item._name}: {item._description}")
        else:
            print("Unlucky. Your inventory is empty.")

    # Initiate battle between your pymon and the creature in your current location.
    def Challenge(self, creature_name):
        opponent = None
        for creature in self.current_location.creatures:
            if creature.nickname == creature_name:
                opponent = creature
                break
                
        if opponent is None:
            print(f"{creature_name} is not available here.")
            return
        
        if opponent is self:
            print("You cannot challenge your own Pymon.")
            return
        
        if not opponent.adoptable:
            random_dialogue = [
                f"{opponent.nickname} just ignored you.",
                f"{opponent.nickname} just laughed at you.",
                f"{opponent.nickname} ran away.",
            ]
            print(random.choice(random_dialogue))
            return
        
        print(f"You started the challenge with {opponent.nickname}!")

        win = 0
        loss = 0
        draw = 0

        while win < 2 and loss < 2 and self.energy > 0:
            player_turn = input("\nChoose Rock, Paper, or Scissors: ").lower()

            if player_turn not in ["rock", "paper", "scissors"]:
                print("Error: Invalid choice. Try again")
                continue
            
            opponent_turn = random.choice(["rock", "paper", "scissors"])
            print(f"Opponent chose {opponent_turn}.")

            if player_turn == opponent_turn:
                print("Draw, no one wins this encounter")
                draw += 1
                continue

            elif (player_turn == "rock" and opponent_turn == "scissors") or \
                (player_turn == "scissors" and opponent_turn == "paper") or \
                (player_turn == "paper" and opponent_turn == "rock"):
                print(f"Your Pymon {self.nickname} won this encounter!")
                win += 1
            else:
                print(f"Your Pymon {self.nickname} lost this encounter.")
                loss += 1
                self.energy -= 1
                print(f"Remaining Energy: {self.energy}")

        self.battle_stats.add_battle(self.nickname, opponent.nickname, win, draw, loss)
        
        if win >= 2:
            print(f"You won the battle against {opponent.nickname}!")

            # Converts the captured creature into a Pymon.
            captured_pymon = Pymon(
                name=opponent.nickname,
                description=opponent.description,
                current_location=opponent.location
            )
            captured_pymon.energy = Pymon.enery_max  # Set full energy for new Pymon
            self.pets.append(captured_pymon)  # Add the new Pymon to pets
            self.current_location.creatures.remove(opponent)  # Remove original creature

        else:
            print(f"Lost the battle. {self.nickname} ran away into the wild.")
            
            if self.pets:
                next_pymon = self.pets.pop(0)
                next_pymon._inventory.extend(self._inventory)
                self._inventory.clear()
                print(f"{next_pymon.nickname} is now your primary Pymon.")
                self.current_location = next_pymon.current_location
            else:
                print("You dont have any Pymon left to help you in this game. GAME OVER!")
                sys.exit(0)

  
    def spawn(self, loc):
        if loc != None:
            loc.add_creature(self)
            self.current_location = loc
            
    def get_location(self):
        return self.current_location
    
    def get_energy(self):
        return self.energy
    
    def set_energy(self, energy):
        self.energy = energy

# Class for loading and managing game data. 
class Record:
    def __init__(self):
        self.locations = []
        self.creatures = []
        self.items = []

    # Imports location data from a CSV file.
    def import_location(self, filename='locations.csv'):
        try:
            with open(filename, 'r') as file:
                header = next(file)
                expected_columns = ['name', 'description', 'west', 'north', 'east', 'south']
                
                if not all(col.lower() in header.lower() for col in expected_columns):
                    raise InvalidInputFileFormat(filename, "Missing required columns in header")
                
                for line_num, line in enumerate(file, 2):  
                    parts = [x.strip() for x in line.split(',')]
                    
                    if len(parts) < 6:
                        raise InvalidInputFileFormat(filename, 
                            f"Line {line_num}: Expected 6 columns, got {len(parts)}")
                    
                    try:
                        
                        name = parts[0]
                        description = parts[1]
                        
                        if not name or not description:
                            raise InvalidInputFileFormat(filename, 
                                f"Line {line_num}: Name and description cannot be empty")
                        
                        location = Location(name, description)
                        self.locations.append(location)

                       
                        directions = {

                            'west': parts[2].replace("west =", "").strip(),
                            'north': parts[3].replace("north =", "").strip(),
                            'east': parts[4].replace("east =", "").strip(),
                            'south': parts[5].replace("south =", "").strip()
                        }
                        
                        for direction, connected_name in directions.items():
                            if connected_name != "None":
                                connected_location = next(
                                    (loc for loc in self.locations if loc.name == connected_name), 
                                    None
                                )
                                if connected_location:
                                    location.connect(direction, connected_location)
                    
                    except Exception as e:
                        raise InvalidInputFileFormat(filename, 
                            f"Line {line_num}: Error processing location data - {str(e)}")
                            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            raise

        except InvalidInputFileFormat as e:
            print(f"Error: {e}")
            raise

        except Exception as e:
            print(f"Unexpected error while reading {filename}: {str(e)}")
            raise
    pass

    # Returns a list of all imported locations. 
    def get_locations(self):
        return self.locations

    # Imports creature data from a CSV file.
    def import_creatures(self, filename='creatures.csv'):
       with open(filename, "r") as file:
            next(file)  # Skip header
            for line in file:
                parts = [x.strip() for x in line.split(',')]
                if len(parts) >= 3:
                    nickname = parts[0].strip()
                    description = parts[1].strip()
                    adoptable = parts[2].strip().lower() == 'yes' 
                    creature = Creature(nickname, description, None, adoptable)
                    self.creatures.append(creature)
    pass     

    # Imports item data from a CSV file
    def import_items(self, filename='items.csv'):
        try:
            with open(filename, "r") as file:
                header = next(file)  
                for line_num, line in enumerate(file, 2):  
                    parts = [x.strip() for x in line.split(',')]
                    
                    
                    if len(parts) < 4:
                        raise InvalidInputFileFormat(filename, 
                            f"Line {line_num}: Expected 4 columns, got {len(parts)}")
                    
                   
                    name = parts[0]
                    description = parts[1]
                    pickable = parts[2].strip().lower() == 'yes'
                    consumable = parts[3].strip().lower() == 'yes'
                    
                    
                    item = Item(name, description, pickable, consumable)
                    self.items.append(item)
                    
                    
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            raise

        except InvalidInputFileFormat as e:
            print(f"Error: {e}")
            raise

        except Exception as e:
            print(f"Unexpected error in items import: {str(e)}")
            raise
    pass

# Main game operation class that handles game setup, menu systems and overall game.
class Operation:

    # Initialize the game operation with empty locations and default Pymon. 
    def __init__(self):

        self.locations = []
        self.current_pymon = Pymon("Kimimon")

    # Displays and handles the main game menu.
    def handle_menu(self):
        while True:

            print("\nPlease issue a command to your Pymon:")
            print("1) Inspect Pymon")
            print("2) Inspect current location")
            print("3) Move")
            print("4) Pick an item")
            print("5) View inventory")
            print("6) Challenge a creature")
            print("7) Generate stats")
            print("8) Exit the program")
            user = input("Enter your choice: ")
            if user == '1':
                self.inspect_pymon_menu()
            elif user == '2':
                self.inspect_current_location()
            elif user == '3':
                self.move_pymon()
            elif user == '4':
                self.pick_item()
            elif user == '5':
                self.check_inventory()
            elif user == '6':
                self.challenge_creature()
            elif user == '7':
                self.stats_generate()
            elif user == '8':
                print("Exiting the game.")
                sys.exit(0)
            else:
                print("Error: Please enter between 1 - 8")

    # Displays the submenu for inspecting the Pymon.
    def inspect_pymon_menu(self):
        
        while True:

            print("\n1) Inspect current Pymon")
            print("2) List and select a benched Pymon to use")
            print("3) Return to main menu")

            user = input("Enter your choice: ")

            if user == '1':
                self.inspect_pymon()
            elif user == '2':
                self.select_benched_pymon()
            elif user == '3':
                break
            else:
                print("Error: Please enter a number between 1 and 3")


    
    # Displays the details of Pymon.
    def inspect_pymon(self):

        print("\nPymon Name:", self.current_pymon.nickname)
        print("Description:", self.current_pymon.description)

    # Allows the player to switch their primary Pymon.
    def select_benched_pymon(self):

        if not self.current_pymon.pets:
            print("You dont have any other Pymon")
            return

        print("\nAvailable Pymons:")

        for index, pymon in enumerate(self.current_pymon.pets, start=1):

            print(f"{index}) {pymon.nickname} - {pymon.description}")

        try:
            user = int(input("Enter the number of the Pymon to switch to, or 0 to cancel: "))

            if user == 0:
                return
            
            selected_pymon = self.current_pymon.pets.pop(user - 1)
            
            self.current_pymon.pets.append(self.current_pymon) 
            self.current_pymon = selected_pymon
            print(f"Your Primary Pymon is now: {self.current_pymon.nickname}")

        except (ValueError, IndexError):
            print("Error: Invalid selection.")

    # Displays the available things in the current location.
    def inspect_current_location(self):

        location = self.current_pymon.get_location()
        print("\nCurrent Location:", location.name)
        print("Description:", location.description)

        print("Creatures here:")
        for creature in location.creatures:
            print(f" * {creature.nickname}")

        print("Items available here:")
        for item in location.items:
            print(f" * {item._name}")

    # Move the pymon to different location.
    def move_pymon(self):

        try:
            direction = input("Enter a direction to move (west, north, east, south): ")
            self.current_pymon.move(direction)

        except InvalidDirectionException as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Unexpected error during movement: {str(e)}")
        

    # Sets up the game environment 
    def setup(self):

        try:
            record = Record()
            record.import_location(filename='locations.csv')
            record.import_creatures(filename='creatures.csv')
            record.import_items(filename='items.csv')
            self.locations = record.get_locations()
            self.items = record.items
            
            if not self.locations:
                raise InvalidInputFileFormat('locations.csv', 
                    "No locations found in locations file")
            
            starting_location = random.choice(self.locations)
            self.current_pymon.spawn(starting_location)

            for creature in record.creatures:
                random_location = random.choice(self.locations)
                creature.location = random_location
                random_location.add_creature(creature)

            
            for item in record.items:
                random_location = random.choice(self.locations)
                random_location.add_item(item)
                
                if item.consumable and random.random() < 0.5:
                    another_location = random.choice(self.locations)
                    another_item = Item(item._name, item._description, item.pick_up_items, item.consumable)
                    another_location.add_item(another_item)
            

        except (InvalidInputFileFormat, FileNotFoundError) as e:
            print(f"Error during setup: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error during setup: {str(e)}")
            sys.exit(1)

    # Starts the game with greeting. 
    def start_game(self):
        print("Welcome to Pymon World\n")
        print("It's just you and your loyal Pymon roaming around to find more Pymons to capture and adopt.\n")
        print("You started at ",self.current_pymon.get_location().get_name())
        self.handle_menu()

    # Allows player to pick up and add items to their inventory.
    def pick_item(self):
        item_name = input("Enter the item to pick: ")
        self.current_pymon.pick_item(item_name)

    # Displays the available items in the inventory.
    def check_inventory(self):

        if not self.current_pymon._inventory:
            print("Your inventory is empty.")
            return
        
        print("\nInventory items:")
        for idx, item in enumerate(self.current_pymon._inventory, start=1):
            print(f"{idx}. {item._name} - {item._description}")

        use_item = input("\nWould you like to use an item? (yes/no): ").lower()
        if use_item == 'yes':
            item_choice = input("What item you what to use? ")
            self.current_pymon.use_item(item_choice)

    # Initiates a battle between the your pymon and creature.
    def challenge_creature(self):

        creature_name = input("Enter the creature to challenge: ")
        self.current_pymon.Challenge(creature_name)

    # Generate stats of the battle of a pymon.
    def stats_generate(self):
        self.current_pymon.battle_stats.stats_generate()

if __name__ == '__main__':

    ops = Operation()
    if len(sys.argv) == 1:
        ops.setup()
    elif len(sys.argv) == 2:
        ops.setup(location_file=sys.argv[1])
    elif len(sys.argv) == 3:
        ops.setup(location_file=sys.argv[1], creature_file=sys.argv[2])
    elif len(sys.argv) == 4:
        ops.setup(location_file=sys.argv[1], creature_file=sys.argv[2], item_file=sys.argv[3])
    else:
        print("Usage: python pymon_game.py [locations.csv] [creatures.csv] [items.csv]")
        sys.exit(1)

    ops.start_game()