from domain.bettor import Bettor

def bettor_to_dict(b: Bettor) -> dict:
    return {
        "id": getattr(b, "id", None),
        "name": getattr(b, "name", None),
        "kontostand": getattr(b, "kontostand", None),
    }

def bettor_from_dict(d: dict) -> Bettor:
    bettor = Bettor(name=d.get("name"))
    setattr(bettor, "id", d.get("id"))
    bettor.kontostand = d.get("kontostand", 0.0)
    return bettor