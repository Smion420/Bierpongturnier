from typing import Callable, Optional, Dict, Any, List
from enum import Enum

class BetType(Enum):
    NORMAL = "normal"
    HANDICAP = "handicap"
    DEATHCUPOVERALL = "deathcup_overall"
    DEATHCUPSPECIFIC = "deathcup_specific"
    BITCHCUPOVERALL = "bitchcup_overall"
    BITCHCUPSPECIFIC = "bitchcup_specific"
    NACKTEMEILEOVERALL = "nacktemeile_overall"
    NACKTEMEILESPECIFIC = "nacktemeile_specific"
    OVERTIME = "overtime"
    CUPS_HIT = "cups_hit"


class Player:
    all_players = []
    def __init__(self, name: str, ratingwin: float = 0.0, matchamount: int = 0):
        self.name = name
        self.ratingwin = ratingwin
        self.wins = 0
        self.losses = 0
        self.cups_hit = 0
        self.rd = 5000/(matchamount + 25) 
        # match_history will store records as dicts: {"match_id": int, "results": {...}}
        self.match_history: List[Dict[str, Any]] = []
        Player.all_players.append(self)

    def record_match(self, match, results: Dict[str, Any], match_id: Optional[int] = None):
        record = {"match_id": match_id, "results": results}
        self.match_history.append(record)
        winner = results.get("winner")
        if winner == ("Team 1" if self in match.team1 else "Team 2"):
            self.wins += 1
        else:
            self.losses += 1
        # If per-player cups are provided, use that; otherwise fall back to total cups_hit
        cups_by_player = results.get("cups_by_player")
        if cups_by_player and isinstance(cups_by_player, dict):
            try:
                self.cups_hit += int(cups_by_player.get(self.name, 0))
            except Exception:
                pass
        else:
            self.cups_hit += int(results.get("cups_hit", 0))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ratingwin": self.ratingwin,
            "wins": self.wins,
            "losses": self.losses,
            "cups_hit": self.cups_hit,
            "match_history": self.match_history,
            "rd": self.rd,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        p = Player(d["name"], d.get("ratingwin", 0.0))
        p.wins = d.get("wins", 0)
        p.losses = d.get("losses", 0)
        p.cups_hit = d.get("cups_hit", 0)
        p.match_history = d.get("match_history", [])
        p.rd = d.get("rd", 200)
        return p




class Match:    
    def __init__(self, team1_players: List[Player], team2_players: List[Player]):
        if len(team1_players) != 2 or len(team2_players) != 2:
            raise ValueError("Each team must have exactly 2 players.")
        self.team1 = team1_players
        self.team2 = team2_players
        self.bets: List['Bet'] = []
        self.ended = False
        self.results: Optional[Dict[str, Any]] = None
        self.id: Optional[int] = None

    def add_bet(self, bet: 'Bet'):
        if self.ended:
            raise Exception("No bets can be placed on a concluded match.")
        self.bets.append(bet)

    def get_teams(self) -> Dict[str, List[str]]:
        return {"Team 1": [player.name for player in self.team1], "Team 2": [player.name for player in self.team2]}

    def end_game(self, results: Dict[str, Any], match_id: Optional[int] = None):
        if self.ended:
            raise Exception("Match has already ended.")
        self.ended = True
        # store results on the match for persistence
        self.results = results
        cups_by_player = results.get("cups_by_player", {}) if isinstance(results.get("cups_by_player"), dict) else {}
        total_cups = results.get("cups_hit", 0)
        # compute total_cups if not provided
        if not total_cups and cups_by_player:
            try:
                total_cups = sum(int(v) for v in cups_by_player.values())
            except Exception:
                total_cups = results.get("cups_hit", 0)

        payouts = compute_payouts(self, self.results)
        for bettor in Bettor.bettors.values():
            payout = payouts.get(bettor.name, 0.0)
            bettor.kontostand += payout
            # bank pays out the amount
            Bettor.bank -= payout

        for player in self.team1 + self.team2:
            # record match id if provided; player.record_match will update cups from results
            player.record_match(self, results, match_id=match_id)
        # Recompute bank as the negative sum of all bettors' kontostand (bank holds opposite of bettors)


    def to_dict(self, match_id: int) -> Dict[str, Any]:
        return {
            "id": self.id,
            "team1": [p.name for p in self.team1],
            "team2": [p.name for p in self.team2],
            "bets": [b.to_dict() for b in self.bets],
            "ended": self.ended,
            "results": self.results,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any], players_dict: Dict[str, Player]):
        t1 = [players_dict[name] for name in d["team1"]]
        t2 = [players_dict[name] for name in d["team2"]]
        m = Match(t1, t2)
        m.ended = d.get("ended", False)
        m.results = d.get("results")
        m.id = d.get("id")
        # bets will be reconstructed after bettors exist
        return m
