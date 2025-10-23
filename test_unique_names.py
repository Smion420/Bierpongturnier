from main import Player, Bettor

# This simple test creates small in-memory players and bettors dicts and simulates the CLI checks
players = {}
bettors = {}

# simulate create_player
name = "Sam"
if name in players or name in bettors:
    print("Create player failed (already exists)")
else:
    players[name] = Player(name, 1000)
    print("Player created")

# simulate create_bettor with same name
name2 = "Sam"
if name2 in bettors or name2 in players:
    print("Create bettor failed (already exists)")
else:
    bettors[name2] = Bettor(name2)
    print("Bettor created")
