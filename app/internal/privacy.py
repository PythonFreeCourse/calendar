import enum

from sqlalchemy.sql.elements import Null


class PrivacyKinds(enum.Enum):
    Public = 1
    Private = 2
    Hidden = 3


class PrivateEvent:
    """Represents a private event to show a non-owner of private event"""
    def __init__(self, start, end, owner_id) -> None:
        self.title = PrivacyKinds.Private.name
        self.start = start
        self.end = end
        self.privacy = PrivacyKinds.Private.name
        self.content = PrivacyKinds.Private.name
        self.owner_id = owner_id
        self.location = PrivacyKinds.Private.name
        self.color = Null
        self.invitees = PrivacyKinds.Private.name
        self.category_id = Null
        self.emotion = Null
