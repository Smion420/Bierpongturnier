from domain.bet import Bet

class BetRepositoryMemory:
	def __init__(self):
		self._bets: dict[int, Bet] = {}
		self._next_id = 1

	def add(self, bet: Bet) -> int:
		bid = self._next_id
		self._next_id += 1
		try:
			setattr(bet, "id", bid)
		except Exception:
			pass
		self._bets[bid] = bet
		return bid

	def get(self, bet_id: int) -> Bet:
		return self._bets.get(bet_id)

	def list(self) -> list[Bet]:
		return list(self._bets.values())

	def list_by_match(self, match_id: int) -> list[Bet]:
		return [b for b in self._bets.values() if getattr(b, "match", None) and getattr(b.match, "id", None) == match_id]
