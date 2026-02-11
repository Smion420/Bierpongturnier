from app.commands import CreateMatch, CreatePlayer

def parse_line(line: str):
    parts = line.strip().split()
    if not parts:
        return None

    if parts[0] == "create_player":
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
    
    if parts[0] == "create_match":
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

    return None