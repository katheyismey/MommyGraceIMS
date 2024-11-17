import json
from django import template

register = template.Library()

@register.filter
def jsonify(value):
    """Converts a Python object to JSON string."""
    return json.dumps(value)
