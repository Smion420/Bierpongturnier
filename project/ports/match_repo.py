from typing import Protocol, Any
from domain.match import Match

class MatchRepository(Protocol):
	def add(self, match: Match) -> None:
		...

	def get(self, match_id: int) -> Match:
		...

	def list(self) -> list[Match]:
		...

	def exists(self, match_id: int) -> bool:
		...

