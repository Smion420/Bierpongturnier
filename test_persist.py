from test import Player, Match, Bettor, save_state, load_state, BetType

# Setup
players = {
    "Alice": Player("Alice", 1200),
    "Bob": Player("Bob", 1100),
    "Carol": Player("Carol", 1000),
    "Dave": Player("Dave", 900),
}

match = Match([players["Alice"], players["Bob"]], [players["Carol"], players["Dave"]])
matches = [match]

bettor = Bettor("Eve")
bettor.kontostand = 100.0
bettor.place_bet(match, "Team 1", None, 10.0, BetType.NORMAL)

# End match with Team 1 winner
match.end_game({"winner": "Team 1", "cups_hit": 3}, match_id=0)

# Save
save_state("state_test.json", players, matches, {bettor.name: bettor})

# Load
loaded = load_state("state_test.json")
if isinstance(loaded, tuple) and len(loaded) == 4:
    players2, matches2, bettors2, _ = loaded
else:
    players2, matches2, bettors2 = loaded

print(len(players2), len(matches2), len(bettors2))
print(list(players2.keys()))
print([m.get_teams() for m in matches2])
print(list(bettors2.keys()))
