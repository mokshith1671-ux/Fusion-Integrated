from datetime import timedelta
from decimal import Decimal


def count_leave_days(category, start_date, end_date, half_day, holidays):
    if end_date < start_date:
        raise ValueError("End date must be after start date")

    days = (end_date - start_date).days + 1

    if category in ('EL', 'COL', 'VL'):
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            if current_date not in holidays:
                days += 0.5 if half_day and current_date == start_date else 1
    elif category == 'CL':
        days = Decimal('0.5') if half_day else Decimal('1')

    return days
