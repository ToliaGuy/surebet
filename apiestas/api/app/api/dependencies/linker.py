from typing import List, Optional

from ...models.enums import Sport
from ...models.linker import LinkerFilterParams


# for now the only filtering parameter is sport
def get_universal_linker_filters(
    sport: Optional[Sport] = None,
    bookmaker: Optional[str] = None,
    action_type: Optional[str] = None,
    tournament: Optional[str] = None,
    tournament_nice: Optional[str] = None,
    tournament_slug_id: Optional[str] = None,
    competitor_slug_id: Optional[str] = None,
    bookmaker_different_event_names: Optional[dict] = None,
    teams: Optional[List[str]] = None
) -> LinkerFilterParams:
    return LinkerFilterParams(
        sport=sport,
        bookmaker=bookmaker,
        action_type=action_type,
        tournament=tournament,
        tournament_nice=tournament_nice,
        tournament_slug_id=tournament_slug_id,
        competitor_slug_id=competitor_slug_id,
        bookmaker_different_event_names=bookmaker_different_event_names,
        teams=teams
        )
