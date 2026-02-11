from typing import Enum

class BetType(Enum):
    NORMAL = "normal"
    HANDICAP = "handicap"
    DEATHCUPOVERALL = "deathcup_overall"
    DEATHCUPSPECIFIC = "deathcup_specific"
    BITCHCUPOVERALL = "bitchcup_overall"
    BITCHCUPSPECIFIC = "bitchcup_specific"
    NACKTEMEILEOVERALL = "nacktemeile_overall"
    NACKTEMEILESPECIFIC = "nacktemeile_specific"
    OVERTIME = "overtime"

class Team(Enum):
    TEAM1 = "Team 1"
    TEAM2 = "Team 2"

class HandicapType(Enum):
    H1_5 = 1.5
    H2_5 = 2.5
    H3_5 = 3.5
    H4_5 = 4.5