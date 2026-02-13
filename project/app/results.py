from domain.bet import Bet

class Ok:
    def __init__(self, message: str = "OK", data: any = None):
        self.message = message
        self.data = data
    
class Error:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

class PlayersListed:
    def __init__(self, players: list):
        self.players = players

class MatchesListed:
    def __init__(self, matches: list, data: list):
        self.matches = matches
        self.data = data

class BettorsListed:
    def __init__(self, bettors: list):
        self.bettors = bettors

class BetPlaced:
    def __init__(self, bet: Bet):
        self.bet = bet

class QuotasListed:
    def __init__(self, match, quotas: list):
        # match: Match object
        # quotas: list of tuples (description:str, quota: float|None)
        self.match = match
        self.quotas = quotas

class MatchEnded:
    def __init__(self, match_id: int, payouts: dict[int, float]):
        self.match_id = match_id
        self.payouts = payouts