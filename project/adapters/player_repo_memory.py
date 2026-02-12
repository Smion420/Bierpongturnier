from domain.player import Player
from adapters.mappers.player_mapper import player_from_dict, player_to_dict


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

	def liste(self) -> list[Player]:
		return list(self._players.values())
	
	def exists_by_name(self, name: str) -> bool:
		for p in self._players.values():
			if getattr(p, "name", None) == name:
				return True
		return False
	def export_state(self) -> dict:
		return {
				"next_id": self._next_id,
				"items": [player_to_dict(p) for p in self._players.values()],
		}

	def import_state(self, state: dict) -> None:
		# Counter laden
		self._next_id = int(state.get("next_id", 1))

		# Objekte rekonstruieren
		items = state.get("items", [])
		players = [player_from_dict(d) for d in items]

		# Dict neu aufbauen
		self._players = {}
		max_id = 0

		for p in players:
			pid = getattr(p, "id", None)
			if pid is None:
				continue

			pid = int(pid)
			self._players[pid] = p
			if pid > max_id:
				max_id = pid

		# Counter absichern (falls JSON next_id fehlt/falsch ist)
		self._next_id = max(self._next_id, max_id + 1)