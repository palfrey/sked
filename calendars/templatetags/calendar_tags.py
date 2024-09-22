from typing import TypedDict
from uuid import UUID

from django import template

from calendars.models import GoogleCalendar, IcalCalendar, MergedCalendar

register = template.Library()


class AccessReturn(TypedDict):
    id: UUID
    chosen: str


@register.inclusion_tag("access_view.html", name="access")
def access(cal: GoogleCalendar | IcalCalendar, m_cal: MergedCalendar) -> AccessReturn:
    ac = m_cal.get_access(cal)
    return {"id": ac.id, "chosen": ac.access_level}
