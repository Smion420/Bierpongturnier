from typing import Protocol, Any
from domain.bettor import Bettor

class BettorRepository(Protocol):
	def add(self, bettor: Bettor) -> None:
		...

	def get(self, bettor_id: int) -> Bettor:
		...

	def list(self) -> list[Bettor]:
		...

	def exists_by_name(self, name: str) -> bool:
		...
