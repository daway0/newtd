from django import template

register = template.Library()


@register.filter(name="persianize")
def persianize(value):
    """
    Converts Latin numerals in a string to their Persian equivalents.
    """
    persian_numbers = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }
    return "".join([persian_numbers.get(char, char) for char in str(value)])


@register.filter(name="none_to_string")
def none_to_string(value):
    if not value:
        return ""
    return value