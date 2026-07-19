import datetime
from decimal import Decimal

from app.modules.enrolments.models.enrolment import Enrolment


def calculate_enrolment_monthly_fee(enrolment: Enrolment):
    total_months = enrolment.pricing_plan.end_month - enrolment.pricing_plan.start_month
    if total_months < 0:
        total_months += 12

    current_month = datetime.date.today().month
    months_passed = current_month - enrolment.pricing_plan.start_month
    if months_passed < 0:
        months_passed += 12

    # clamp to total months
    if months_passed > total_months:
        months_passed = total_months

    if months_passed < enrolment.months_paid:
        return Decimal("0")

    print(enrolment.pricing_plan.monthly_price)
    return enrolment.pricing_plan.monthly_price * (months_passed - enrolment.months_paid)
