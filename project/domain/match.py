from typing import Optional, Dict, List
from domain.player import Player
from domain.bettor import Bettor
from domain.enums import BetType
from domain.bet import Bet


class Match:    
    id: Optional[int] = None
    def __init__(self, team1_players: List[Player], team2_players: List[Player]):
        if len(team1_players) != 2 or len(team2_players) != 2:
            raise ValueError("Each team must have exactly 2 players.")
        self.team1 = team1_players
        self.team2 = team2_players
        self.bets: List['Bet'] = []
        self.ended = False
        #results
        self.winner: Optional[str] = None
        self.remaining: Optional[int] = None
        self.deathcup: bool = False
        self.deathcup_player: Optional[str] = None
        self.bitchcup: bool = False
        self.bitchcup_player: Optional[str] = None
        self.nacktemeile_overall: bool = False
        self.nacktemeile_player: Optional[str] = None
        self.overtime: bool = False
        self.id = Match.amount_of_matches + 1


    def add_bet(self, bet: 'Bet'):
        if self.ended:
            raise Exception("No bets can be placed on a concluded match.")
        self.bets.append(bet)

    def get_teams(self) -> Dict[str, List[str]]:
        return {"Team 1": [player.name for player in self.team1], "Team 2": [player.name for player in self.team2]}

    def end_game(self, *, winner:int, remaining: int, deathcup: bool, deathcup_player: Optional[str], bitchcup: bool, bitchcup_player: Optional[str], nacktemeile_overall: bool, nacktemeile_player: Optional[str], overtime: bool):
        if self.ended:
            raise Exception("Match has already ended.")
        self.ended = True
        # populate individual attributes from provided results (legacy dict input)
        self.winner = winner
        self.remaining = remaining
        self.deathcup = deathcup
        self.deathcup_player = deathcup_player
        self.bitchcup = bitchcup
        self.bitchcup_player = bitchcup_player
        self.nacktemeile_overall = nacktemeile_overall
        self.nacktemeile_player = nacktemeile_player
        self.overtime = overtime
        payouts = compute_payouts(self)
        for bettor in Bettor.bettors.values():
            payout = payouts.get(bettor.name, 0.0)
            bettor.kontostand += payout
            # bank pays out the amount
            Bettor.bank -= payout

    
def compute_payouts(match: Match) -> Dict[str, float]:
    """Compute payouts per bettor for a match using per-match attributes.

    Rewritten with `match/case` for clarity.
    """
    payouts: Dict[str, float] = {}

    for bet in match.bets:
        payout = 0.0
        match bet.bet_type:
            case BetType.NORMAL:
                if bet.team and bet.team == match.winner:
                    payout = bet.amount * bet.quota
            case BetType.DEATHCUPOVERALL:
                if match.deathcup:
                    payout = bet.amount * bet.quota
            case BetType.DEATHCUPSPECIFIC:
                if bet.player and bet.player.name == match.deathcup_player:
                    payout = bet.amount * bet.quota
            case BetType.BITCHCUPOVERALL:
                if match.bitchcup:
                    payout = bet.amount * bet.quota
            case BetType.BITCHCUPSPECIFIC:
                if bet.player and bet.player.name == match.bitchcup_player:
                    payout = bet.amount * bet.quota
            case BetType.NACKTEMEILEOVERALL:
                if match.nacktemeile_overall:
                    payout = bet.amount * bet.quota
            case BetType.NACKTEMEILESPECIFIC:
                if bet.player and bet.player.name == match.nacktemeile_player:
                    payout = bet.amount * bet.quota
            case BetType.OVERTIME:
                if match.overtime:
                    payout = bet.amount * bet.quota
            case BetType.HANDICAP:
                if match.remaining is not None:
                    try:
                        if int(match.remaining) > int(bet.details):
                            payout = bet.amount * bet.quota
                    except Exception:
                        pass
            case _:
                # unknown bet type; no payout
                pass

        payout -= bet.amount
        if bet.bettor:
            payouts[bet.bettor.name] = payouts.get(bet.bettor.name, 0.0) + payout
    return payouts

