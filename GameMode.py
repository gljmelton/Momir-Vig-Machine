class GameModeManager:
    def __init__(self):
        self.selected_mode = 0

        self.game_mode_list = []

        self.game_mode_list.extend(
            [Filter("Basic")
                .add_legal(include = ["vintage"])
                .add_types(include = ["creature"]),
            Filter("Standard")
                .add_legal(include = ["standard"])
                .add_types(include = ["creature"])])

    def get_game_mode_name_list(self):
        game_mode_name_list = []

        for game_mode in self.game_mode_list:
            print(game_mode.name)
            game_mode_name_list.append(game_mode.name)

        return game_mode_name_list

    def get_selected_game_mode_name(self):
        return self.game_mode_list[self.selected_mode].name

    def select_game_mode(self, game_mode_name):
        for game_mode in self.game_mode_list:
            if game_mode.name == game_mode_name:
                return game_mode

        return None

    def get_filter(self):
        return self.game_mode_list[self.selected_mode]

    def increment_selected_mode(self):
        self.selected_mode += 1

        if self.selected_mode >= len(self.game_mode_list):
            self.selected_mode = 0

    def decrement_selected_mode(self):
        self.selected_mode -= 1
        if self.selected_mode < 0:
            self.selected_mode = len(self.game_mode_list)-1

class Filter:
    def __init__(self, name):
        self.name = name

        self.legal_include = []
        self.legal_exclude = []

        self.type_include = []
        self.type_exclude = []

    def add_legal(self, include = None, exclude = None):
        if include is not None:
            self.legal_include = include

        if exclude is not None:
            self.legal_exclude = exclude

        return self

    def add_types(self, include = None, exclude = None):
        if include is not None:
            self.type_include = include

        if exclude is not None:
            self.type_exclude = exclude

        return self