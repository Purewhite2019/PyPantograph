"""
Data structuers for expressions and goals
"""
from dataclasses import dataclass
from typing import Optional, Union

Expr = str

def parse_expr(payload: dict) -> Expr:
    return payload["pp"]

@dataclass(frozen=True)
class Variable:
    t: Expr
    v: Optional[Expr] = None
    name: Optional[str] = None

    @staticmethod
    def parse(payload: dict):
        name = payload.get("userName")
        t = parse_expr(payload["type"])
        v = payload.get("value")
        if v:
            v = parse_expr(v)
        return Variable(t, v, name)

    def __str__(self):
        result = self.name if self.name else "_"
        result += f" : {self.t}"
        if self.v:
            result += f" := {self.v}"
        return result

@dataclass(frozen=True)
class Goal:
    variables: list[Variable]
    target: Expr
    name: Optional[str] = None
    is_conversion: bool = False

    @staticmethod
    def sentence(target: Expr):
        return Goal(variables=[], target=target)

    @staticmethod
    def parse(payload: dict):
        name = payload.get("userName")
        variables = [Variable.parse(v) for v in payload["vars"]]
        target = parse_expr(payload["target"])
        is_conversion = payload["isConversion"]
        return Goal(variables, target, name, is_conversion)

    def __str__(self):
        front = "|" if self.is_conversion else "⊢"
        return "\n".join(str(v) for v in self.variables) + \
            f"\n{front} {self.target}"

@dataclass(frozen=True)
class GoalState:
    state_id: int
    goals: list[Goal]

    _sentinel: list[int]

    def __del__(self):
        self._sentinel.append(self.state_id)

    @property
    def is_solved(self) -> bool:
        """
        WARNING: Does not handle dormant goals.
        """
        return not self.goals

    @staticmethod
    def parse_inner(state_id: int, goals: list, _sentinel: list[int]):
        goals = [Goal.parse(g) for g in goals]
        return GoalState(state_id, goals, _sentinel)
    @staticmethod
    def parse(payload: dict, _sentinel: list[int]):
        return GoalState.parse_inner(payload["nextStateId"], payload["goals"], _sentinel)

@dataclass(frozen=True)
class TacticHave:
    branch: str
@dataclass(frozen=True)
class TacticCalc:
    step: str

Tactic = Union[str, TacticHave, TacticCalc]
