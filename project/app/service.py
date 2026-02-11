from app.commands import CreatePlayer, CreateMatch
from app.results import Ok, Error
from domain import Player, Match, Bettor, Bet, BetType, compute_payouts
from ports.player_repo import PlayerRepository
from ports.bettor_repo import BettorRepository
from ports.match_repo import MatchRepository

class AppService:
	def __init__(self, player_repo: PlayerRepository, match_repo: MatchRepository, bettor_repo: BettorRepository):
		self.player_repo = player_repo
		self.match_repo = match_repo
		self.bettor_repo = bettor_repo


	def handle(self, cmd):
		if isinstance(cmd, CreatePlayer):
			return self._create_player(cmd)
		if isinstance(cmd, CreateMatch):
			return self._create_match(cmd)

		return Error("unknown_command", f"Unsupported command: {type(cmd).__name__}")

	def _create_player(self, cmd: CreatePlayer):
		name = cmd.name.strip()

		if not name:
			return Error("invalid_name", "Name darf nicht leer sein.")

		if not isinstance(cmd.rating, int):
			return Error("invalid_rating_type", "Rating muss eine ganze Zahl sein.")

		if cmd.rating < 0 or cmd.rating > 3000:
			return Error("invalid_rating_range", "Rating muss zwischen 0 und 3000 liegen.")

		if self.player_repo.exists_by_name(name):
			return Error("duplicate_player", f"Spieler '{name}' existiert bereits.")

		player = Player(name=name, rating=cmd.rating)
		self.player_repo.add(player)

		return Ok(message=f"Spieler '{name}' wurde angelegt.", data=player)
	def _create_match(self, cmd: CreateMatch):
		p11 = self.player_repo.get(cmd.player1_team1_id)
		p12 = self.player_repo.get(cmd.player2_team1_id)
		p21 = self.player_repo.get(cmd.player1_team2_id)
		p22 = self.player_repo.get(cmd.player2_team2_id)
		if not all([p11, p12, p21, p22]):
			return Error("invalid_player_id", "Ein oder mehrere Spieler-IDs sind ungültig.")
		for pi in [p11, p12, p21, p22]:
			for pj in [p11, p12, p21, p22]:
				if pi == pj:
					return Error("duplicate_player_in_match", f"Spieler '{pi.name}' ist mehrfach im Match vertreten.")
		t1 = [p11, p12]
		t2 = [p21, p22]
		match = Match(team1=t1, team2=t2)
		self.match_repo.add(match)
		return Ok(message=f"Match zwischen {', '.join(p.name for p in t1)} und {', '.join(p.name for p in t2)} wurde angelegt.", data=match)
