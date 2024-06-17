from math import ceil

import jdatetime
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_400_BAD_REQUEST


def get_diff_in_percentage(now: int, before: int) -> float:
    assert isinstance(now, int)
    assert isinstance(before, int)
    try:
        return int(100 * now / before - 100)
    except ZeroDivisionError:
        # means exponential growth and must be handled by template
        return None


def gdate_to_jdate(date: jdatetime.date) -> str:
    jdate = jdatetime.GregorianToJalali(date.year, date.month, date.day)
    return f"{jdate.jyear}/{jdate.jmonth}/{jdate.jday}"


def get_month_start_end(
    month_count: int,
) -> tuple[jdatetime.date, jdatetime.date]:
    """for example if we are in 1402/05/06
    get_month_start_end(2) returns  (1402/03/06, 1402/04/06)
    """
    assert month_count != 0
    start = jdatetime.datetime.now() - jdatetime.timedelta(
        days=30 * month_count
    )
    end = jdatetime.datetime.now() - jdatetime.timedelta(
        days=30 * (month_count - 1)
    )

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
    name, title, datatable_headers: list[str], qs: QuerySet, table_template: str
) -> dict:
    return dict(
        name=name,
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


def is_leap_year(year: int) -> bool:
    leap_year_consts = (1, 5, 9, 13, 17, 22, 26, 30)
    return year % 33 in leap_year_consts


def get_last_day_of_month(date_obj: jdatetime.date) -> int:
    """
    Calculating last day of the given date and returning it.

    Args:
        date_obj: The date you want to get the last day of it.

    Returns:
        last day of the given month.
    """

    if date_obj.month in (1, 2, 3, 4, 5, 6):
        return 31

    if date_obj.month == 12:
        # leap year
        if is_leap_year(date_obj.year):
            return 30
        return 29

    return 30


def create_jdate_from_str(str_date: str) -> jdatetime.date:
    return jdatetime.date(
        int(str_date.split("/")[0]),
        int(str_date.split("/")[1]),
        int(str_date.split("/")[2]),
    )


def calculate_time_between_2dates(
    start_date_obj: jdatetime.date, until_date_obj: jdatetime.date, suffix: str
) -> str:
    """
    Calculating remaining time from an specific date to another one
    in persian verbose format.

    Suffix will be choosed based on if 'start_date_obj' is smaller or
    bigger.

    Args:
        start_date_obj: start date
        until_date_obj: end date

    Returns:
        str: Persian verbose format of remaining time.
    """
    difference = abs((until_date_obj - start_date_obj).days)

    if difference >= 365:
        # using 365.25 cause of leap years.
        time_left = (
            f"{difference // 365} سال و {ceil(difference % 365.25)} روز"
        )
    else:
        time_left = f"{difference} روز"

    return f"{time_left} {suffix}"


def membership_from_verbose(
    start_date_obj: jdatetime.date, until_date_obj: jdatetime.date
) -> str:
    if start_date_obj == until_date_obj:
        return "امروز"

    if start_date_obj > until_date_obj:
        suffix = "دیگر"
    else:
        suffix = "قبل"

    return calculate_time_between_2dates(
        start_date_obj, until_date_obj, suffix
    )


def contract_end_verbose(
    start_date_obj: jdatetime.date, until_date_obj: jdatetime.date
) -> str:
    if start_date_obj == until_date_obj:
        return "امروز"

    if start_date_obj > until_date_obj:
        suffix = "قبل"
    else:
        suffix = "دیگر"

    return calculate_time_between_2dates(
        start_date_obj, until_date_obj, suffix
    )


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


def seperate_numbers(threshold: int, number: str) -> str:
    assert number.isdigit()
    seperator = "-" if threshold == 4 else ","

    final_number = list()
    for index, bit in enumerate(reversed(number)):
        if (index + 1) % threshold == 1 and index + 1 != 1:
            final_number.append(seperator)

        final_number.append(bit)

    return "".join(final_number[::-1])


def err_response(err: str | dict) -> Response:
    if isinstance(err, dict):
        return Response(err, HTTP_400_BAD_REQUEST)

    return Response({"error": err}, HTTP_400_BAD_REQUEST)


def raise_validation_err(code: str, value: str):
    raise ValidationError({"code": code, "value": value})


def calculate_age(birthdate: str):
    birth_year = int(birthdate.split("/")[0])
    birth_month = int(birthdate.split("/")[1])
    birth_day = int(birthdate.split("/")[2])

    today = jdatetime.date.today()

    return (
        today.year
        - birth_year
        # 10 - True = 9, so if you were born on 03/01 and today is 02/01
        # you have not completed today's age yet.
        - ((today.month, today.day) < (birth_month, birth_day))
    )
