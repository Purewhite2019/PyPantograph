from typing import Optional, Tuple
from dataclasses import dataclass, field
from pantograph.expr import GoalState

@dataclass(frozen=True)
class TacticInvocation:
    """
    One tactic invocation with the before/after goals extracted from Lean source
    code.
    """
    before: str
    after: str
    tactic: str
    used_constants: list[str]

    @staticmethod
    def parse(payload: dict):
        return TacticInvocation(
            before=payload["goalBefore"],
            after=payload["goalAfter"],
            tactic=payload["tactic"],
            used_constants=payload.get('usedConstants', []),
        )

@dataclass(frozen=True)
class CompilationUnit:

    # Byte boundaries [begin, end[ of each compilation unit.
    i_begin: int
    i_end: int

    messages: list[str] = field(default_factory=list)

    invocations: Optional[list[TacticInvocation]] = None
    # If `goal_state` is none, maybe error has occurred. See `messages`
    goal_state: Optional[GoalState] = None
    goal_src_boundaries: Optional[list[Tuple[int, int]]] = None

    new_constants: Optional[list[str]] = None

    @staticmethod
    def parse(payload: dict, goal_state_sentinel=None):
        i_begin = payload["boundary"][0]
        i_end = payload["boundary"][1]
        messages = payload["messages"]

        if (invocation_payload := payload.get("invocations")) is not None:
            invocations = [
                TacticInvocation.parse(i) for i in invocation_payload
            ]
        else:
            invocations = None

        if (state_id := payload.get("goalStateId")) is not None:
            goal_state = GoalState.parse_inner(int(state_id), payload["goals"], goal_state_sentinel)
            goal_src_boundaries = payload["goalSrcBoundaries"]
        else:
            goal_state = None
            goal_src_boundaries = None

        new_constants = payload.get("newConstants")

        return CompilationUnit(
            i_begin,
            i_end,
            messages,
            invocations,
            goal_state,
            goal_src_boundaries,
            new_constants
        )