from enum import Enum


class CharacterLifecycleStatus(str, Enum):
    """
    Lifecycle status of a Companion Character.
    Decoupled from User's active selection.
    """
    AVAILABLE = "available"
    ARCHIVED = "archived"
    DELETED = "deleted"
