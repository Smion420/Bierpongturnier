from typing import Optional, List
from domain.enums import BetType, Team


class Bettor:
	id: Optional[int] = None
	# Bank holds the opposite of the sum of all bettors' kontostand
	def __init__(self, name: str):
		self.name = name
		self.kontostand = 0.0

	def get_money(self) -> float:
		return self.kontostand