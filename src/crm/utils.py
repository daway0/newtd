import jdatetime as jdt


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
