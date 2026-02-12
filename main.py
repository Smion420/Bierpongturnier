
import json
from typing import Dict, List, Tuple, Any, Optional
from project.domain.quoten import calculate_quota
from domain.sachen import Player, Match, Bettor, Bet, BetType, compute_payouts


# Stable incrementing id for matches (persisted)
NEXT_MATCH_ID = 0



def save_state(filename: str, players: Dict[str, Player], matches: List[Match], bettors: Dict[str, Bettor]):
    data = {
        "players": {name: p.to_dict() for name, p in players.items()},
        "matches": [m.to_dict(i) for i, m in enumerate(matches)],
        "bettors": {name: b.to_dict() for name, b in bettors.items()},
        "next_match_id": NEXT_MATCH_ID,
        "bank": Bettor.bank,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
def load_state(filename: str) -> Tuple[Dict[str, Player], List[Match], Dict[str, Bettor]]:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    players = {name: Player.from_dict(d) for name, d in data.get("players", {}).items()}
    # create matches with player references
    matches: List[Match] = [Match.from_dict(d, players) for d in data.get("matches", [])]
    bettors = {name: Bettor.from_dict(d) for name, d in data.get("bettors", {}).items()}

    # reconstruct bets stored inside matches and bettors
    for mi, mdata in enumerate(data.get("matches", [])):
        match_obj = matches[mi]
        for bdict in mdata.get("bets", []):
            bet_obj = Bet.from_dict(calculate_quota, bdict, match_obj, players, bettors)
            match_obj.bets.append(bet_obj)
            # attach bet to bettor
            if bet_obj.bettor:
                bet_obj.bettor.bets.append(bet_obj)

    # restore next match id if present
    next_id = data.get("next_match_id")
    # Recompute bank as the negative sum of all bettors' kontostand (bank holds opposite of bettors)
    try:
        Bettor.bank = -sum(b.kontostand for b in bettors.values())
    except Exception:
        Bettor.bank = 0.0
    return players, matches, bettors, next_id
def prompt_results_for_match(match: Match, players) -> Dict[str, Any]:
    """Interactive helper: prompt the user for winner, score and special events and return a results dict."""
    # Winner
    # accept 'cancel' at any prompt to abort
    def prompt_player(prompt_msg: str) -> Optional[str]:
        """Prompt for a player name that must be in the match. Return the name or None if canceled."""
        while True:
            val = input(prompt_msg).strip()
            if not val:
                print("Empty input, please enter a value or 'cancel' to skip.")
                continue
            if val.lower() == "cancel":
                return None
            # Check if it's a team indicator
            low = val.replace(" ", "").lower()
            if low in ("1", "team1", "teamone") or low in ("2", "team2", "teamtwo"):
                return val
            # check player name in this match
            match_players = [p.name for p in match.team1 + match.team2]
            if val in match_players:
                return val
            print(f"Player '{val}' is not in this match. Enter a player from: {match_players}, or type 'cancel'.")

    winner_input = prompt_player("Who won? (Team 1 / Team 2 or player name) [type 'cancel' to abort]: ")
    if winner_input is None:
        raise ValueError("No winner provided")
    if winner_input in players:
        p = players[winner_input]
        winner = "Team 1" if p in match.team1 else "Team 2"
    else:
        low = winner_input.replace(" ", "").lower()
        if low in ("1", "team1", "teamone"):
            winner = "Team 1"
        elif low in ("2", "team2", "teamtwo"):
            winner = "Team 2"
        else:
            winner = winner_input
    
    while True:
        val = input(f"How many cups stood before the losing team at the end?: ").strip()
        try:
            remaining = int(val)
            break
        except Exception:
            print("Please enter a valid integer or leave blank for 0.")
    results: Dict[str, Any] = {"winner": winner, "remaining": remaining}
    

    # Special events
    for evt, player_key in (("bitchcup", "bitchcup_player"), ("deathcup", "deathcup_player"), ("nacktemeile", "nacktemeile_player")):
        yn = input(f"Was there a {evt}? (y/n): ").strip().lower()
        if yn in ("y", "yes"):
            results[evt] = True
            who = prompt_player(f"Who hit the {evt}? (enter player name) [or 'cancel' to leave blank]: ")
            if who:
                # If user typed a team indicator, don't store it as player
                if who.replace(" ", "").lower() in ("1", "team1", "teamone", "2", "team2", "teamtwo"):
                    print("Entered a team instead of a player; ignoring player field.")
                else:
                    results[player_key] = who
        else:
            results[evt] = False

    yn = input("Was there overtime? (y/n): ").strip().lower()
    results["overtime"] = True if yn in ("y", "yes") else False
    return results



def main():
    players = {}
    dirty = False  # tracks whether there are unsaved changes

    print("Griasdi bei der ersten Wal Bierpongliga!")
    print("Type 'help' for a list of commands.")

    while True:
        cmd = input("> ").strip().lower()
        if cmd == "exit":
            # If there are unsaved changes, prompt the user to save/exit/cancel
            if dirty:
                resp = input("You have unsaved changes. Save before exiting? (y = save & exit, n = exit without saving, c = cancel) ").strip().lower()
                if resp == "y":
                    filename = input("Filename to save to: ").strip()
                    try:
                        save_state(filename, players, matches, Bettor.bettors)
                        print(f"State saved to {filename}.")
                        dirty = False
                        print("Bfiati!")
                        break
                    except Exception as e:
                        print(f"Failed to save state: {e}")
                        # continue the loop instead of exiting so user can try again
                        continue
                elif resp == "n":
                    print("Bfiati!")
                    break
                else:
                    print("Exit canceled.")
                    continue
            else:
                print("Bfiati!")
                break
        elif cmd == "help":
            print("Commands:")
            print("  create_player <name>")
            print("  create_bettor <name>")
            print("  create_match <player1> <player2> <player3> <player4>")
            print("  place_bet <bettor> <match_id> <amount> <bet_type> [team/player] [details]")
            print("  end_match <match_id> <winner> [special_results]")
            print("  show_bets [match_id]    # show bets for a match (defaults to last)")
            print("  list_bettors")
            print("  players")
            print("  list_matches")
            print("  save <filename>")
            print("  load <filename>")
            print("  exit")
        elif cmd.startswith("create_player"):
            parts = cmd.split()
            if len(parts) < 4 or not parts[1]:
                print("Player name cannot be empty. Usage: create_player <name> <rating> <amount_of_matches>")
                continue
            name = parts[1]
            if any(p.name == name for p in Player.all_players):
                print(f"Name '{name}' is already in use. Choose a different name.")
                continue
            # Prompt for rating if not provided

            rating_input = parts[2]
            amount_of_matches_input = parts[3]
            try:
                rating = float(rating_input)
                amount_of_matches = int(amount_of_matches_input)    

            except ValueError:
                print("Invalid rating. Please enter a number.")
                continue
            players[name] = Player(name, rating, amount_of_matches)
            dirty = True
            print(f"Player '{name}' created with rating {rating}.")
        elif cmd.startswith("create_bettor"):
            parts = cmd.split()
            if len(parts) < 2:
                print("Usage: create_bettor <name>")
                continue
            name = parts[1]
            # Enforce unique names
            if any(p.name == name for p in Bettor.bettors.values()):
                print(f"Name '{name}' is already in use. Choose a different name.")
                continue
            Bettor.bettors[name] = Bettor(name)
            dirty = True
            print(f"Bettor '{name}' created.")
        elif cmd.startswith("create_match"):
            parts = cmd.split()
            if len(parts) != 5:
                print("Usage: create_match <player1> <player2> <player3> <player4>")
                continue
            _, p1, p2, p3, p4 = parts
            try:
                match = Match([players[p1], players[p2]], [players[p3], players[p4]])
            except Exception as e:
                print(f"{e} ist noch nicht als Spieler registriert")
                continue
            # assign a stable id
            global NEXT_MATCH_ID
            match.id = NEXT_MATCH_ID
            NEXT_MATCH_ID += 1
            matches.append(match)
            dirty = True
            print(f"Match {len(matches)-1} created.")
        elif cmd.startswith("place_bet"):
            parts = cmd.split()
            if len(parts) < 5:
                print("Usage: place_bet <bettor> <match_id> <amount> <bet_type> [team/player] [details]")
                continue
            try:
                bettor_name = parts[1]
                match_id = int(parts[2])
                amount = float(parts[3])
                bet_type = parts[4]
            except Exception:
                print("Invalid arguments. Usage: place_bet <bettor> <match_id> <amount> <bet_type> [team/player] [details]")
                continue
            team_or_player = parts[5] if len(parts) > 5 else None
            details = None
            if len(parts) > 6:
                try:
                    details = json.loads(parts[6])
                except Exception:
                    # fallback to eval for convenience, but warn
                    try:
                        details = eval(parts[6])
                    except Exception:
                        details = None
            bettor = Bettor.bettors.get(bettor_name)
            if bettor is None:
                print(f"Unknown bettor '{bettor_name}'.")
                continue
            if match_id < 0 or match_id >= len(matches):
                print(f"Unknown match id {match_id}.")
                continue
            match = matches[match_id]
            # determine if team_or_player names a team or a player
            player_obj = None
            team_name = None
            if team_or_player:
                if team_or_player in players:
                    player_obj = players[team_or_player]
                else:

                    if team_or_player.lower() in ("1", "team1"):
                        team_name = "Team 1"
                    elif team_or_player.lower() in ("2", "team2"):
                        team_name = "Team 2"
                    else:
                        print(f"Unknown player or team '{team_or_player}'. Must be a player name or 'Team1'/'Team2'.")
                        continue
            try:
                # try by name lookup first, then by enum name
                try:
                    bet_type_enum = BetType[bet_type.upper()]
                except KeyError:
                    bet_type_enum = BetType(bet_type)
            except Exception:
                print(f"Unknown bet type '{bet_type}'.")
                continue
            try:
                bettor.place_bet(calculate_quota, match, team_name, player_obj, amount, bet_type_enum, details)
            except Exception as e:
                print(f"Failed to place bet: {e}")
                continue
            dirty = True
            # Retrieve the bet just placed for nicer output
            bet = bettor.bets[-1] if bettor.bets else None
            if bet:
                target = bet.player.name if bet.player else (bet.team if bet.team else "(no target)")
                print(f"Bet placed by {bettor_name} on match {match_id}: amount={bet.amount}, type={bet.bet_type.value} {bet.details if bet.details else None}, target={target}, quota={bet.quota}")
            else:
                print(f"Bet placed by {bettor_name} on match {match_id}.")
        elif cmd.startswith("end_match"):
            parts = cmd.split()
            # Determine match id: use provided one if numeric, otherwise default to last match
            if len(matches) == 0:
                print("No matches to end.")
                continue
            match_id = None
            if len(parts) >= 2:
                try:
                    match_id = int(parts[1])
                except Exception:
                    match_id = None
            if match_id is None:
                match_id = len(matches) - 1

            if match_id < 0 or match_id >= len(matches):
                print(f"Unknown match id {match_id}.")
                continue

            match = matches[match_id]

            # refuse to re-end an already ended match
            if match.ended:
                print(f"Match {match_id} has already been ended. Use 'edit_match {match_id}' to change results.")
                continue
            try:
                results = prompt_results_for_match(match, players)
            except ValueError:
                print("Aborted ending match.")
                continue
            match.end_game(results, match_id=match_id)
            dirty = True
            print(f"Match {match_id} ended.")
        elif cmd.startswith("change_match"):
            # Show last 5 matches and ask which to change
            if len(matches) == 0:
                print("No matches available to change.")
                continue
            print("Last matches:")
            for i in range(max(0, len(matches)-5), len(matches)):
                m = matches[i]
                print(f"{i}: {m.get_teams()} Ended={m.ended} Winner={m.winner if m.winner else 'N/A'}")
            try:
                mid = int(input("Enter match id to change: ").strip())
            except Exception:
                print("Invalid match id input.")
                continue
            if mid < 0 or mid >= len(matches):
                print("Unknown match id.")
                continue
            match = matches[mid]
            if not match.ended or not match.winner:
                print("That match has no results to change. Use end_match to end it first.")
                continue
            # display previous results
            print("Previous results:")
            # show current stored attributes
            prev = {
                "winner": match.winner,
                "remaining": match.remaining,
                "deathcup": match.deathcup,
                "deathcup_player": match.deathcup_player,
                "bitchcup": match.bitchcup,
                "bitchcup_player": match.bitchcup_player,
                "nacktemeile_overall": match.nacktemeile_overall,
                "nacktemeile_player": match.nacktemeile_player,
                "overtime": match.overtime,
                "cups_by_player": match.cups_by_player,
                "cups_hit": match.cups_hit,
            }
            print(json.dumps(prev, indent=2))

            # Reverse previous payouts and player stats
            prev_payouts = compute_payouts(match)
            # subtract payouts
            for bettor_name, amount in prev_payouts.items():
                bt = Bettor.bettors.get(bettor_name)
                if bt:
                    bt.kontostand -= amount
                    # bank receives the amount back when reversal
                    Bettor.bank += amount
            # reverse player wins/losses and cups
            prev_results = prev
            for player in match.team1 + match.team2:
                # remove last match_history entry for this match id if it matches
                # match id in records are the index mid
                for irec in range(len(player.match_history)-1, -1, -1):
                    rec = player.match_history[irec]
                    if rec.get("match_id") == mid:
                        # determine previous result either from stored results (legacy) or from match object
                        prev_winner = None
                        prev_cups_by_player = None
                        prev_cups_hit = None
                        if rec.get("results"):
                            prev_winner = rec.get("results", {}).get("winner")
                            prev_cups_by_player = rec.get("results", {}).get("cups_by_player")
                            prev_cups_hit = rec.get("results", {}).get("cups_hit", 0)
                        else:
                            # try to resolve from the match object
                            try:
                                prev_match = matches[int(mid)]
                                prev_winner = prev_match.winner
                                prev_cups_by_player = prev_match.cups_by_player
                                prev_cups_hit = prev_match.cups_hit
                            except Exception:
                                pass
                        # reverse wins/losses
                        if prev_winner == ("Team 1" if player in match.team1 else "Team 2"):
                            player.wins = max(0, player.wins-1)
                        else:
                            player.losses = max(0, player.losses-1)
                        # reverse cups
                        cbp = prev_cups_by_player
                        if cbp and isinstance(cbp, dict):
                            try:
                                player.cups_hit -= int(cbp.get(player.name, 0))
                            except Exception:
                                pass
                        else:
                            try:
                                player.cups_hit -= int(prev_cups_hit or 0)
                            except Exception:
                                pass
                        # remove the history record
                        player.match_history.pop(irec)
                        break

            # Now prompt for new results and reapply
            try:
                new_results = prompt_results_for_match(match, players)
            except ValueError:
                print("Aborted change.")
                continue
            # zero out old results and set ended True (already ended) then set new results
            # reset per-match attributes
            match.winner = None
            match.remaining = None
            match.deathcup = False
            match.deathcup_player = None
            match.bitchcup = False
            match.bitchcup_player = None
            match.nacktemeile_overall = False
            match.nacktemeile_player = None
            match.overtime = False
            match.cups_by_player = None
            match.cups_hit = None
            # now set new attributes from the interactive result and compute payouts
            if new_results:
                match.winner = new_results.get("winner")
                match.remaining = new_results.get("remaining")
                match.deathcup = new_results.get("deathcup", False)
                match.deathcup_player = new_results.get("deathcup_player")
                match.bitchcup = new_results.get("bitchcup", False)
                match.bitchcup_player = new_results.get("bitchcup_player")
                match.nacktemeile_overall = new_results.get("nacktemeile_overall", False)
                match.nacktemeile_player = new_results.get("nacktemeile_player")
                match.overtime = new_results.get("overtime", False)
                match.cups_by_player = new_results.get("cups_by_player")
                match.cups_hit = new_results.get("cups_hit")
            new_payouts = compute_payouts(match)
            for bettor_name, amount in new_payouts.items():
                bt = Bettor.bettors.get(bettor_name)
                if bt:
                    bt.kontostand += amount
                    # bank pays out the new amount
                    Bettor.bank -= amount
                    # update bettor bet list? we keep bets as-is

            # record match in player histories and update wins/losses/cups
            for player in match.team1 + match.team2:
                # append only match id to player history; details can be resolved from match attributes
                try:
                    player.match_history.append({"match_id": mid})
                except Exception:
                    # if player object lacks match_history, create it
                    player.match_history = [{"match_id": mid}]
            dirty = True
            print(f"Match {mid} changed.")
        elif cmd.startswith("save"):
            parts = cmd.split()
            if len(parts) < 2:
                print("Usage: save <filename>")
                continue
            filename = parts[1]
            try:
                save_state(filename, players, matches, Bettor.bettors)
                dirty = False
                print(f"State saved to {filename}.")
            except Exception as e:
                print(f"Failed to save state: {e}")
        elif cmd.startswith("load"):
            parts = cmd.split()
            if len(parts) < 2:
                print("Usage: load <filename>")
                continue
            filename = parts[1]
            try:
                loaded = load_state(filename)
                # load_state now returns (players, matches, bettors, next_match_id)
                if isinstance(loaded, tuple) and len(loaded) == 4:
                    players, matches, Bettor.bettors, next_id = loaded
                    if next_id is not None:
                        NEXT_MATCH_ID = next_id
                else:
                    players, matches, Bettor.bettors = loaded
                dirty = False
                print(f"State loaded from {filename}.")
            except Exception as e:
                print(f"Failed to load state: {e}")
        elif cmd.startswith("players"):
            parts = cmd.split()
            n = None
            if len(parts) >= 2:
                try:
                    n = int(parts[1])
                except Exception:
                    print("Invalid number for players. Usage: players [n]")
                    continue

            # If n is provided, compute stats from the first n matches for each player with different partners
            if n is not None:
                for name, player in players.items():
                    wins = 0
                    losses = 0
                    cups = 0
                    seen_partners = set()
                    selected_recs = []
                    for rec in player.match_history:
                        mid = rec.get("match_id")
                        if mid is None:
                            continue
                        try:
                            mid_i = int(mid)
                        except Exception:
                            continue
                        if mid_i < 0 or mid_i >= len(matches):
                            continue
                        match = matches[mid_i]
                        # find partner
                        if player in match.team1:
                            partner = match.team1[0] if match.team1[1] == player else match.team1[1]
                        else:
                            partner = match.team2[0] if match.team2[1] == player else match.team2[1]
                        if partner.name not in seen_partners:
                            selected_recs.append(rec)
                            seen_partners.add(partner.name)
                            if len(selected_recs) == n:
                                break
                    # Now compute stats from selected_recs
                    for rec in selected_recs:
                        mid = rec.get("match_id")
                        match = matches[int(mid)]
                        winner = match.winner
                        # determine team for player
                        team = "Team 1" if player in match.team1 else "Team 2"
                        if winner == team:
                            wins += 1
                        else:
                            losses += 1
                        # add per-player cups if present
                        cbp = match.cups_by_player
                        if isinstance(cbp, dict):
                            try:
                                cups += int(cbp.get(player.name, 0))
                            except Exception:
                                pass
                        else:
                            try:
                                cups += int(match.cups_hit or 0)
                            except Exception:
                                pass
                    print(f"{name}: Wins={wins}, Losses={losses}, Cups Hit={cups} (first {n} matches with different partners for this player)")
            else:
                for name, player in players.items():
                    print(f"{name}: Wins={player.wins}, Losses={player.losses}, Cups Hit={player.cups_hit}, RD = {round(player.rd)}")
        elif cmd == "bettors":
            for name, bettor in Bettor.bettors.items():
                print(f"{name}: {round(bettor.kontostand, 2)}")
        elif cmd == "matches":
            for i, match in enumerate(matches):
                print(f"Match {i}: {match.get_teams()} Ended={match.ended} Winner = {match.winner if match.winner else 'N/A'} remaining cups = {match.remaining if match.remaining is not None else 'N/A'}")
        elif cmd.startswith("bets"):
            parts = cmd.split()
            if len(matches) == 0:
                print("No matches available.")
                continue
            match_id = None
            if len(parts) >= 2:
                try:
                    match_id = int(parts[1])
                except Exception:
                    match_id = None
            if match_id is None:
                match_id = len(matches) - 1
            if match_id < 0 or match_id >= len(matches):
                print(f"Unknown match id {match_id}.")
                continue
            match = matches[match_id]
            print(f"Bets for match {match_id}: {match.get_teams()}")
            if not match.bets:
                print("  No bets placed on this match.")
                continue
            for bi, bet in enumerate(match.bets):
                bettor_name = bet.bettor.name if bet.bettor else "(unknown)"
                target = bet.player.name if bet.player else (bet.team if bet.team else "(no target)")
                print(f"  [{bi}] Bettor={bettor_name}, amount={bet.amount}, type={bet.bet_type.value}, target={target}, quota={bet.quota}, details={bet.details}")
        elif cmd.startswith("quotes") or cmd.startswith("show_quotas"):
            parts = cmd.split()
            if len(matches) == 0:
                print("No matches available.")
                continue
            match_id = None
            if len(parts) >= 2:
                try:
                    match_id = int(parts[1])
                except Exception:
                    match_id = None
            if match_id is None:
                match_id = len(matches) - 1
            if match_id < 0 or match_id >= len(matches):
                print(f"Unknown match id {match_id}.")
                continue
            match = matches[match_id]
            teams = match.get_teams()
            t1_names = ", ".join(teams.get("Team 1", []))
            t2_names = ", ".join(teams.get("Team 2", []))
            print(f"Quoten für Match {match_id}: {t1_names}  vs  {t2_names}")

            # use the centralized bank value (opposite of sum of bettors' money)
            bankroll = Bettor.bank

            def safe_quota(fn, *args, **kwargs):
                try:
                    return float(fn(*args, **kwargs))
                except Exception as e:
                    return None

            # NORMAL
            q_t1 = safe_quota(calculate_quota, match, BetType.NORMAL, "Team 1", None, None, bankroll)
            q_t2 = safe_quota(calculate_quota, match, BetType.NORMAL, "Team 2", None, None, bankroll)
            print("\nStandardwetten:")
            print(f"  Team 1 ({t1_names}): {round(q_t1,2) if q_t1 is not None else 'N/A'}")
            print(f"  Team 2 ({t2_names}): {round(q_t2,2) if q_t2 is not None else 'N/A'}")

            # HANDICAP variants
            handicaps = [1.5, 2.5, 3.5]
            print("\nHandicap-Quoten (je Team, pro Handicap):")
            for h in handicaps:
                h_q_t1 = safe_quota(calculate_quota, match, BetType.HANDICAP, "Team 1", None, h, bankroll)
                h_q_t2 = safe_quota(calculate_quota, match, BetType.HANDICAP, "Team 2", None, h, bankroll)
                print(f"  Handicap {h}: Team1: {round(h_q_t1,2) if h_q_t1 is not None else 'N/A'}   Team2: {round(h_q_t2,2) if h_q_t2 is not None else 'N/A'}")

            # Deathcup
            q_death_overall = safe_quota(calculate_quota, match, BetType.DEATHCUPOVERALL, None, None, None, bankroll)
            print("\nDeathcup:")
            print(f"  Overall: {round(q_death_overall,2) if q_death_overall is not None else 'N/A'}")
            '''
            print("  Specific per player:")
            for p in match.team1 + match.team2:
                q_p = safe_quota(calculate_quota, match, BetType.DEATHCUPSPECIFIC, None, None, p, bankroll)
                print(f"    {p.name}: {round(q_p,2) if q_p is not None else 'N/A'}")
            '''
            # Bitchcup
            q_bitch_overall = safe_quota(calculate_quota, match, BetType.BITCHCUPOVERALL, None, None, None, bankroll)
            print("\nBitchcup:")
            print(f"  Overall: {round(q_bitch_overall,2) if q_bitch_overall is not None else 'N/A'}")
            print("  Specific per player:")
            for p in match.team1 + match.team2:
                q_p = safe_quota(calculate_quota, match, BetType.BITCHCUPSPECIFIC, None, p, None, bankroll)
                print(f"    {p.name}: {round(q_p,2) if q_p is not None else 'N/A'}")

            # Nacktemeile
            q_nack_overall = safe_quota(calculate_quota, match, BetType.NACKTEMEILEOVERALL, None, None, None, bankroll)
            print("\nNackte Meile:")
            print(f"  Overall: {round(q_nack_overall,2) if q_nack_overall is not None else 'N/A'}")
            print("  Specific per player:")
            for p in match.team1 + match.team2:
                q_p = safe_quota(calculate_quota, match, BetType.NACKTEMEILESPECIFIC, None, p, None, bankroll)
                print(f"    {p.name}: {round(q_p,2) if q_p is not None else 'N/A'}")

            # Overtime
            q_ot = safe_quota(calculate_quota, match, BetType.OVERTIME, None, None, None, bankroll)
            print("\nOvertime:")
            print(f"  {round(q_ot,2) if q_ot is not None else 'N/A'}")
        elif cmd.startswith("bank"):
            print (f"Bank: {round(Bettor.bank,2)}")
        else:
            print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
    
