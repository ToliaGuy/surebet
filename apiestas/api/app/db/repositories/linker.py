

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Union
from slugify import slugify

from ...db.errors import EntityDoesNotExist, MatchedEventIngestionError, MatchedEventDeletionError
from ...db.repositories.base import BaseRepository
from ...core.config import COLLECTION_NAME_UNMATCHED_EVENTS, COLLECTION_NAME_MATCHED_EVENTS
from ...models.matches import MatchInUpsert
from ...models.linker import MatchedEvent, UnmatchedEvent
from ...models.enums import Sport



#await self.client.delete_many({})            

class UnmatchedEventsRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client[COLLECTION_NAME_UNMATCHED_EVENTS]

    async def filter_competitors(self, sport: Sport = None) -> List[UnmatchedEvent]:
        query = {}
        if sport:
            query["sport"] = sport.value
        competitors_docs = self.client.find(query)
        return [UnmatchedEvent(**competitor) async for competitor in competitors_docs]
    
    async def insert_if_not_exists(self, match: MatchInUpsert, tournament_slug_id: Optional[str] = "") -> None:
        """get slug id of matched tournament
        example of matched competitor:
        {
            "sport": "soccer",
            "bookmaker": "thunder-pick", 
            "tournament": "premiere-league", // match.tournament
            "competitor": "liverpool", // slugify(match.team[x])
            "competitor_nice": "Liverpool", // match.team[x]
            "label": "Liverpool - Manchester City"
    }
        """

        # With tournament_slug_id I am reusing value that was created by endpoint handling function get_tournament_slug(match), I think it is better
        # to reuse it than call it two times, because the result will be the same, so if the value is being passed, that means, that 
        # tournament is alredy matched if not that means it is not matched and the value is an empty string

        # go through teams always should be only two teams, but still loop is more elegant
        for team in match.teams:
            await self.client.update_one(
                {
                "sport": match.sport,
                "bookmaker": match.bookmaker,
                "tournament": match.tournament,
                "competitor": slugify(team),
                "competitor_nice": team
                },
                {
            "$setOnInsert": {
                "sport": match.sport,
                "bookmaker": match.bookmaker,
                "tournament": match.tournament,
                "competitor": slugify(team),
                "competitor_nice": team,
                "label": " - ".join(match.teams),
                }
            }, upsert=True)
        
        #for team in match.teams:
            #competitors = self.client.find({
            #"sport": match.sport,
            #"bookmaker": match.bookmaker,
            #"tournament_slug_id": tournament_slug_id,
            #"tournament_slugified_name": match.tournament,
            #"tournament_slug_id": tournament_slug_id,
            #"competitor_name": team
            #})
            #print("getting upserted competitors")
            #[print(competitor) async for competitor in competitors]
    
    # for development purposes
    async def delete_all(self):
        await self.client.delete_many({})


class MatchedEventsRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorDatabase) -> None:
        super().__init__(client)
        self._client = self._client[COLLECTION_NAME_MATCHED_EVENTS]
    
    # in the future get_matched_competitors_by_match can be replaced by this function,
    # I can simply introduce more filter params
    async def filter_competitors(self, sport: Sport = None) -> List[MatchedEvent]:
        query = {}
        if sport:
            query["sport"] = sport.value
        competitors_docs = self.client.find(query)
        return [MatchedEvent(**competitor) async for competitor in competitors_docs]
    # event and match are in this case completeley interchangeable
    # TODO: break match down into parameters
    async def get_matched_competitors_by_match(self, match: MatchInUpsert) -> List[MatchedEvent]:
        """get slug id of matched tournament
        example of matched competitor:
        {
        "sport": "soccer",
        "tournament_slug_id": "premiere-league", // unified tournament, which has to be same for all bookmakers
        "competitor_slug_id": "liverpool", // unified competitor, which has to be same for all bookmakers
        "bookmaker_different_event_names": {
            "thunder-pick": {
                "tournament": ["premiere-league"], // match.tournament slugified tournament extracted from bookmaker can be different for every bookmaker
                "competitor": ["liverpool"] // match.team[x] slugified competitor extracted from bookmaker can be different for every bookmaker
            },
            "n-1-bet": {
                "tournament": ["premiere-league"],
                "competitor": ["liverpool"]
            }
        }
    }
        """
        nested_competitor_names_path = ".".join(["bookmaker_different_event_names", match.bookmaker, "competitor"])
        nested_tournament_names_path = ".".join(["bookmaker_different_event_names", match.bookmaker, "tournament"])
        # this is weird function I can not await it but the only way to get result is to use it in async for loop
        competitor_docs = self.client.find({
            "sport": match.sport,
            "$or": [
                {
                    "$and": [
                        {nested_competitor_names_path: slugify(match.teams[0])},
                        {nested_tournament_names_path: match.tournament}
                    ]
                },
                {
                    "$and": [
                        {nested_competitor_names_path: slugify(match.teams[1])},
                        {nested_tournament_names_path: match.tournament}
                    ]
                }
            ]
        })
        
        return [MatchedEvent(**competitor) async for competitor in competitor_docs]
    
    async def add_link(self, sport: Sport, action_type: str,
                      tournament_slug_id: str,
                      competitor_slug_id: str,
                      bookmaker_different_event_names: dict) -> MatchedEvent:
        # basic validation
        if not sport:
            raise MatchedEventIngestionError("sport is required.")
        if not tournament_slug_id:
            raise MatchedEventIngestionError("tournament_slug_id is required")
        if not competitor_slug_id:
            raise MatchedEventIngestionError("competitor_slug_id is required")
        if type(bookmaker_different_event_names) != dict:
            raise MatchedEventIngestionError("bookmaker_different_event_names has to be a dict")
        if action_type.lower() not in ["new", "add"]:
            raise MatchedEventIngestionError("Unsupported action_type")

        if action_type.lower() == "new":
            await self.client.update_one({
                "sport": sport,
                "tournament_slug_id": tournament_slug_id,
                "competitor_slug_id": competitor_slug_id
                },
                {
                "$setOnInsert": {
                    "sport": sport,
                    "tournament_slug_id": tournament_slug_id,
                    "competitor_slug_id": competitor_slug_id,
                    "bookmaker_different_event_names": bookmaker_different_event_names
                    }
                }, upsert=True)

        elif action_type.lower() == "add":
            bookmaker_key = list(bookmaker_different_event_names.keys())[0]
            # check if there is only one bookmaker
            # check if in that bookmaker is only one tournament
            # check if in that bookmaker is only one competitor
            if len(list(bookmaker_different_event_names.keys())) != 1 or type(bookmaker_different_event_names[bookmaker_key]) != dict \
                or len(bookmaker_different_event_names[bookmaker_key]["tournament"]) != 1 or len(bookmaker_different_event_names[bookmaker_key]["competitor"]) != 1 \
                or type(bookmaker_different_event_names[bookmaker_key]["tournament"][0]) != str or type(bookmaker_different_event_names[bookmaker_key]["competitor"][0]) != str:
                raise MatchedEventIngestionError("If you are adding matched event you can not add more than one competitor (str) and tournament (str) in one bookmaker at a time.")
            bookmaker_competitor_names_path = ".".join(["bookmaker_different_event_names", bookmaker_key, "competitor"])
            bookmaker_tournament_names_path = ".".join(["bookmaker_different_event_names", bookmaker_key, "tournament"])
            self.client.update_one(
                {"sport": sport,
                "tournament_slug_id": tournament_slug_id,
                "competitor_slug_id": competitor_slug_id
                },
                {"$addToSet": { 
                    bookmaker_competitor_names_path:  bookmaker_different_event_names[bookmaker_key]["competitor"][0],
                    bookmaker_tournament_names_path:  bookmaker_different_event_names[bookmaker_key]["tournament"][0]
                }
                }
                )
        doc = await self.client.find_one({
            'sport':sport,
            'tournament_slug_id': tournament_slug_id,
            'competitor_slug_id': competitor_slug_id
            })
        if doc:
            return MatchedEvent(**doc)
        raise EntityDoesNotExist("It seems like for some reason the matched wasn't created nor added.")



    async def delete_link(self, sport: Sport,
                      action_type: str,
                      tournament_slug_id: str,
                      competitor_slug_id: str,
                      bookmaker_different_event_names: dict) -> MatchedEvent:
        # basic validation
        if not sport:
            raise MatchedEventDeletionError("sport is required.")
        if not tournament_slug_id:
            raise MatchedEventDeletionError("tournament_slug_id is required")
        if not competitor_slug_id:
            raise MatchedEventDeletionError("competitor_slug_id is required")
        if action_type.lower() not in ["whole", "part"]:
            raise MatchedEventDeletionError("Unsupported action_type")

        if action_type.lower() == "whole":
            await self.client.delete_one({
                "sport": sport,
                "tournament_slug_id": tournament_slug_id,
                "competitor_slug_id": competitor_slug_id
            })
        elif action_type.lower() == "part":
            if type(bookmaker_different_event_names) != dict:
                raise MatchedEventDeletionError("bookmaker_different_event_names has to be a dict")

            bookmaker_key = list(bookmaker_different_event_names.keys())[0]
            if len(list(bookmaker_different_event_names.keys())) != 1 or type(bookmaker_different_event_names[bookmaker_key]) != dict \
                or len(bookmaker_different_event_names[bookmaker_key]["competitor"]) != 1 or len(bookmaker_different_event_names[bookmaker_key]["tournament"]) != 1 \
                or type(bookmaker_different_event_names[bookmaker_key]["competitor"][0]) != str or type(bookmaker_different_event_names[bookmaker_key]["tournament"][0]) != str:
            #if len(list(bookmaker_different_event_names["competitor"].keys())) != 1 or len(list(bookmaker_different_event_names["tournament"].keys())) != 1 \
            #    or len(list(bookmaker_different_event_names["competitor"].values())[0]) != 1 or len(list(bookmaker_different_event_names["tournament"].values())[0]) != 1:
                raise MatchedEventDeletionError("If you are deleting part of matched event you can not delete more than one competitor (str) and tournament (str) in one bookmaker at a time.")

            bookmaker_competitor_names_path = ".".join(["bookmaker_different_event_names", bookmaker_key, "competitor"])
            bookmaker_tournament_names_path = ".".join(["bookmaker_different_event_names", bookmaker_key, "tournament"])
            await self.client.update_one({
                "sport": sport,
                "tournament_slug_id": tournament_slug_id,
                "competitor_slug_id": competitor_slug_id
            },
            {
                "$pull": {
                        bookmaker_competitor_names_path:  bookmaker_different_event_names[bookmaker_key]["competitor"][0],
                        bookmaker_tournament_names_path:  bookmaker_different_event_names[bookmaker_key]["tournament"][0]

                    }
                }
            )
        doc = await self.client.find_one({
            'sport':sport,
            'tournament_slug_id': tournament_slug_id,
            'competitor_slug_id': competitor_slug_id
            })

        if doc:
            return MatchedEvent(**doc)
        raise EntityDoesNotExist(f"Whole matched competitor: {competitor_slug_id} with in tournament: {tournament_slug_id} was successfully deleted.")

    # for development purposes
    async def delete_all(self):
        await self.client.delete_many({})