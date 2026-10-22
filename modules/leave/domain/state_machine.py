from dataclasses import dataclass

DRAFT = "draft"
AWAITING_SUBSTITUTE = "awaiting_substitute"
PENDING_UNIT_HEAD = "pending_unit_head"
APPROVED = "approved"
REJECTED = "rejected"
WITHDRAWN = "withdrawn"

TERMINAL = frozenset({APPROVED, REJECTED, WITHDRAWN})

#: Still in the running, so the auto-withdraw sweep knows what to close.
IN_FLIGHT = frozenset({DRAFT, AWAITING_SUBSTITUTE, PENDING_UNIT_HEAD})

# Explicit per transition rather than inferred, because a recruiter is an outsider.
EMPLOYEE = "employee"
SUBSTITUTE = "substitute"           # TPO / placement chairman, via IAM permissions
UNIT_HEAD = "unit_head"         # a company's own account, scoped to its postings

class InvalidTransition(Exception):
    def __init__(self, frm: str, event: str):
        super().__init__(f"Cannot move an application from {frm!r} to {event!r}.")
        self.frm, self.event = frm, event


@dataclass(frozen=True)
class Transition:
    frm: str
    event: str
    permission: str
    actors: frozenset[str]


def can_transition(current_status: str, event: str) -> bool:
    return (current_status, event) in TRANSITIONS


def next_status(current_status: str, event: str) -> str:
    if not can_transition(current_status, event):
        raise InvalidTransition(current_status, event)
    return _INDEX[(current_status, event)].to


TRANSITIONS: tuple[Transition, ...] = (
    # -- the employee's own moves ------------------------------------------
    Transition(DRAFT, "submit", "leave.request.create",
               frozenset({EMPLOYEE})),

    # -- substitute responses ----------------------------------------------
    Transition(AWAITING_SUBSTITUTE, "substitute_accept",
               "leave.substitute.accept",
               frozenset({SUBSTITUTE})),
    Transition(AWAITING_SUBSTITUTE, "substitute_decline",
               "leave.substitute.decline",
               frozenset({SUBSTITUTE})),

    # -- unit head responses -----------------------------------------------
    Transition(PENDING_UNIT_HEAD, "unit_head_approve",
               "leave.unit_head.approve",
               frozenset({UNIT_HEAD})),
    Transition(PENDING_UNIT_HEAD, "unit_head_reject",
               "leave.unit_head.reject",
               frozenset({UNIT_HEAD})),

    # -- withdrawal: a student may pull out of anything not already ended ---
    Transition(DRAFT, "withdraw", "leave.request.withdraw",
               frozenset({EMPLOYEE})),
    Transition(AWAITING_SUBSTITUTE, "withdraw", "leave.request.withdraw",
               frozenset({EMPLOYEE})),
    Transition(PENDING_UNIT_HEAD, "withdraw", "leave.request.withdraw",
               frozenset({EMPLOYEE})),
)

_INDEX = {(t.frm, t.event): t for t in TRANSITIONS}
