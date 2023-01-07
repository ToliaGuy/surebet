from fastapi import APIRouter, Depends, HTTPException
from starlette import status


from ...db.repositories.linker import UnmatchedEventsRepository, MatchedEventsRepository
from ...db.errors import EntityDoesNotExist, MatchedEventDeletionError, MatchedEventIngestionError
from ...api.dependencies.database import get_repository
from ...api.dependencies.linker import get_universal_linker_filters
from ...models.linker import LinkerFilterParams
from ...models.linker import (
    ManyUnmatchedEventsInResponse, ManyMatchedEventsInResponse, MatchedEvent
)


router = APIRouter()

@router.get(
    '/unmatched',
    response_model=ManyUnmatchedEventsInResponse,
    name="linker:list-unmatched-events"
)
# for now only sport filter, but I think I should include filter by tournament id and many other
async def list_unmatched_events(
    linker_filters: LinkerFilterParams = Depends(get_universal_linker_filters),
    un_matched_events_repo: UnmatchedEventsRepository = Depends(get_repository(UnmatchedEventsRepository))
) -> ManyUnmatchedEventsInResponse:
    competitors = await un_matched_events_repo.filter_competitors(sport=linker_filters.sport)
    # just for developmet purpose
    #await un_matched_competitors_repo.delete_all()
    return ManyUnmatchedEventsInResponse(events=competitors, events_count=len(competitors))



@router.get(
    '/matched',
    response_model=ManyMatchedEventsInResponse,
    name="linker:list-matched-events"
)
async def list_matched_events(
    linker_filters: LinkerFilterParams = Depends(get_universal_linker_filters),
    matched_events_repo: MatchedEventsRepository = Depends(get_repository(MatchedEventsRepository))
) -> ManyMatchedEventsInResponse:
    competitors = await matched_events_repo.filter_competitors(sport=linker_filters.sport)
    # just for developmet purpose
    #await matched_competitors_repo.delete_all()
    return ManyMatchedEventsInResponse(events=competitors, events_count=len(competitors))


# create matched competitors and add the data
@router.post(
    '/matched',
    response_model=MatchedEvent,
    name='linker:create-matched-event'
)
async def create_matched_events(
    linker_params: LinkerFilterParams,
    matched_events_repo: MatchedEventsRepository = Depends(get_repository(MatchedEventsRepository))
) -> MatchedEvent:
    try:
        competitor_link = await matched_events_repo.add_link(sport=linker_params.sport,
                                                              action_type=linker_params.action_type,
                                                              tournament_slug_id=linker_params.tournament_slug_id,
                                                              competitor_slug_id=linker_params.competitor_slug_id,
                                                              bookmaker_different_event_names=linker_params.bookmaker_different_event_names
                                                              )
        return competitor_link
    
    except MatchedEventIngestionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

@router.delete(
    '/matched',
    response_model=MatchedEvent,
    name="linker:delete-matched-events"
)

async def delete_matched_events(
    linker_params: LinkerFilterParams,
    matched_events_repo: MatchedEventsRepository = Depends(get_repository(MatchedEventsRepository))
) -> MatchedEvent:
    try:
        response = await matched_events_repo.delete_link(sport=linker_params.sport,
                                                        action_type=linker_params.action_type,
                                                        tournament_slug_id=linker_params.tournament_slug_id,
                                                        competitor_slug_id=linker_params.competitor_slug_id,
                                                        bookmaker_different_event_names=linker_params.bookmaker_different_event_names)
        return response

    except EntityDoesNotExist as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except MatchedEventDeletionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )