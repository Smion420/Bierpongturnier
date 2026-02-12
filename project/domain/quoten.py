from math import sqrt, pi, exp
from typing import Optional, List
from domain.enums import BetType, HandicapType, Team
from domain.player import Player


#Es ist bisschen cursed, dass manche bases immer größer 1 sind und manche kleiner 1. Aber das kommt daher, dass sie teilweise als Quote und teilweise als Gewinnwahrschienlichkeit implementiert sind. 
se = 1500 #Start Elo
rd = 150 #Unsicherheit der Vorhersage, wäre bei ca 30, wenn es sehr sicher ist. Sehr unsicher zwischen 100 und 150\\
bank_bonus_lower = 1.15 #Untergrenze des dynamischen Bankvorteils\
bank_bonus_upper = 1.4 #Obergrenze des dynamischen Bankvorteils\
p0 = 0.9512 #0.5 Perzentil der Normalverteilung mit mittelwert = 2.14 und std = 0.99
p1 = 0.74101 #1.5 Perzentil
p2 = 0.35806 #2.5 Perzentil
p3 = 0.08476 #3.5 Perzentil
p4 = 0.00857 #4.5 Perzentil
avg_rating_diff_elo = 273 #Durchschnittlicher Ratingunterschied aller Teilnehmer, vor Start des Turniers berechnet, aus den cleanen elo Zahlen von der Webseite
deathcup_base = 25 #willkürlich gewählt
bitch_base = 0.078 #ist so gewählt, dass mit dem durchschnittlichen Unterschied 
    #(avg_rating_diff ist auch hier angegeben, aber es muss keine Abhängfigkeit bestehen, weil in der Formel für die Bitchcup berechnung eh damit normiert wird) 
    # zwischen beiden Spielern eines Teams die Quote für den overall bitchcup 3 ist. 
    #Diese wird über die Gegenwahrscheinlichkeiten der einzelnen berechnet
exp_red = 5 #Mehr oder weniger willkürlich, reduziert den Einfluss des Ratingunterschieds auf die Quote bei Bitchcup und Nackte. Je höher, desto niedriger der Einfluss
overtime_base = 4 #willkürlich gewählt
nackte_base = 0.0083 #ist so gewählt, dass ohne modifier für den ratingunterschied der beiden Spieler die Quote für den overall nackte 25 ist. Diese wird über die Gegenwahrscheinlichkeiten der einzelnen berechnet




