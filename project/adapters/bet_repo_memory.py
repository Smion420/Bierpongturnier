from domain.bet import Bet
from adapters.mappers.bet_mapper import bet_to_dict, bet_from_dict

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

	def liste(self) -> list[Bet]:
		return list(self._bets.values())

	def list_by_match(self, match_id: int) -> list[Bet]:
		bets = []
		for bet in self._bets.values():
			if getattr(bet, "match_id", None) == match_id:
				bets.append(bet)
		return bets

		
	
	def export_state(self) -> dict:
			return {
				"next_id": self._next_id,
				"items": [bet_to_dict(b) for b in self._bets.values()],
			}	
	def import_state(self, state: dict) -> None:
		self._next_id = int(state.get("next_id", 1))
		items = state.get("items", [])

		bets = [bet_from_dict(d) for d in items]

		self._bets = {}
		max_id = 0
		for b in bets:
			bid = getattr(b, "id", None)
			if bid is None:
				continue
			bid = int(bid)
			self._bets[bid] = b
			if bid > max_id:
				max_id = bid

		# Counter korrigieren, falls JSON keinen oder einen falschen Counter hatte
		self._next_id = max(self._next_id, max_id + 1)
