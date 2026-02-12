from adapters.player_repo_memory import PlayerRepositoryMemory
from adapters.bettor_repo_memory import BettorRepositoryMemory
from adapters.match_repo_memory import MatchRepositoryMemory
from adapters.bet_repo_memory import BetRepositoryMemory
from app.service import AppService
from ui_text.parser import parse_line
from app.results import Ok, Error, PlayersListed, MatchesListed, BettorsListed, BetPlaced, QuotasListed
from ui_text.renderer import render_result

def main():
    service = AppService(player_repo=PlayerRepositoryMemory(), match_repo = MatchRepositoryMemory(), bettor_repo = BettorRepositoryMemory(), bet_repo = BetRepositoryMemory())

    while True:
        line = input("> ")
        parsed = parse_line(line)

        if parsed is None:
            print("Unbekannter Befehl")
            continue

        if isinstance(parsed, tuple):
            kind, msg = parsed
            print(msg)
            continue

        result = service.handle(parsed)

        if isinstance(result, Ok):
            print(result.message)
        elif isinstance(result, Error):
            print(f"[{result.code}] {result.message}")
        elif isinstance(result, PlayersListed) or isinstance(result, MatchesListed) or isinstance(result, BettorsListed) or isinstance(result, BetPlaced) or isinstance(result, QuotasListed):
            render_result(result)
        else:
            print("Unerwartetes Ergebnis")

if __name__ == "__main__":
    main()