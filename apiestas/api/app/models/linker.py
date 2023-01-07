from typing import List, Optional, Union

from pydantic import Field

from .enums import Sport
from .rwmodel import RWModel
from .matches import Match


# I think that using slugified name instead of name is more
# convinient, there is less probability that I will write it
# wrong or there is some weird character, but I still
# should keep the name for visual reference

class UnmatchedEvent(RWModel):
    sport: Sport = Field(..., example="soccer")
    bookmaker: str = Field(..., example="thunder-pick")
    tournament: str = Field(..., example="premier-league") # slugified tournament extracted from bookmaker
    competitor: str = Field(..., example="liverpool") # tournament extracted from bookmaker
    competitor_nice: str = Field(..., example="Liverpool")
    label: str = Field(..., example="Liverpool - Manchester City")


class ManyUnmatchedEventsInResponse(RWModel):
    events: List[UnmatchedEvent]
    events_count: int

class MatchedEvent(RWModel):
    sport: Sport = Field(..., example="soccer")
    tournament_slug_id: str = Field(..., example="") # unified tournament, which has to be same for all bookmakers
    competitor_slug_id: str = Field(..., example="") # unified competitor, which has to be same for all bookmakers
    bookmaker_different_event_names: dict = Field(..., example="")

class ManyMatchedEventsInResponse(RWModel):
    events: List[MatchedEvent]
    events_count: int



# universal params
class LinkerFilterParams(RWModel):
    # for now only sport
    sport: Optional[Sport] = None
    bookmaker: Optional[str] = None
    action_type: Optional[str] = None
    tournament: Optional[str] = None
    tournament_nice: Optional[str] = None
    tournament_slug_id: Optional[str] = None
    competitor_slug_id: Optional[str] = None
    bookmaker_different_event_names: Optional[dict] = None
    teams: Optional[List[str]] = None

