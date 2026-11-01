from decimal import Decimal

import pytest
from dateutil import parser
from django.db.models import ProtectedError

from modules.leave.models import LeaveLedgerEntry, LeaveRequest, LeaveRequestHistory


def make_request():
    return LeaveRequest.objects.create(
        user_id=1,
        category="EL",
        start_date=parser.parse("2026-10-05").date(),
        end_date=parser.parse("2026-10-09").date(),
        days_counted=Decimal("5"),
    )


def make_history(request):
    return LeaveRequestHistory.objects.create(
        request=request,
        from_status="draft",
        to_status="awaiting_unit_head",
        actor_user_id=1,
    )


def make_entry(request):
    return LeaveLedgerEntry.objects.create(
        user_id=1,
        category="EL",
        year=2026,
        entry_type="debit",
        days=Decimal("5"),
        request=request,
    )


@pytest.mark.django_db
def test_history_row_cannot_be_modified():
    history = make_history(make_request())
    with pytest.raises(ValueError):
        history.note = "Modified"
        history.save()


@pytest.mark.django_db
def test_history_row_cannot_be_deleted():
    history = make_history(make_request())
    with pytest.raises(ValueError):
        history.delete()


@pytest.mark.django_db
def test_ledger_entry_cannot_be_modified():
    entry = make_entry(make_request())
    with pytest.raises(ValueError):
        entry.note = "Modified"
        entry.save()


@pytest.mark.django_db
def test_ledger_entry_cannot_be_deleted():
    entry = make_entry(make_request())
    with pytest.raises(ValueError):
        entry.delete()


@pytest.mark.django_db
def test_request_with_history_cannot_be_deleted():
    request = make_request()
    history = make_history(request)
    with pytest.raises(ProtectedError):
        request.delete()


@pytest.mark.django_db
def test_request_with_ledger_entries_cannot_be_deleted():
    request = make_request()
    entry = make_entry(request)
    with pytest.raises(ProtectedError):
        request.delete()
