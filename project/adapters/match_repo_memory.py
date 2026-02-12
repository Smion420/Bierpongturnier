from domain.match import Match
from adapters.mappers.match_mapper import match_to_dict, match_from_dict

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

	def liste(self) -> list[Match]:
		return list(self._matches.values())

	def exists(self, match_id: int) -> bool:
		return match_id in self._matches

	def export_state(self) -> dict:
		return {
			"next_id": self._next_id,
			"items": [match_to_dict(m) for m in self._matches.values()],
		}

	def import_state(self, state: dict) -> None:
		self._next_id = int(state.get("next_id", 1))
		items = state.get("items", [])

		matches = [match_from_dict(d) for d in items]

		self._matches = {}
		max_id = 0
		for m in matches:
			mid = getattr(m, "id", None)
			if mid is None:
				continue
			mid = int(mid)
			self._matches[mid] = m
			if mid > max_id:
				max_id = mid

		# Counter korrigieren, falls JSON keinen oder einen falschen Counter hatte
		self._next_id = max(self._next_id, max_id + 1)
