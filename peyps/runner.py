import argparse
import re
from peyps.diary import Diary
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import namedtuple

MODE_ADD = 'add'
MODE_READ = 'read'
MODE_BURN = 'burn'
RUNNER_HELP = {
    MODE_ADD: 'Add entry to diary',
    MODE_READ: 'Show diary',
    MODE_BURN: 'Burn entry',
}


DateRange = namedtuple('DateRange', ['from_', 'upto'])


def makedate(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


def testthing(intem):
    pass


def str2date(date_str):
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
    def __init__(self, option_strings, dest, **kwargs):
        super(ListToStringAction, self).__init__(
            option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values,
                 option_string=None):
        if isinstance(values, list):
            values = ' '.join(values).replace('. ', '.  ')
        setattr(namespace, self.dest, values)


def parser_args_add(parser):
    parser.add_argument(
        'entry',
        nargs='+',
        action=ListToStringAction,
        help='',
    )


def parser_args_read(parser):
    parser.add_argument(
        '-t', '--tags',
        nargs='+',
        type=str,
        help='',
    )
    parser.add_argument(
        '-d', '--date',
        action=ListToDateRangeAction,
        nargs='+',
        help='',
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--head',
        type=int,
        required=False,
        help='',
    )
    group.add_argument(
        '-n', '--tail',
        type=int,
        required=False,
        help='',
    )


def parser_args_burn(parser):
    parser.add_argument(
        'hash',
        type=str,
        help='',
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description='Command line diary tool')
    subparsers = parser.add_subparsers(help='sub-command help')
    parsers = {}
    for mode, help in RUNNER_HELP.items():
        subparser = subparsers.add_parser(mode, help=help)
        subparser.set_defaults(mode=mode)
        parsers[mode] = subparser
    parser_args_add(parsers[MODE_ADD])
    parser_args_read(parsers[MODE_READ])
    parser_args_burn(parsers[MODE_BURN])
    return parser.parse_args()


def run():
    args = parse_args()
    with Diary() as d:
        if args.mode == MODE_ADD:
            d.add(args.entry)
        elif args.mode == MODE_READ:
            d.read(
                tags=args.tags,
                head=args.head,
                tail=args.tail,
                date_from=args.date.from_,
                date_upto=args.date.upto,
            )
        elif args.mode == MODE_BURN:
            d.burn(args.hash)
