from domain.match import Match

def match_to_dict(m: Match) -> dict:
    return {
        "id": getattr(m, "id", None),
        "team1": getattr(m, "team1", None),
        "team2": getattr(m, "team2", None),
        "bets": getattr(m, "bets", []),
        "ended": getattr(m, "ended", False),
        "winner": getattr(m, "winner", None),
        "remaining": getattr(m, "remaining", None),
        "deathcup": getattr(m, "deathcup", False),
        "deathcup_player": getattr(m, "deathcup_player", None),
        "bitchcup": getattr(m, "bitchcup", False),
        "bitchcup_player": getattr(m, "bitchcup_player", None),
        "nacktemeile_overall": getattr(m, "nacktemeile_overall", False),
        "nacktemeile_player": getattr(m, "nacktemeile_player", None),
        "overtime": getattr(m, "overtime", False),
    }

def match_from_dict(d: dict) -> Match:
    match = Match(
        team1_players=d.get("team1", []),
        team2_players=d.get("team2", []),
    )
    setattr(match, "id", d.get("id"))
    match.bets = d.get("bets", [])
    match.ended = d.get("ended", False)
    match.winner = d.get("winner")
    match.remaining = d.get("remaining")
    match.deathcup = d.get("deathcup", False)
    match.deathcup_player = d.get("deathcup_player")
    match.bitchcup = d.get("bitchcup", False)
    match.bitchcup_player = d.get("bitchcup_player")
    match.nacktemeile_overall = d.get("nacktemeile_overall", False)
    match.nacktemeile_player = d.get("nacktemeile_player")
    match.overtime = d.get("overtime", False)
    return match