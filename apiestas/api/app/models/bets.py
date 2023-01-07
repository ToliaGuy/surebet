from typing import List, Optional
import datetime

from pydantic import Field

from .common import DateTimeModelMixin
from .rwmodel import RWModel


class Opportunity(RWModel):
    label: str = Field(..., example="Draw")
    odd: float = Field(..., example=1.8)


class BetBase(RWModel):
    bookmaker: str = Field(..., example="bet365")
    bookmaker_nice: str = Field(..., example="Bet365")
    bet_type: str = Field(..., example='1X2')
    bet_category: str = Field(..., example="1 X 2")
    bet_scope: str = Field(..., example='Full time')
    is_back: bool = Field(..., description="If the bet is back (True) or lay (False)")
    handicap: float = Field(description="Handicap of the bet (If applies)", default=0)
    url: Optional[str] = Field(None, example= "http://www.bet365.com/betslip/instantbet/...")
    commence_time: Optional[datetime.datetime] = None # to help prioritize betting opportunities
    opportunities: List[Opportunity] = Field(...,
                                            description="Odds are in the same order as teams. For 3 outcome sports, "
                                            "the 3rd item in the list is the draw odd."
                                            "We need to have additional information, "
                                            "other than the odds, to help us locate the exact betting opportunity.", min_items=2,
                                            )


class Bet(DateTimeModelMixin, BetBase):
    slug: str = Field(..., example="brighton-bournemouth-football-premier-league-bet365")


class BetInDB(Bet):
    feed: str


class BetInResponse(RWModel):
    bet: Bet


class BetFilterParams(RWModel):
    bookmaker: str


class ManyBetsInResponse(RWModel):
    bets: List[Bet]


class BetInUpsert(BetBase):
    feed: str








