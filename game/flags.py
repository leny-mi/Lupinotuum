import enum


class Flags(enum.Enum):
    # Town roles
    VOTE_READY = 0
    GUARDED = 1
    INHIBITED = 2
    GRACED = 3
    ABILITY_READY = 4
    VOTE_BLOCKED = 5
