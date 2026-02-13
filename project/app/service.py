from app.commands import CreatePlayer, CreateMatch, CreateBettor, ListPlayers, ListMatches, ListBettors, Load, Save, Create_Bet, Quotas, EndMatch
from app.results import MatchEnded, Ok, Error, PlayersListed, MatchesListed, BettorsListed, BetPlaced, QuotasListed
from domain.enums import BetType, Team, HandicapType
from domain.player import Player
from domain.match import Match, compute_payouts
from domain.bet import Bet
from domain.bettor import Bettor
from domain.quoten import calculate_quota
from ports.player_repo import PlayerRepository
from ports.bettor_repo import BettorRepository
from ports.match_repo import MatchRepository
from ports.bet_repo import BetRepository
from adapters.snapshot import JsonSnapshotStore
from pathlib import Path


class AppService:
	def __init__(self, player_repo: PlayerRepository, match_repo: MatchRepository, bettor_repo: BettorRepository, bet_repo: BetRepository):
		self.player_repo = player_repo
		self.match_repo = match_repo
		self.bettor_repo = bettor_repo
		self.bet_repo = bet_repo
		self.saves_dir = Path(__file__).parent.parent / "saves"


	def handle(self, cmd):
		if isinstance(cmd, CreatePlayer):
			return self._create_player(cmd)
		if isinstance(cmd, CreateBettor):
			return self._create_bettor(cmd)
		if isinstance(cmd, CreateMatch):
			return self._create_match(cmd)
		if isinstance(cmd, ListBettors):
			return self._list_bettors()
		if isinstance(cmd, Save):
			return self._save_snapshot(cmd)
		if isinstance(cmd, Load):
			return self._load_snapshot(cmd)
		if isinstance(cmd, ListPlayers):
			return self._list_players()
		if isinstance(cmd, ListMatches):
			return self._list_matches()
		if isinstance(cmd, Create_Bet):
			return self._create_bet(cmd)
		if isinstance(cmd, EndMatch):
			return self._end_match(cmd)
		if isinstance(cmd, Quotas):
			return self._quotas(cmd)

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

		player = Player(name=name, rating=cmd.rating, matchamount=cmd.amount_of_games)
		self.player_repo.add(player)

		return Ok(message=f"Spieler '{name}' wurde angelegt.", data=player)

	def _create_bettor(self, cmd: CreateBettor):
		name = cmd.name.strip()

		if not name:
			return Error("invalid_name", "Name darf nicht leer sein.")

		if self.bettor_repo.exists_by_name(name):
			return Error("duplicate_bettor", f"Tipper '{name}' existiert bereits.")

		bettor = Bettor(name=name)
		self.bettor_repo.add(bettor)

		return Ok(message=f"Tipper '{name}' wurde angelegt.", data=bettor)
	def _create_match(self, cmd: CreateMatch):
		p11 = cmd.team1_players[0]
		p12 = cmd.team1_players[1]
		p21 = cmd.team2_players[0]
		p22 = cmd.team2_players[1]
		p_11 = self.player_repo.get(p11)
		p_12 = self.player_repo.get(p12)
		p_21 = self.player_repo.get(p21)
		p_22 = self.player_repo.get(p22)
		if not all([p_11, p_12, p_21, p_22]):
			return Error("invalid_player_id", "Ein oder mehrere Spieler-IDs sind ungültig.")
		i = j = 0
		for pi in [p11, p12, p21, p22]:
			i += 1
			j = 0
			for pj in [p11, p12, p21, p22]:
				j += 1
				if i != j: 
					if pi == pj:
						return Error("duplicate_player_in_match", f"Spieler '{pi.name}' ist mehrfach im Match vertreten.")
		t1 = [p11, p12]
		t2 = [p21, p22]
		t_1 = [p_11, p_12]
		t_2 = [p_21, p_22]
		match = Match(team1_players=t1, team2_players=t2)
		self.match_repo.add(match)
		return Ok(message=f"Match zwischen {', '.join(p.name for p in t_1)} und {', '.join(p.name for p in t_2)} wurde angelegt.", data=match)
	def _save_snapshot(self, cmd: Save):
			full_path = self.saves_dir / cmd.name
			saver = JsonSnapshotStore(full_path)
			try:
				saver.save(
					player_repo=self.player_repo,
					bettor_repo=self.bettor_repo,
					match_repo=self.match_repo,
					bet_repo=self.bet_repo,
				)
				return Ok(message=f"Gespeichert nach: {full_path}")
			except Exception as e:
				return Error("snapshot_save_failed", str(e))

	def _load_snapshot(self, cmd: Load):
			
			full_path = self.saves_dir / cmd.name
			loader = JsonSnapshotStore(full_path)
			try:
				loader.load(
					player_repo=self.player_repo,
					bettor_repo=self.bettor_repo,
					match_repo=self.match_repo,
					bet_repo=self.bet_repo,
				)
				return Ok(message=f"Geladen von: {cmd.name}")
			except Exception as e:
				return Error("snapshot_load_failed", str(e))
	def _list_players(self):
		players = self.player_repo.liste()
		if not players:
			return Ok(message="Keine Spieler gefunden.", data=[])
		return PlayersListed(players=players)

	def _list_bettors(self):
		bettors = self.bettor_repo.liste()
		if not bettors:
			return Ok(message="Keine Tipper gefunden.", data=[])
		return BettorsListed(bettors=bettors)

	def _list_matches(self):
		matches = self.match_repo.liste()
		data = []
		for match in matches:
			liste = []
			liste.append (self.player_repo.get(match.team1[0]))
			liste.append (self.player_repo.get(match.team1[1]))
			liste.append (self.player_repo.get(match.team2[0]))
			liste.append (self.player_repo.get(match.team2[1]))
		data.append(liste)
		if not matches:
			return Ok(message="Keine Matches gefunden.", data=[])
		return MatchesListed(matches=matches, data = data)
	def _create_bet(self, cmd: Create_Bet):
		
		match = self.match_repo.get(cmd.match_id)
		if not match:
			return Error("invalid_match_id", "Ungültige Match-ID.")
		players = []
		players.append([])
		for p in match.team1:
			players[0].append(self.player_repo.get(p))
		players.append([])
		for p in match.team2:
			players[1].append(self.player_repo.get(p))
		bankroll_of_bank = self.bettor_repo.get_bank()
		quoata = calculate_quota(players=players, bankroll_of_bank=bankroll_of_bank, bet_type=cmd.bet_type, team=cmd.team, player=self.player_repo.get(cmd.player_id) if cmd.player_id else None, handicap=cmd.handicap)
		bet = Bet(bettor_id=cmd.bettor_id, match_id=cmd.match_id, amount=cmd.amount, bet_type=cmd.bet_type, team=cmd.team, player_id=cmd.player_id, handicap=cmd.handicap, quota=quoata)
		self.bet_repo.add(bet)
		return BetPlaced(bet=bet)

	def _end_match(self, cmd: 'EndMatch'):
		# select match
		if cmd.match_id is not None:
			match = self.match_repo.get(cmd.match_id)
			if not match:
				return Error("invalid_match_id", "Ungültige Match-ID.")
		else:
			matches = self.match_repo.liste()
			if not matches:
				return Error("no_matches", "Keine Matches vorhanden.")
			match = matches[-1]

		# set fields
		match.ended = True
		# winner passed as string "Team 1" / "Team 2" from parser
		match.winner = cmd.winner
		match.remaining = cmd.remaining
		match.deathcup = bool(cmd.deathcup)
		match.bitchcup = bool(cmd.bitchcup)
		match.nacktemeile_overall = bool(cmd.nacktemeile_overall)
		match.overtime = bool(cmd.overtime)
		match.deathcup_player = cmd.deathcup_player_id if cmd.deathcup else None
		match.bitchcup_player = cmd.bitchcup_player_id if cmd.bitchcup else None
		match.nacktemeile_player = cmd.nacktemeile_player_id if cmd.nacktemeile_overall else None
		# gather bets for this match and attach bettor/player objects so compute_payouts can use them
		bets = []
		bets = self.bet_repo.list_by_match(match.id)


		# compute payouts and apply to bettors in repo
		payouts = compute_payouts(match, bets)
		for bettor_id, payout in payouts.items():
			bettor = self.bettor_repo.get(bettor_id)
			if bettor:
				bettor.kontostand += payout
		return MatchEnded(match_id=match.id, payouts=payouts)

	def _quotas(self, cmd: Quotas):
		# Determine match: by id or latest
		if cmd.match_id is not None:
			match = self.match_repo.get(cmd.match_id)
			if not match:
				return Error("invalid_match_id", "Ungültige Match-ID.")
		else:
			matches = self.match_repo.liste()
			if not matches:
				return Error("no_matches", "Keine Matches vorhanden.")
			match = matches[-1]

		# build players matrix [[p1,p2],[p3,p4]]
		players = [[], []]
		for p in match.team1:
			players[0].append(self.player_repo.get(p))
		for p in match.team2:
			players[1].append(self.player_repo.get(p))

		bankroll_of_bank = self.bettor_repo.get_bank()
		quotas = []

		# Normal team bets
		try:
			q = calculate_quota(players=players, bet_type=BetType.NORMAL, bankroll_of_bank=bankroll_of_bank, team=Team.TEAM1)
		except Exception:
			q = None
		quotas.append(("NORMAL Team 1", q))
		try:
			q = calculate_quota(players=players, bet_type=BetType.NORMAL, bankroll_of_bank=bankroll_of_bank, team=Team.TEAM2)
		except Exception:
			q = None
		quotas.append(("NORMAL Team 2", q))

		# Handicap bets for both teams
		for h in [HandicapType.H1_5, HandicapType.H2_5, HandicapType.H3_5, HandicapType.H4_5]:
			for t, tname in ((Team.TEAM1, "Team 1"), (Team.TEAM2, "Team 2")):
				try:
					q = calculate_quota(players=players, bet_type=BetType.HANDICAP, bankroll_of_bank=bankroll_of_bank, team=t, handicap=h)
				except Exception:
					q = None
				quotas.append((f"HANDICAP {h.value} {tname}", q))

		# Deathcup, Bitchcup, Nacktemeile specific and overall
		for overall_type, specific_type, label in (
			(BetType.DEATHCUPOVERALL, BetType.DEATHCUPSPECIFIC, "DEATHCUP"),
			(BetType.BITCHCUPOVERALL, BetType.BITCHCUPSPECIFIC, "BITCHCUP"),
			(BetType.NACKTEMEILEOVERALL, BetType.NACKTEMEILESPECIFIC, "NACKTEMEILE"),
		):
			try:
				q = calculate_quota(players=players, bet_type=overall_type, bankroll_of_bank=bankroll_of_bank)
			except Exception:
				q = None
			quotas.append((f"{label} OVERALL", q))
			# specific for each player
			for side in (0, 1):
				for idx, p in enumerate(players[side]):
					if p is None:
						quotas.append((f"{label} SPEC Player {side+1}-{idx+1}", None))
						continue
					try:
						q = calculate_quota(players=players, bet_type=specific_type, bankroll_of_bank=bankroll_of_bank, player=p)
					except Exception:
						q = None
					quotas.append((f"{label} SPEC {p.name}", q))

		# Overtime
		try:
			q = calculate_quota(players=players, bet_type=BetType.OVERTIME, bankroll_of_bank=bankroll_of_bank)
		except Exception:
			q = None
		quotas.append(("OVERTIME", q))

		return QuotasListed(match=match, quotas=quotas)