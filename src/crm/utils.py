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

    final_string = list()

    years_diff = unitl_date_obj.year - start_date_obj.year

    days_diff = unitl_date_obj.day - start_date_obj.day
    if days_diff < 0:
        last_day_of_month = get_last_day_of_month(unitl_date_obj)
        days_diff = last_day_of_month - abs(days_diff)

    month_diff = unitl_date_obj.month - start_date_obj.month
    if month_diff < 0:
        month_diff = 12 - abs(month_diff)

    if days_diff != 0 and month_diff != 0:
        # Decreasing month value becasuse its actually not a month,
        # its between 1 to 30 days, for instance:
        # when we have 25 days until end_date, we have to say
        # "25 روز", not "1 ماه و 25 روز".
        month_diff -= 1

    if years_diff > 0:
        final_string.append(f"{years_diff} سال")
    if month_diff > 0:
        final_string.append(f"{month_diff} ماه")
    if days_diff > 0:
        final_string.append(f"{days_diff} روز")

    return ", ".join(final_string)
