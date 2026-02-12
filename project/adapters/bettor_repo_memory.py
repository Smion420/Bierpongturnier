from domain.bettor import Bettor
from adapters.mappers.bettor_mapper import bettor_to_dict, bettor_from_dict

class BettorRepositoryMemory:
	def __init__(self):
		self._bettors: dict[int, Bettor] = {}
		self._next_id = 1

	def add(self, bettor: Bettor) -> int:
		bid = self._next_id
		self._next_id += 1
		try:
			setattr(bettor, "id", bid)
		except Exception:
			pass
		self._bettors[bid] = bettor
		return bid

	def get(self, bettor_id: int) -> Bettor:
		return self._bettors.get(bettor_id)

	def liste(self) -> list[Bettor]:
		return list(self._bettors.values())

	def exists_by_name(self, name: str) -> bool:
		return name in self._bettors
	
	def get_bank(self) -> float:
		return -sum(getattr(b, "kontostand", 0) for b in self._bettors.values())

	def export_state(self) -> dict:
		return {
			"next_id": self._next_id,
			"items": [bettor_to_dict(b) for b in self._bettors.values()],
		}

	def import_state(self, state: dict) -> None:
		self._next_id = int(state.get("next_id", 1))
		items = state.get("items", [])

		bettors = [bettor_from_dict(d) for d in items]

		self._bettors = {}
		max_id = 0
		for b in bettors:
			bid = getattr(b, "id", None)
			if bid is None:
				continue
			bid = int(bid)
			self._bettors[bid] = b
			if bid > max_id:
				max_id = bid

		# Counter korrigieren, falls JSON keinen oder einen falschen Counter hatte
		self._next_id = max(self._next_id, max_id + 1)
