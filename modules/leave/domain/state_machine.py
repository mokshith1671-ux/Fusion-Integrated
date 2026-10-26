from dataclasses import dataclass

DRAFT = "draft"
AWAITING_SUBSTITUTE = "awaiting_substitute"
APPLICANT_ACTION_REQUIRED = "applicant_action_required"
AWAITING_UNIT_HEAD = "awaiting_unit_head"
AWAITING_FINAL_SANCTION = "awaiting_final_sanction"
APPROVED = "approved"
REJECTED = "rejected"
WITHDRAWN = "withdrawn"

TERMINAL = frozenset({APPROVED, REJECTED, WITHDRAWN})

#: Still in the running, so the auto-withdraw sweep knows what to close.
IN_FLIGHT = frozenset({DRAFT, AWAITING_SUBSTITUTE, APPLICANT_ACTION_REQUIRED, AWAITING_UNIT_HEAD, AWAITING_FINAL_SANCTION})

# Explicit per transition rather than inferred, because a recruiter is an outsider.
EMPLOYEE = "employee"
SUBSTITUTE = "substitute"           # TPO / placement chairman, via IAM permissions
UNIT_HEAD = "unit_head"         # a company's own account, scoped to its postings

class InvalidTransition(Exception):
    def __init__(self, frm: str, event: str):
        super().__init__(f"Cannot apply {event!r} to a leave request in status {frm!r}.")
        self.frm, self.event = frm, event


@dataclass(frozen=True)
class Transition:
    frm: str
    event: str
    actor: str
    to: str


def can_transition(current_status: str, event: str, actor: str) -> bool:
    return (current_status, event, actor) in TRANSITIONS


def next_status(current_status: str, event: str, actor: str) -> str:
    if not can_transition(current_status, event, actor):
        raise InvalidTransition(current_status, event)
    return _INDEX[(current_status, event)].to


TRANSITIONS: tuple[Transition, ...] = (
    # -- the employee's own moves ------------------------------------------
    Transition(DRAFT, "submit_with_substitute", EMPLOYEE, AWAITING_SUBSTITUTE),
    Transition(DRAFT, "submit_without_substitute", EMPLOYEE, APPLICANT_ACTION_REQUIRED),

    # -- substitute responses ----------------------------------------------
    Transition(AWAITING_SUBSTITUTE, "substitute_accept", SUBSTITUTE, APPLICANT_ACTION_REQUIRED),
    Transition(AWAITING_SUBSTITUTE, "substitute_decline", SUBSTITUTE, AWAITING_UNIT_HEAD),

    # -- unit head responses -----------------------------------------------
    Transition(APPLICANT_ACTION_REQUIRED, "unit_head_approve", UNIT_HEAD, APPROVED),
    Transition(APPLICANT_ACTION_REQUIRED, "unit_head_reject", UNIT_HEAD, REJECTED),
    Transition(APPLICANT_ACTION_REQUIRED, "unit_head_recommend", UNIT_HEAD, AWAITING_FINAL_SANCTION),

    # -- final sanction responses ------------------------------------------
    Transition(AWAITING_FINAL_SANCTION, "sanction_approve", UNIT_HEAD, APPROVED),
    Transition(AWAITING_FINAL_SANCTION, "sanction_reject", UNIT_HEAD, REJECTED),

    # -- withdrawal: a student may pull out of anything not already ended ---
    Transition(DRAFT, "withdraw", EMPLOYEE, WITHDRAWN),
    Transition(AWAITING_SUBSTITUTE, "withdraw", EMPLOYEE, WITHDRAWN),
    Transition(APPLICANT_ACTION_REQUIRED, "withdraw", EMPLOYEE, WITHDRAWN),
    Transition(AWAITING_UNIT_HEAD, "withdraw", EMPLOYEE, WITHDRAWN),
    Transition(AWAITING_FINAL_SANCTION, "withdraw", EMPLOYEE, WITHDRAWN),
)

_INDEX = {(t.frm, t.event): t for t in TRANSITIONS}
