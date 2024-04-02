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


@register.filter(name="remove_slash")
def remove_slash(value):
    if value[-1] == "/":
        return value[:-1]
    return value


@register.filter(name="remove_minus")
def remove_minus(value):
    assert isinstance(value, int)
    if value < 0:
        return value * -1
    return value


@register.inclusion_tag("base/breadcrumb.html")
def make_breadcrumb(path: str):
    assert len(path) > 0, "did you missed me!?"
    parents = path.split("/") if "/" in path else [path]
    return dict(parents=parents[:-1], latest=parents[-1])


@register.simple_tag(name="get_people_url")
def get_people_url(people, action: str):
    assert action.lower() in [
        "create",
        "edit",
        "update",
        "delete",
    ], "invalid action"

    return people.get_absolute_url(action.lower())