def compute_payouts(match: Match, results: Dict[str, Any]) -> Dict[str, float]:
    """Compute payouts per bettor for a match given results without applying them."""
    payouts: Dict[str, float] = {}
    cups_by_player = results.get("cups_by_player", {}) if isinstance(results.get("cups_by_player"), dict) else {}
    total_cups = results.get("cups_hit", 0)
    if not total_cups and cups_by_player:
        try:
            total_cups = sum(int(v) for v in cups_by_player.values())
        except Exception:
            total_cups = results.get("cups_hit", 0)

    for bet in match.bets:
        payout = 0.0
        if bet.bet_type == BetType.NORMAL:
            if bet.team and bet.team == results.get("winner"):
                payout = bet.amount * bet.quota 
        elif bet.bet_type == BetType.DEATHCUPOVERALL:
            if results.get("deathcup", False):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.DEATHCUPSPECIFIC:
            if bet.player and bet.player.name == results.get("deathcup_player"):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.BITCHCUPOVERALL:
            if results.get("bitchcup", False):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.BITCHCUPSPECIFIC:
            if bet.player and bet.player.name == results.get("bitchcup_player"):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.NACKTEMEILEOVERALL:
            if results.get("nacktemeile_overall", False):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.NACKTEMEILESPECIFIC:
            if bet.player and bet.player.name == results.get("nacktemeile_player"):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.OVERTIME:
            if results.get("overtime", False):
                payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.HANDICAP:
            if results.get("remaining", False):
                if results.get("remaining", 0) > bet.details:
                    payout = bet.amount * bet.quota
        elif bet.bet_type == BetType.CUPS_HIT:
            if bet.player and bet.details:
                try:
                    target = int(bet.details.get("cups", -1))
                    player_cups = int(cups_by_player.get(bet.player.name, 0))
                    if player_cups == target:
                        payout = bet.amount * bet.quota
                except Exception:
                    pass
            else:
                if bet.details and int(bet.details.get("cups", -1)) == int(total_cups):
                    payout = bet.amount * bet.quota
        payout -= bet.amount
        if bet.bettor:
            payouts[bet.bettor.name] = payouts.get(bet.bettor.name, 0.0) + payout
    return payouts

class Bet:
    def __init__(self, calculator: callable,match: Match, team: Optional[str], amount: float, bet_type: BetType, bettor: Optional['Bettor'] = None,
                 player: Optional[Player] = None, details: Optional[Dict[str, Any]] = None, quota: Optional[float] = None, bank:Optional[float] = None):
        self.match = match
        self.team = team
        self.amount = float(amount)
        self.player = player
        self.bet_type = bet_type
        self.details = details or {}
        self.quota = quota if quota is not None else calculator(match, bet_type, team, player, self.details, bank)
        self.bettor = bettor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match": self.match.id,
            "team": self.team,
            "amount": self.amount,
            "player": self.player.name if self.player else None,
            "bet_type": self.bet_type.value,
            "details": self.details,
            "quota": self.quota,
            "bettor": self.bettor.name if self.bettor else None,
        }

    @staticmethod
    def from_dict(calculator: callable, d: Dict[str, Any], match: Match, players: Dict[str, Player], bettors: Dict[str, 'Bettor']):
        bettor = bettors.get(d.get("bettor"))
        player = players.get(d.get("player")) if d.get("player") else None
        bet_type = BetType(d.get("bet_type"))
        b = Bet(calculator, match, d.get("team"), d.get("amount", 0), bet_type, bettor=bettor, player=player, details=d.get("details"), quota=d.get("quota"))
        return b
class Bettor:
    bettors = {}
    # Bank holds the opposite of the sum of all bettors' kontostand
    bank: float = 0.0
    def __init__(self, name: str):
        self.name = name
        self.kontostand = 0.0
        self.bets: List[Bet] = []
        Bettor.bettors[self.name] = self

    def get_money(self) -> float:
        return self.kontostand

    def place_bet(self, calculator:callable, match: Match, team: Optional[str], player: Optional[Player], amount: float, bet_type: BetType, details: Optional[Dict[str, Any]] = None) -> Bet:
        bet = Bet(calculator, match, team, amount, bet_type, bettor=self, player=player, details=details, bank = Bettor.bank)
        self.bets.append(bet)
        match.add_bet(bet)
        return bet

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "kontostand": self.kontostand, "bets": [b.to_dict() for b in self.bets]}

    @staticmethod
    def from_dict(d: Dict[str, Any]):
        bt = Bettor(d["name"])
        bt.kontostand = d.get("kontostand", 0.0)
        # bets will be reconstructed after matches and players available
        return bt