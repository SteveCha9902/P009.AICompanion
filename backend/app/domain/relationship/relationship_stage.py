from enum import Enum

class RelationshipStage(str, Enum):
    # Legacy Stages
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    TRUSTED_COMPANION = "trusted_companion"

    # Sprint 55 4-Stage Lifecycle Aliases
    STAGE_1_NEW = "STAGE_1_NEW"
    STAGE_2_FAMILIAR = "STAGE_2_FAMILIAR"
    STAGE_3_TRUSTED = "STAGE_3_TRUSTED"
    STAGE_4_DEEP = "STAGE_4_DEEP"
