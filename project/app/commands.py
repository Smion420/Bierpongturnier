from domain.enums import BetType, Team, HandicapType
from typing import Optional

class CreatePlayer:
    def __init__(self, name: str, rating: int, amount_of_games: int):
        self.name = name
        self.rating = rating
        self.amount_of_games = amount_of_games

class CreateMatch:
    def __init__(self, team1_players: list[int], team2_players: list[int]):
        self.team1_players = team1_players
        self.team2_players = team2_players

class CreateBettor:
    def __init__(self, name: str):
        self.name = name
class Save:
    def __init__(self, name: str):
        self.name = name

class Load:
    def __init__(self, name: str):
        self.name = name
class ListPlayers:
    pass

class ListMatches:
    pass

class ListBettors:
    pass
class Create_Bet:
    def __init__(self, bettor_id: int, match_id: int, amount: float, bet_type: BetType, team: Optional[Team] = None, player_id: Optional[int] = None, handicap: Optional[HandicapType] = None):
        self.bettor_id = bettor_id
        self.match_id = match_id
        self.amount = amount
        self.bet_type = bet_type
        self.team = team
        self.player_id = player_id
        self.handicap = handicap

class Quotas:
    def __init__(self, match_id: Optional[int] = None):
        self.match_id = match_id

class EndMatch:
    def __init__(self, match_id: Optional[int], winner: Team, remaining: int, deathcup: bool, deathcup_player_id: Optional[int], bitchcup: bool, bitchcup_player_id: Optional[int], nacktemeile_overall: bool, nacktemeile_player_id: Optional[int], overtime: bool):
        self.match_id = match_id
        self.winner = winner
        self.remaining = remaining
        self.deathcup = deathcup
        self.deathcup_player_id = deathcup_player_id
        self.bitchcup = bitchcup
        self.bitchcup_player_id = bitchcup_player_id
        self.nacktemeile_overall = nacktemeile_overall
        self.nacktemeile_player_id = nacktemeile_player_id
        self.overtime = overtime