def calculate_quota(players: list, bet_type: BetType, bankroll_of_bank: float, team: Optional[Team] = None, player: Optional[Player] = None,handicap: Optional[HandicapType] = None) -> float:
    avg_rating_diff = avg_rating_diff_elo/174 #normiert fr glicko 2
    # calculate dynamic bank bonus
    bank_bonus = bank_bonus_lower + (bank_bonus_upper - bank_bonus_lower) * min(1, max(0, (-bankroll_of_bank)/50))
    # helper to compute per-player RD factor (safe). Die 174 kommt aus der Glicko 2 Berechnung, ebenso die ganze Formel
    def _player_rd_factor(p: Player) -> float:
        try:
            rd_val = getattr(p, "rd", 0.0)
            rd_val = rd_val / 174 #174 kommt aus Glicko 2
            return 1.0 / (sqrt(1 + 3 * (rd_val ** 2) / pi ** 2 ))
        except Exception:
            return 0.0

    # Build g as a 2D list: [ [team1_factors...], [team2_factors...] ]
    g = [
        [_player_rd_factor(p) for p in players[0]],
        [_player_rd_factor(p) for p in players[1]],
    ]

    # Build a 2D list of ratings: [ [team1_ratings...], [team2_ratings...] ]
    ratings_2d: List[List[float]] = [
        [getattr(p, "rating", 0.0) for p in players[0]],
        [getattr(p, "rating", 0.0) for p in players[1]],
    ]
    # normaliesiere die ratings
    for i in range(2):
        for j in range(2):
            ratings_2d[i][j] = (ratings_2d[i][j] - se) / 174

    # Example: compute average rating per team (safe division)
    def avg(lst: List[float]) -> float:
        return sum(lst) / len(lst) if lst else 0.0

    # avg_g is the average of all player factors
    flat_g = [val for sub in g for val in sub]
    avg_g = avg(flat_g)
    avg_team1 = avg(ratings_2d[0])
    avg_team2 = avg(ratings_2d[1])
    '''
    Hier wird die Berechnung der Quote nach Glicko 2 Standard vorgenommen. Normalerweise wird hier einfach die Gewinnwahrscheinlichkeit umgekehrt. 
    Hier wird aber noch der Bankvorteil mit einberechnet, der dynamisch an die Bankroll angepasst wird.
    Außerdem geht noch ein Perzentil einer Normalverteilung mit ein. Das kommt daher, dass die Standardwette konstant zur Handicapwette sein soll. 
    Also die 0.5 Handicap Wette die gleiche Quote wie normal haben soll. Für das Handicap wird angenmmen, dass der Becherabstand normalverteilt ist mit Mittelwert 2.14 und Standardabweichung 0.99.
    Das ist eigentlich quatsch, da hier nicht mit eingeht, wer gewinnt. Also ist der handicap multiplayer für beide Teams immer gleich. 
    '''
    if bet_type == BetType.NORMAL or bet_type == BetType.HANDICAP:
        if team not in (Team.TEAM1, Team.TEAM2) or player is not None:
                raise ValueError("For NORMAL bets, specify team as 'team1' or 'team2' and no player.")
        opponent_avg = avg_team2 if team == Team.TEAM1 else avg_team1
        team_avg = avg_team1 if team == Team.TEAM1 else avg_team2
        base_quota = 1/(1+exp(-avg_g*(team_avg - opponent_avg)/exp_red))
        if bet_type == BetType.NORMAL:
            return 1 / (base_quota * bank_bonus * p0)
        if bet_type == BetType.HANDICAP:
            if handicap is None or handicap not in [HandicapType.H1_5, HandicapType.H2_5, HandicapType.H3_5, HandicapType.H4_5]:
                raise ValueError("For HANDICAP bets, details must be one of ['1.5','2.5','3.5','4.5'].")
            elif handicap == HandicapType.H1_5:
                return 1 / (base_quota * bank_bonus * p1)
            elif handicap == HandicapType.H2_5:
                return 1 / (base_quota * bank_bonus * p2)
            elif handicap == HandicapType.H3_5:
                return 1 / (base_quota * bank_bonus * p3)
            elif handicap == HandicapType.H4_5:
                return 1 / (base_quota * bank_bonus * p4)
            else:
                raise ValueError("Invalid handicap value. Must be one of [1.5, 2.5, 3.5, 4.5].")
    if bet_type in (BetType.DEATHCUPOVERALL, BetType.DEATHCUPSPECIFIC):
        if bet_type == BetType.DEATHCUPOVERALL:
            return deathcup_base / bank_bonus
    if bet_type in (BetType.BITCHCUPOVERALL, BetType.BITCHCUPSPECIFIC):
        '''
        Es werden zuerst die Quoten für alle individuellen Bitchcups berecnet. Hierfür wird prinzipiel 1/bitch_base genommen. Allerdings wird es noch um den Bankbonus geänder.
        Außerdem fließt die Ratingdifferenz der beiden Spieler eines Teams mit ein. Damit diese nicht zu extrem wird gibt es den bitch_exp_red
        '''
        bitchcup_quota = [[0.0 for _ in range(2)] for _ in range(2)]
        for i in range (2):
            for j in range (2):
                k = 0 if j == 1 else 1
                d = ratings_2d[i][j] - ratings_2d[i][k]
                bitchcup_quota[i][j] = 1/(bank_bonus * bitch_base * exp(((d) * avg(g[i])/avg_rating_diff +1 - avg(g[i])) / exp_red))
        if bet_type ==  BetType.BITCHCUPSPECIFIC:
            if player is None: 
                raise ValueError ("Es muss ein Spieler angegeben werden für Bitchcupspecificwette")
            if player == players[0][0]:
                return bitchcup_quota[0][0]
            elif player == players[0][1]:
                return bitchcup_quota[0][1]
            elif player == players[1][0]:
                return bitchcup_quota[1][0]
            elif player == players[1][1]:
                return bitchcup_quota[1][1]
            else:
                raise ValueError(f"Der Spieler {player.name} spielt nicht mit")
        if bet_type == BetType.BITCHCUPOVERALL:
            #Die logische Konsequenz, auf insgesamt zu wetten sollte die gleiche Quote haben, wie auf alle einzeln zu setzen. Das ist zwar nicht ganz richtig, weil ignoriert wird, dass ja auch 2 Bitchcups getroffen werden
            #können. Aber da wird entspannt drauf geschissen.
            return 1/(1 - ( 1- 1/bitchcup_quota[0][0]) * ( 1- 1/bitchcup_quota[0][1]) * ( 1- 1/bitchcup_quota[1][0]) * ( 1- 1/bitchcup_quota[1][1]))
    if bet_type == BetType.OVERTIME:
        #funktioniert sehr ähnlich wie die anderen. 
        return overtime_base * ((abs(avg_team1 - avg_team2)/(2*avg_rating_diff) + 1) * avg_g ** 2 + 1 - avg_g ** 2) / bank_bonus

    if bet_type in (BetType.NACKTEMEILEOVERALL, BetType.NACKTEMEILESPECIFIC):
        nackte_quota = [[0.0 for _ in range(2)] for _ in range(2)]
        for i in range (2):
            for j in range (2):
                k = 0 if i == 1 else 1
                d = ratings_2d[i][j] - avg(ratings_2d[k])
                nackte_quota[i][j] = 1/(bank_bonus * nackte_base * exp(((-d) * avg(g[i])/avg_rating_diff +1 - avg(g[i])) / exp_red))
        if bet_type ==  BetType.NACKTEMEILESPECIFIC:
            if player is None: 
                raise ValueError ("Es muss ein Spieler angegeben werden für Nackte Meile specificwette")
            if player == players[0][0]:
                return nackte_quota[0][0]
            elif player == players[0][1]:
                return nackte_quota[0][1]
            elif player == players[1][0]:
                return nackte_quota[1][0]
            elif player == players[1][1]:
                return nackte_quota[1][1]
            else:
                raise ValueError(f"Der Spieler {player.name} spielt nicht mit")
        if bet_type == BetType.NACKTEMEILEOVERALL:
            #Die logische Konsequenz, auf insgesamt zu wetten sollte die gleiche Quote haben, wie auf alle einzeln zu setzen. Ist falsch, da mehrere nackte Meilen möglich sind. Aber des ist per Design der nackten Meile
            # schon sehr unwahrscheinlich, daher wird drauf geschissen. 
            return 1/(1 - ( 1- 1/nackte_quota[0][0]) * ( 1- 1/nackte_quota[0][1]) * ( 1- 1/nackte_quota[1][0]) * ( 1- 1/nackte_quota[1][1]))