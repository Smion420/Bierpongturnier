from dataclasses import dataclass
import string
from app.commands import CreatePlayer, CreateMatch, CreateBettor, ListPlayers, ListMatches, ListBettors, Load, Save, Create_Bet, Quotas, EndMatch
from domain.enums import BetType, Team, HandicapType


class AppController:
    def __init__(self, service):
        self.service = service
    
    def create_player(self, name:string, rating:string, amount_of_games:string):
        name = (name or "").strip()
        if not name:
            raise ValueError("Spielername darf nicht leer sein.")
        try:
            rating = int(rating)
        except ValueError:
            raise ValueError("Rating muss eine ganze Zahl sein.")
        try:
            amount_of_games = int(amount_of_games)
        except ValueError:
            raise ValueError("Anzahl der Spiele muss eine ganze Zahl sein.")
        return self.service._create_player(CreatePlayer(name=name, rating=rating, amount_of_games=amount_of_games))
    
    def create_bettor(self, name: str):
        name = (name or "").strip()
        if not name:
            raise ValueError("Bettor-Name darf nicht leer sein.")
        return self.service._create_bettor(CreateBettor(name=name))
    
    def create_match(self, p1_id:int, p2_id:int, p3_id:int, p4_id:int):
        return self.service._create_match(CreateMatch(team1_players=[p1_id, p2_id], team2_players=[p3_id, p4_id]))
    
    def list_players(self):
        return self.service._list_players()
    
    def list_bettors(self):
        return self.service._list_bettors()

    def list_matches(self):
        return self.service._list_matches()

    def place_bet(self, bettor_id:str, match_id:str, amount:str, bet_type:str, target:str, handicap: str | None = None):
        # Normalize and validate inputs
        try:
            bettor_id_val = int(bettor_id)
        except Exception:
            raise ValueError("Ungültige Bettor-ID")
        try:
            match_id_val = int(match_id)
        except Exception:
            raise ValueError("Ungültige Match-ID")
        try:
            amount_val = float(amount)
        except Exception:
            raise ValueError("Betrag muss eine Zahl sein")

        # bet_type can be provided as name or value
        bt = None
        for t in BetType:
            if bet_type == t.name or bet_type == t.value:
                bt = t
                break
        if bt is None:
            raise ValueError("Ungültiger Wetttyp")

        team = None
        player_id = None
        # target format: 'team:TEAM1' or 'player:<id>' or just id
        if isinstance(target, str) and target.startswith("team:"):
            val = target.split("team:",1)[1]
            if val == 'TEAM1':
                team = Team.TEAM1
            else:
                team = Team.TEAM2
        elif isinstance(target, str) and target.startswith("player:"):
            try:
                player_id = int(target.split("player:",1)[1])
            except Exception:
                player_id = None
        else:
            # try parse as int -> player id
            try:
                player_id = int(target)
            except Exception:
                player_id = None

        # parse handicap if provided
        hval = None
        if handicap:
            try:
                # try match by name
                for h in HandicapType:
                    if handicap == h.name or str(handicap) == str(h.value):
                        hval = h
                        break
                # try numeric match
                if hval is None:
                    hf = float(handicap)
                    for h in HandicapType:
                        if float(h.value) == hf:
                            hval = h
                            break
            except Exception:
                hval = None

        return self.service._create_bet(Create_Bet(bettor_id=bettor_id_val, match_id=match_id_val, amount=amount_val, bet_type=bt, team=team, player_id=player_id, handicap=hval))

    def quotas(self, match_id: str | None = None):
        # normalize match_id
        if match_id is None or match_id == "":
            mid = None
        else:
            try:
                mid = int(match_id)
            except Exception:
                raise ValueError("Ungültige Match-ID")
        return self.service._quotas(Quotas(match_id=mid))

    def end_match(self, match_id: str, winner: str, remaining: str, nacktemeile_player: str | None = None, deathcup_player: str | None = None, bitchcup_player: str | None = None, overtime: str | bool = False):
        # normalize match id and remaining
        try:
            match_id_val = int(match_id)
        except Exception:
            raise ValueError("Ungültige Match-ID")
        try:
            remaining_val = int(remaining) if remaining is not None and remaining != "" else 0
        except Exception:
            raise ValueError("Remaining muss eine ganze Zahl sein")

        # winner -> Team
        win = None
        for t in Team:
            if winner == t.name or winner == t.value or winner == str(t.name) or winner == str(t.value):
                win = t
                break
        if win is None:
            raise ValueError("Ungültiger Gewinner")

        # parse player ids
        def parse_pid(v):
            if v is None or v == "":
                return None
            try:
                return int(v)
            except Exception:
                return None

        nack_pid = parse_pid(nacktemeile_player)
        death_pid = parse_pid(deathcup_player)
        bitch_pid = parse_pid(bitchcup_player)

        # booleans: set True if player id provided
        nack_overall = bool(nack_pid)
        deathcup_flag = bool(death_pid)
        bitchcup_flag = bool(bitch_pid)

        # overtime parse
        ot = False
        if isinstance(overtime, bool):
            ot = overtime
        else:
            if str(overtime).lower() in ("1", "true", "ja", "yes"):
                ot = True

        return self.service._end_match(EndMatch(match_id=match_id_val, winner=win, remaining=remaining_val, deathcup=deathcup_flag, deathcup_player_id=death_pid, bitchcup=bitchcup_flag, bitchcup_player_id=bitch_pid, nacktemeile_overall=nack_overall, nacktemeile_player_id=nack_pid, overtime=ot))

    def save_snapshot(self, name: str):
        name = (name or "").strip()
        if not name:
            raise ValueError("Dateiname darf nicht leer sein.")
        return self.service._save_snapshot(Save(name=name))

    def load_snapshot(self, name: str):
        name = (name or "").strip()
        if not name:
            raise ValueError("Dateiname darf nicht leer sein.")
        return self.service._load_snapshot(Load(name=name))