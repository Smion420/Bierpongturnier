import json
from pathlib import Path
from adapters.bet_repo_memory import BetRepositoryMemory
from adapters.match_repo_memory import MatchRepositoryMemory
from adapters.player_repo_memory import PlayerRepositoryMemory
from adapters.bettor_repo_memory import BettorRepositoryMemory
from domain.enums import BetType, Team, HandicapType


def enum_default(obj):
    if isinstance(obj, Team):
        return obj.value
    if isinstance(obj, BetType):
        return obj.value
    if isinstance(obj, HandicapType):
        return obj.value

class JsonSnapshotStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def save(
        self,
        *,
        player_repo: PlayerRepositoryMemory,
        bettor_repo: BettorRepositoryMemory,
        match_repo: MatchRepositoryMemory,
        bet_repo: BetRepositoryMemory,
    ) -> None:
        payload = {
            "meta": {"version": 1},
            "players": player_repo.export_state(),
            "bettors": bettor_repo.export_state(),
            "matches": match_repo.export_state(),
            "bets": bet_repo.export_state(),
        }
        try:
            self.path.write_text(json.dumps(payload, indent=2, default=enum_default), encoding="utf-8")
        except Exception as e:
            print(f"Fehler beim Speichern des Snapshots: {e}")
            raise

    def load(
        self,
        *,
        player_repo: PlayerRepositoryMemory,
        bettor_repo: BettorRepositoryMemory,
        match_repo: MatchRepositoryMemory,
        bet_repo: BetRepositoryMemory,
    ) -> None:
        if not self.path.exists():
            # Du kannst hier auch Error werfen, je nach gewünschtem Verhalten
            return

        payload = json.loads(self.path.read_text(encoding="utf-8"))

        # Defaults verhindern KeyErrors bei leeren/alten Dateien
        player_repo.import_state(payload.get("players", {"next_id": 1, "items": []}))
        bettor_repo.import_state(payload.get("bettors", {"next_id": 1, "items": []}))
        match_repo.import_state(payload.get("matches", {"next_id": 1, "items": []}))
        bet_repo.import_state(payload.get("bets", {"next_id": 1, "items": []}))
