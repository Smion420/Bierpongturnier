from domain.bettor import Bettor

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

	def list(self) -> list[Bettor]:
		return list(self._bettors.values())

	def exists_by_name(self, name: str) -> bool:
		return name in self._bettors
