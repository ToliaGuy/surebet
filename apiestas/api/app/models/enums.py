from enum import Enum


class Sport(str, Enum):
    SOCCER = "soccer"
    FOOTBALL = "football"
    TENNIS = "tennis"
    BASKETBALL = "basketball"
    HOCKEY = "hockey"
    ICE_HOCKEY = "ice-hockey"
    VOLLEYBALL = "volleyball"
    HANDBALL = "handball"
    BASEBALL = "baseball"
    AMERICAN_FOOTBALL = "american-football"
    RUGBY = "rugby"
    FUTSAL = "futsal"
    BADMINTON = "badminton"
    CRICKET = "cricket"
    SNOOKER = "snooker"
    DARTS = "darts"
    BOXING = "boxing"

class Bookmaker(str, Enum):
    THUNDER_PICK = "thunder-pick"
    N_ONE_BET = "n-1-bet"

