from typing import Optional
from enums import BetType, Team, HandicapType

class Bet:
    id: Optional[int] = None
    def __init__(self, calculator: callable,match_id: int, team: Optional[Team], amount: float, bet_type: BetType, bettor_id: int,
                 player_id: Optional[int] = None, handicap: Optional[HandicapType] = None,bank:Optional[float] = None):
        self.match_id = match_id
        self.team = team
        self.amount = float(amount)
        self.player_id = player_id
        self.bet_type = bet_type
        self.handicap = handicap
        self.quota = calculator(match_id, bet_type, team, player_id, self.handicap, bank)
        self.bettor_id = bettor_id

