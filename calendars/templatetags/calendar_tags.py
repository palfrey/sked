from django import template

register = template.Library()

@register.inclusion_tag('access_view.html', name="access")
def access(cal, m_cal):
    ac = m_cal.get_access(cal)
    return {'id': ac.id, 'chosen': ac.access_level}