from django import template

register = template.Library()


@register.filter
def normalize_icon(value):
    """Return a safe FontAwesome class string for a service icon.

    Rules:
    - If value is falsy, return a default icon class.
    - If value contains a space, assume it's already a class list and return as-is.
    - If value starts with 'fa-' return 'fas ' + value.
    - Otherwise assume value is an icon name and return 'fas fa-<name>'.
    """
    if not value:
        return 'fas fa-broom'
    val = str(value).strip()
    if ' ' in val:
        return val
    if val.startswith('fa-'):
        return f'fas {val}'
    return f'fas fa-{val}'
