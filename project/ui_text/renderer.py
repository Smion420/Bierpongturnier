from app.results import MatchEnded, PlayersListed, MatchesListed, BettorsListed, BetPlaced, QuotasListed


def render_result(result):
    if isinstance(result, PlayersListed):
        if not result.players:
            print("Keine Spieler gefunden.")
            return
        print(f"{len(result.players)} Spieler gefunden:")
        for player in result.players:
            print(f"- {player.name}   ID: {player.id}  Rating: {player.rating}   Matches: {player.matchamount}   RD: {player.rd:.2f}")
    elif isinstance(result, MatchesListed):
        if not result.matches:
            print("Keine Matches gefunden.")
            return
        print(f"{len(result.matches)} Matches gefunden:")
        for match in result.matches:
            team1_names = ", ".join([p.name for p in result.data[match.id - 1][0:2]])
            team2_names = ", ".join([p.name for p in result.data[match.id - 1][2:4]])
            status = "Beendet" if match.ended else "Läuft"
            print(f"- ID: {match.id}  Team 1: [{team1_names}] vs Team 2: [{team2_names}]  Status: {status}")
    elif isinstance(result, BettorsListed):
        if not result.bettors:
            print("Keine Tipper gefunden.")
            return
        print(f"{len(result.bettors)} Tipper gefunden:")
        for bettor in result.bettors:
            print(f"- ID: {bettor.id}  Name: {bettor.name}  Kontostand: {bettor.kontostand:.2f}")
    elif isinstance(result, BetPlaced):
        bet = result.bet
        if not bet:
            print("Wette konnte nicht erstellt werden.")
            return
        target = ""
        if getattr(bet, 'team', None):
            target = bet.team.value
        elif getattr(bet, 'player_id', None):
            target = f"Player ID {bet.player_id}"
        else:
            target = "(no specific target)"
        handicap = getattr(bet, 'handicap', None)
        handicap_str = f", Handicap: {handicap.value}" if handicap else ""
        quota = getattr(bet, 'quota', None)
        quota_str = f", Quote: {quota:.2f}" if quota is not None else ""
        print(f"Wette platziert: ID: {getattr(bet, 'id', None)} Bettor ID: {bet.bettor_id} Match ID: {bet.match_id} Amount: {bet.amount:.2f} Type: {bet.bet_type.value} Target: {target}{handicap_str}{quota_str}")
    elif isinstance(result, QuotasListed):
        match = result.match
        print(f"Quoten für Match ID: {getattr(match, 'id', None)}")
        for desc, q in result.quotas:
            if q is None:
                continue
            else:
                print(f"- {desc}: {q:.2f}")
    elif isinstance(result, MatchEnded):
        print(f"Match ID {result.match_id} beendet. Auszahlungen:")
        for bettor_id, payout in result.payouts.items():
            print(f"- Bettor ID {bettor_id}: Auszahlung {payout:.2f}")