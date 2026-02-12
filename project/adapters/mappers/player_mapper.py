from domain.player import Player

def player_to_dict(p: Player) -> dict:
    return {
        "id": getattr(p, "id", None),
        "name": getattr(p, "name", None),
        "rating": getattr(p, "rating", None),
        "matchamount": getattr(p, "matchamount", None),
        "rd": getattr(p, "rd", None),
    }

def player_from_dict(d: dict) -> Player:
    player = Player(name=d.get("name"), rating=d.get("rating", 1500), matchamount=d.get("matchamount", 0))
    setattr(player, "id", d.get("id"))
    return player