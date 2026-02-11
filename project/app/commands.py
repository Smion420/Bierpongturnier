

class CreatePlayer:
    def __init__(self, name: str, rating: int, amount_of_games: int):
        self.name = name
        self.rating = rating
        self.amount_of_games = amount_of_games

class CreateMatch:
    def __init__(self, team1_players: list[int], team2_players: list[int]):
        self.team1_players = team1_players
        self.team2_players = team2_players