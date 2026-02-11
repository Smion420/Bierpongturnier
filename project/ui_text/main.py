from adapters.player_repo_memory import PlayerRepositoryMemory
from app.service import AppService
from ui_text.parser import parse_line
from app.results import Ok, Error

def main():
    service = AppService(player_repo=PlayerRepositoryMemory())

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
        else:
            print("Unerwartetes Ergebnis")

if __name__ == "__main__":
    main()