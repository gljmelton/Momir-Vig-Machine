import msgspec

class GameModeManager:
    def __init__(self):
        self.selected_mode = 0

        with open("gamemodes.json", 'rb') as file:
            self.game_mode_data = msgspec.json.decode(file.read(), type=list[GameMode])

    def get_game_mode_name_list(self):
        game_mode_name_list = []

        for game_mode in self.game_mode_data:
            print(game_mode.name)
            game_mode_name_list.append(game_mode.name)

        return game_mode_name_list

    def get_selected_game_mode_name(self):
        return self.game_mode_data[self.selected_mode].name

    def select_game_mode(self, game_mode_name):
        for game_mode in self.game_mode_data:
            if game_mode.name == game_mode_name:
                return game_mode

        return None

    def get_game_mode(self):
        return self.game_mode_data[self.selected_mode]

    def increment_selected_mode(self):
        self.selected_mode += 1

        if self.selected_mode >= len(self.game_mode_data):
            self.selected_mode = 0

    def decrement_selected_mode(self):
        self.selected_mode -= 1
        if self.selected_mode < 0:
            self.selected_mode = len(self.game_mode_data)-1

class FilterSetIncExcl(msgspec.Struct):
    inclusive : list
    exclusive : list

class FilterSet(msgspec.Struct):
    include : FilterSetIncExcl
    exclude : FilterSetIncExcl

class Filter(msgspec.Struct):
    legal: FilterSet
    types: FilterSet
    colors: FilterSet

class GameMode(msgspec.Struct):
    name : str
    description : str
    rules: str
    filter : Filter

class GameModes(msgspec.Struct):
    game_mode_list: list[GameMode]

if __name__ == "__main__":
    game_mode_manager = GameModeManager()
    print(game_mode_manager.game_mode_data)