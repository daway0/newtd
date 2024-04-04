import jdatetime
import jdatetime as jdt
from django.db.models import QuerySet


def get_diff_in_percentage(now: int, before: int) -> float:
    assert isinstance(now, int)
    assert isinstance(before, int)
    try:
        return int(100 * now / before - 100)
    except ZeroDivisionError:
        # means exponential growth and must be handled by template
        return None


def gdate_to_jdate(date: jdt.date) -> str:
    jdate = jdt.GregorianToJalali(date.year, date.month, date.day)
    return f"{jdate.jyear}/{jdate.jmonth}/{jdate.jday}"


def get_month_start_end(month_count: int) -> tuple[jdt.date, jdt.date]:
    """for example if we are in 1402/05/06
    get_month_start_end(2) returns  (1402/03/06, 1402/04/06)
    """
    assert month_count != 0
    start = jdt.datetime.now() - jdt.timedelta(days=30 * month_count)
    end = jdt.datetime.now() - jdt.timedelta(days=30 * (month_count - 1))

    format = "%Y/%m/%d"

    return start.strftime(format), end.strftime(format)


def make_dashboard_card_data(
    title, number, icon_name, growth_percentage, **kwargs
) -> dict:
    return dict(
        title=title,
        icon=f"svg/{icon_name}.html",
        this_month_number=number,
        growth=growth_percentage,
        **kwargs,
    )


def make_section_tab(
    title, datatable_headers: list[str], qs: QuerySet, table_template: str
) -> dict:
    return dict(
        title=title,
        data_table_headers=datatable_headers,
        qs=qs,
        table_template=table_template,
    )


def summarize_tooman_number(value):
    assert isinstance(value, int)
    if value < 999999:
        return int(value / 1000)
    elif value < 999999999:
        return round(value / 1000000, 1)
    elif value < 999999999999:
        return round(value / 1000000000, 1)


def summarize_tooman_postfix_word(value):
    assert isinstance(value, int)
    if value < 999999:
        return "هزار تومان"
    elif value < 999999999:
        return "میلیون تومان"
    elif value < 999999999999:
        return "میلیارد تومان"


def translate_serializer_fields(
    serialized_data: dict,
    translated_fields: dict,
    exclude_fields: list[str] = [],
):
    """
    Translating serializer fields based on the given data, then
    converting each field to object for the sake of frontend.

    All fields within 'serialized_data' HAVE TO have a translated value
    in 'translated_fields', or specified within 'exclude_fields'.

    Fields that are exists in 'exclude_fields' will not
    have a translated value.

    Args:
        serialized_data: The final data of serializer.
        translated_fields: Translated value of serializer fields.
        exclude_fields: Fields which you dont want to translate.
    """

    new_data = dict()
    for key, value in serialized_data.items():
        if key in exclude_fields:
            new_data[key] = value
            continue

        new_data[key] = {"title": translated_fields[key]}

        if isinstance(value, dict):
            new_data[key].update(value)
        else:
            new_data[key]["value"] = value

    return new_data


def get_last_day_of_month(date_obj: jdatetime.date) -> int:
    """
    Calculating last day of the given date and returning it.

    Args:
        date_obj: The date you want to get the last day of it.

    Returns:
        last day of the given month.
    """

    if date_obj.day == 31:
        # day is already on maximum value, so we dont need to
        # calculate anything here.
        return date_obj.day

    last_day_value = date_obj.day

    while last_day_value < 31:
        last_day_value = date_obj.day
        date_obj += jdatetime.timedelta(days=1)
        if date_obj.day == 1:
            return last_day_value

    raise RuntimeError(
        "last_day_value passed 31 and your logic couldn't find "
        "the last day of month, Abort!"
    )


def create_jdate_from_str(str_date: str) -> jdatetime.date:
    return jdatetime.date(
        int(str_date.split("/")[0]),
        int(str_date.split("/")[1]),
        int(str_date.split("/")[2]),
    )


def time_left_til_specific_date_verbose(
    start_date_obj: jdatetime.date, unitl_date_obj: jdatetime.date
) -> str:
    """
    Calculating remaining time from an specific date to another one
    in persian verbose format.

    Args:
        start_date_obj: start date
        unitl_date_obj: end date

    Returns:
        str: Persian verbose format of remaining time.

    Raises:
        ValueError: if start_date_obj is bigger than unitl_date_obj.
    """

    if start_date_obj > unitl_date_obj:
        raise ValueError(
            "'start_date_obj' value is bigger than 'unitl_date_obj' value, "
            "your data is wrong logically, Abort!"
        )

    difference = (unitl_date_obj - start_date_obj).days
    years = difference // 365
    months = (difference % 365) // 30
    days = (difference % 365) % 30

    final_string = list()
    if years:
        final_string.append(f"{years} سال")

    if months:
        final_string.append(f"{months} ماه")

    if days:
        final_string.append(f"{days} روز")

    return " و ".join(final_string)


def omit_null_fields(data: dict, omitabale_fields: list[str]) -> dict:
    """
    Skipping null fields in serializer's data, removing them from
    final schema.
    All fields must be an instance of object which has a 'value' field
    within it, otherwise it will crash the code.

    Args:
        data: Final serializer data.
        omitabale_fields: fields which you want to skip if they are null.

    Returns:
        data after skiping null values.
    """

    new_data = dict()

    for key, value in data.items():
        if key in omitabale_fields and value["value"] is None:
            continue
        new_data[key] = value

    return new_data
