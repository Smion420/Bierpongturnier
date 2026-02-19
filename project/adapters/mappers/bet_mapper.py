from domain.bet import Bet
from domain.enums import BetType, Team, HandicapType

def bet_to_dict(b: Bet) -> dict:
	return {
		"id": getattr(b, "id", None),

		"match_id": getattr(b, "match_id", None),
		"bettor_id": getattr(b, "bettor_id", None),
		"quota": getattr(b, "quota", None),
		"amount": getattr(b, "amount", None),
		"team": getattr(b, "team", None),
		"bet_type": getattr(b, "bet_type", None),
		"player_id": getattr(b, "player_id", None),
		"handicap": getattr(b, "handicap", None),
	}

def bet_from_dict(d: dict) -> Bet:

	bet = Bet(
		match_id=d.get("match_id"),
		team=d.get("team"),
		amount=d.get("amount"),
		bet_type=d.get("bet_type"),
		bettor_id=d.get("bettor_id"),
		player_id=d.get("player_id"),
		handicap=d.get("handicap"),
		quota=d.get("quota"),
	)
	setattr(bet, "id", d.get("id"))
	return bet