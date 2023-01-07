class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""


class MatchedEventIngestionError(Exception):
    """Raised when there is error while ingesting data into matched competitors db"""

class MatchedEventDeletionError(Exception):
    """Raised when there is error while deleting data from matched events db"""
