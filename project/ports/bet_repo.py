from typing import Protocol, Any
from domain.bet import Bet

class BetRepository(Protocol):
    def add(self, bet: Bet) -> None:
        ...

    def get(self, bet_id: int) -> Bet:
        ...

    def list(self) -> list[Bet]:
        ...

    def list_by_match(self, match_id: int) -> list[Bet]:
        ...
