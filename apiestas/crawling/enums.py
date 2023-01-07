from enum import Enum


class Spiders(str, Enum):
    OODS_PORTAL = "odds-portal"
    FORTUNE_JACK = "Fortune Jack"
    SPORT_BET_ONE = "SportBet One" # sportbet.one
    N_ONE_BET = "N1 Bet"
    THUNDER_PICK = "Thunder Pick" # thunderpick.com
    TRUSTDICE_WIN = "TrustDice Win" # trustdice.win
    DUELBITS = "Duelbits"


class Bookmakers(Enum):
    BET365 = "Bet365"
    BWIN = "Bwin"
    WILLIAM_HILL = "William Hill"
    INTERWETTEN = "Interwetten"
    MARCAAPUESTAS = "MARCA Apuestas"
    PAF = "Paf"
    BETFAIR = "Betfair"
    LUCKIA = "Luckia"
    SPORT888 = "888 Sport"
    SPORTIUM = "Sportium"
    CODERE = "Codere"
    MARATHON_BET = "Marathon Bet"
    BETWAY = "Betway"
    RETABET= "RETAbet"
    LEOVEGAS="LeoVegas"


class BetTypes(Enum):
    WINNER = 'Winner'
    _1X2 = '1X2'
    HOME_AWAY = 'Home/Away'
    AH = 'Asian Handicap'
    O_U = 'Over/Under'
    DNB = 'Draw No Bet'
    EH = 'European Handicap'
    DC = 'Double Chance'
    TQ = 'To Qualify'
    CS = 'Correct Score'
    HT_FT = 'Half Time / Full Time'
    O_E = 'Odd or Even'
    BTS = 'Both Teams to Score'