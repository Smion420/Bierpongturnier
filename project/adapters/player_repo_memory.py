from domain.player import Player


class PlayerRepositoryMemory:
	def __init__(self):
		self._players: dict[int, Player] = {}
		self._next_id = 1

	def add(self, player: Player) -> int:
		pid = self._next_id
		self._next_id += 1
		try:
			setattr(player, "id", pid)
		except Exception:
			pass
		self._players[pid] = player
		return pid

	def get(self, player_id: int) -> Player:
		return self._players.get(player_id)

	def list(self) -> list[Player]:
		return list(self.players.values())
	
	def exists_by_name(self, name: str) -> bool:
		return name in self.players