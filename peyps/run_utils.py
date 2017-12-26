import argparse
import re
from collections import namedtuple
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


DateRange = namedtuple('DateRange', ['from_', 'upto'])


def makedate(date_str):
    """
    Make a `datetime.date` from an ISO formatted string.

    Parameters
    ==========
    date_str: str
        String representing an ISO format date.

    Returns
    =======
    datetime.date
    """
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def str2date(date_str):
    """
    From a string indicating either an absolute or relative
    date string, create a `datetime.date`.

    Parameters
    ==========
    date_str: str
        String representing an ISO format date, or a relative
        date with respect to today.

    Returns
    =======
    datetime.date
    """
    n_months, n_weeks, n_days = 0, 0, 0
    re_date = re.match('\d{4}-\d{2}-\d{2}', date_str)
    if re_date is not None:
        return makedate(date_str)
    months = re.search('(\d+)(months|month|m)', date_str)
    weeks = re.search('(\d+)(weeks|week|w)', date_str)
    days = re.search('(\d+)(days|day|d)', date_str)
    if months is not None:
        n_months = abs(int(months.groups()[0]))
        date_str = date_str.replace(months.group(), '')
    if weeks is not None:
        n_weeks = abs(int(weeks.groups()[0]))
        date_str = date_str.replace(weeks.group(), '')
    if days is not None:
        n_days = abs(int(days.groups()[0]))
        date_str = date_str.replace(days.group(), '')
    if len(date_str) > 0 and n_days == 0:
        days = re.search('(\d+)', date_str)
        if days is not None:
            n_days = abs(int(days.groups()[0]))
            date_str = date_str.replace(days.group(), '')
    n_days += 7 * n_weeks
    return date.today() - relativedelta(months=n_months, days=n_days)


class ListToDateRangeAction(argparse.Action):
    """
    Slightly imperfect Action class to turn a list (nargs='+' must
    be implemented) of 1 or 2 input variables into 2 datetimes (or None)
    in the form of a DateRange namedtuple.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(ListToDateRangeAction, self).__init__(
            option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values,
                 option_string=None):
        date_from, date_upto = None, None
        if isinstance(values, list):
            if len(values) == 1:
                date_from = str2date(values[0])
            elif len(values) == 2:
                date_from = str2date(values[0])
                date_upto = str2date(values[1])
                if date_from > date_upto:
                    date_from, date_upto = date_upto, date_from
        setattr(namespace, self.dest, DateRange(date_from, date_upto))


class ListToStringAction(argparse.Action):
    """
    Slightly imperfect Action class to turn a list (nargs='+' must
    be implemented) into a single string.
    """
    def __init__(self, option_strings, dest, **kwargs):
        super(ListToStringAction, self).__init__(
            option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values,
                 option_string=None):
        if isinstance(values, list):
            values = ' '.join(values).replace('. ', '.  ')
        setattr(namespace, self.dest, values)
