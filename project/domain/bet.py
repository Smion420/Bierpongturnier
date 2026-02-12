from typing import Optional
from domain.enums import BetType, Team, HandicapType

class Bet:
    id: Optional[int] = None
    def __init__(self,match_id: int, quota: float, team: Optional[Team], amount: float, bet_type: BetType, bettor_id: int,
                 player_id: Optional[int] = None, handicap: Optional[HandicapType] = None):
        self.match_id = match_id
        self.team = team
        self.amount = float(amount)
        self.player_id = player_id
        self.bet_type = bet_type
        self.handicap = handicap
        self.quota = quota
        self.bettor_id = bettor_id

