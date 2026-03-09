from enum import Enum

class MotorMovement(Enum):
    FORWARDS = 1,
    BACKWARDS = 2,
    FREE = 3,
    LOCKED = 4
    
    @property
    def movement_value(self) -> int | None:
        # We map the enum member (self) to the desired output
        mapping: dict[MotorMovement, int | None] = {
            MotorMovement.FORWARDS: 1,
            MotorMovement.BACKWARDS: -1,
            MotorMovement.FREE: None,
            MotorMovement.LOCKED: 0
        }
        return mapping[self]