from domain.match import Match

class MatchRepositoryMemory:
	def __init__(self):
		self._matches: dict[int, Match] = {}
		self._next_id = 1

	def add(self, match: Match) -> int:
		mid = self._next_id
		self._next_id += 1
		try:
			setattr(match, "id", mid)
		except Exception:
			pass
		self._matches[mid] = match
		return mid

	def get(self, match_id: int) -> Match:
		return self._matches.get(match_id)

	def list(self) -> list[Match]:
		return list(self._matches.values())

	def exists(self, match_id: int) -> bool:
		return match_id in self._matches
