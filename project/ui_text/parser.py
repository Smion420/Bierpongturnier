from app.commands import CreateMatch, CreatePlayer, CreateBettor, ListPlayers, ListMatches, ListBettors, Load, Save, Create_Bet
from app.commands import CreateMatch, CreatePlayer, CreateBettor, ListPlayers, ListMatches, ListBettors, Load, Save, Create_Bet, Quotas, EndMatch
from enum import Enum
from domain.enums import BetType, Team, HandicapType
class Commands (Enum):
    CREATE_PLAYER = 'create_player'
    CREATE_MATCH = "create_match"
    SAVE = "save"
    LOAD = "load"
    LIST_PLAYERS = "list_players"
    LIST_MATCHES = "list_matches"
    LIST_BETTORS = "list_bettors"
    PLACE_BET = "place_bet"
    CREATE_BETTOR = "create_bettor"
    QUOTAS = "quotas"
    END_MATCH = "end_match"

def parse_line(line: str):
    parts = line.strip().split()
    if not parts:
        return None
    cmd = parts[0].lower()
    if cmd == Commands.CREATE_PLAYER.value:
        if len(parts) != 4:
            return ("help", "Usage: create_player <name> <rating> <amount_of_games>")

        name = parts[1]
        try:
            rating = int(parts[2])
        except ValueError:
            return ("error", "rating muss eine Zahl sein")
        try:
            amount_of_games = int(parts[3])
        except ValueError:
            return ("error", "amount_of_games muss eine Zahl sein")

        return CreatePlayer(name=name, rating=rating, amount_of_games=amount_of_games)    
    if cmd == Commands.CREATE_MATCH.value:
        if len(parts) != 5:
            return ("help", "Usage: create_match <player1_team1_id> <player2_team1_id> <player1_team2_id> <player2_team2_id>")
        try:
            player1_team1_id = int(parts[1])
            player2_team1_id = int(parts[2])
            player1_team2_id = int(parts[3])
            player2_team2_id = int(parts[4])
        except ValueError:
            return ("error", "Alle Spieler-IDs müssen Zahlen sein.")
        
        return CreateMatch(team1_players=[player1_team1_id, player2_team1_id], team2_players=[player1_team2_id, player2_team2_id])
    if cmd == Commands.SAVE.value:

        if len(parts) != 2:
            return ("error", "Usage: save <filename>")

        return Save(name=parts[1])     
    if cmd == Commands.LOAD.value:

        if len(parts) != 2:
            return ("error", "Usage: load <filename>")

        return Load(name=parts[1])
    if cmd == Commands.LIST_PLAYERS.value:
        liste = ListPlayers()
        return liste
    if cmd == Commands.LIST_MATCHES.value:
        return ListMatches()
    if cmd == Commands.LIST_BETTORS.value:
        return ListBettors()
    if cmd == Commands.CREATE_BETTOR.value:
        if len(parts) != 2:
            return ("help", "Usage: create_bettor <name>")
        name = parts[1]
        return CreateBettor(name=name)
    if cmd == Commands.PLACE_BET.value:
        # Usage: place_bet <bettor_id> <match_id> <amount> <bet_type> [team|player_id] [details]
        if len(parts) < 5:
            return ("help", "Usage: place_bet <bettor_id> <match_id> <amount> <bet_type> [team|player_id] [details]")
        try:
            bettor_id = int(parts[1])
            match_id = int(parts[2])
            amount = float(parts[3])
        except ValueError:
            return ("error", "bettor_id and match_id must be integers, amount must be a number")

        bet_type_str = parts[4].lower()
        try:
            bet_type = next(bt for bt in BetType if bt.value == bet_type_str)
        except StopIteration:
            return ("error", f"Unknown bet_type: {parts[4]}")

        team = None
        player_id = None
        handicap = None

        if len(parts) >= 6:
            p5 = parts[5]
            # team can be 'team1' or 'team2' or 'Team 1'/'Team 2'
            if p5.lower().startswith("team") or p5 in ("Team 1", "Team 2"):
                if "1" in p5:
                    team = Team.TEAM1
                else:
                    team = Team.TEAM2
            else:
                try:
                    player_id = int(p5)
                except ValueError:
                    return ("error", "Fifth argument must be team or player_id (integer)")

        if len(parts) >= 7:
            p6 = parts[6]
            # handicap may be 1.5,2.5,3.5,4.5
            try:
                hval = float(p6)
                handicap = next(h for h in HandicapType if float(h.value) == hval)
            except ValueError:
                return ("error", "Handicap must be a number like 1.5")
            except StopIteration:
                return ("error", f"Unknown handicap: {p6}")

        return Create_Bet(bettor_id=bettor_id, match_id=match_id, amount=amount, bet_type=bet_type, team=team, player_id=player_id, handicap=handicap)
    
    if cmd == Commands.QUOTAS.value:
        # Usage: quotas [match_id]
        if len(parts) == 1:
            return Quotas()
        if len(parts) == 2:
            try:
                mid = int(parts[1])
            except ValueError:
                return ("error", "match_id must be an integer")
            return Quotas(match_id=mid)
        return ("help", "Usage: quotas [match_id]")
    if cmd == Commands.END_MATCH.value:
            # Usage: end_match [match_id] <winner: team1|team2> <remaining:int> <deathcup:true|false> <deathcup_player_id or 0> <bitchcup:true|false> <bitchcup_player_id or 0> <nacktemeile:true|false> <nacktemeile_player_id or 0> <overtime:true|false>
            parts_len = len(parts)
            # minimal without match_id: 10 parts (command + 9 args)
            if parts_len not in (10, 11):
                return ("help", "Usage: end_match [match_id] <winner:team1|team2> <remaining> <deathcup:true|false> <deathcup_player_id|0> <bitchcup:true|false> <bitchcup_player_id|0> <nacktemeile:true|false> <nacktemeile_player_id|0> <overtime:true|false>")

            idx = 1
            mid = None
            if parts_len == 11:
                try:
                    mid = int(parts[1])
                except ValueError:
                    return ("error", "match_id must be an integer")
                idx = 2

            # winner
            winner_raw = parts[idx].lower()
            if winner_raw in ("team1", "1"):
                winner = Team.TEAM1
            elif winner_raw in ("team2", "2"):
                winner = Team.TEAM2
            else:
                return ("error", "winner must be 'team1' or 'team2'")
            idx += 1

            try:
                remaining = int(parts[idx])
            except ValueError:
                return ("error", "remaining must be an integer")
            idx += 1

            def parse_bool(s: str):
                s2 = s.lower()
                if s2 in ("true", "1", "yes"):
                    return True
                if s2 in ("false", "0", "no"):
                    return False
                raise ValueError()

            try:
                deathcup = parse_bool(parts[idx]); idx += 1
                deathcup_player_id = int(parts[idx]); idx += 1
                bitchcup = parse_bool(parts[idx]); idx += 1
                bitchcup_player_id = int(parts[idx]); idx += 1
                nacktemeile_overall = parse_bool(parts[idx]); idx += 1
                nacktemeile_player_id = int(parts[idx]); idx += 1
                overtime = parse_bool(parts[idx])
            except ValueError:
                return ("error", "Bad argument types for end_match; check booleans and integers")

            # convert 0 => None for player ids
            if deathcup_player_id == 0:
                deathcup_player_id = None
            if bitchcup_player_id == 0:
                bitchcup_player_id = None
            if nacktemeile_player_id == 0:
                nacktemeile_player_id = None

            return EndMatch(match_id=mid, winner=winner, remaining=remaining, deathcup=deathcup, deathcup_player_id=deathcup_player_id, bitchcup=bitchcup, bitchcup_player_id=bitchcup_player_id, nacktemeile_overall=nacktemeile_overall, nacktemeile_player_id=nacktemeile_player_id, overtime=overtime)
    return None