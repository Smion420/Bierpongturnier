from typing import Optional, List

class Bettor:
	id: Optional[int] = None
	# Bank holds the opposite of the sum of all bettors' kontostand
	bank: float = 0.0
	def __init__(self, name: str):
		self.name = name
		self.kontostand = 0.0
		self.bets: List[int] = []


	def get_money(self) -> float:
		return self.kontostand

	def place_bet(self, calculator:callable, match: Match, team: Optional[str], player: Optional[Player], amount: float, bet_type: BetType, details: Optional[Dict[str, Any]] = None) -> Bet:
		bet = Bet(calculator, match, team, amount, bet_type, bettor=self, player=player, details=details, bank = Bettor.bank)
		self.bets.append(bet)
		match.add_bet(bet)
		return bet