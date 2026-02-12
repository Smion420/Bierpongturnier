from typing import Optional

class Player:
    id: Optional[int] = None
    def __init__(self, *,name: str, rating: int = 1500, matchamount: int = 0):
        self.name = name
        self.rating = rating
        self.matchamount = matchamount
        self.rd = 5000/(self.matchamount + 25) 





