from typing import Protocol
from domain.player import Player

class PlayerRepository(Protocol):
    def add(self, player: Player) -> None:
        ...

    def get(self, player_id: int) -> Player:
        ...

    def list(self) -> list[Player]:
        ...
    def exists_by_name(self, name: str) -> bool:
        ...