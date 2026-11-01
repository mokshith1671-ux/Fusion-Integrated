from django.db import models

from core.db.mixins import TimeStampedModel, UserScopedModel


class LeaveLedgerEntry(TimeStampedModel, UserScopedModel):
    ENTRY_TYPE_CHOICES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
        ("reversal", "Reversal"),
    ]

    user_id = models.IntegerField()
    category = models.CharField(max_length=3)
    year = models.PositiveSmallIntegerField()
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    days = models.DecimalField(max_digits=5, decimal_places=2)
    request = models.ForeignKey("LeaveRequest", on_delete=models.PROTECT,
                                related_name="ledger_entries", null=True, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        db_table = "leave_ledger_entry"
        indexes = [
            models.Index(fields=["user_id", "category", "year"], name="ledger_user_cat_year_idx"),
        ]

    def __str__(self) -> str:
        return f"entry#{self.pk} u{self.user_id} {self.category} {self.entry_type} {self.days}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValueError("Ledger entries cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Ledger entries cannot be deleted.")
