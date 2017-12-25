import argparse
import re
from peyps.diary import Diary
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import namedtuple

from peyps.run_utils import ListToStringAction, ListToDateRangeAction
from peyps.run_utils import DateRange

MODE_ADD = 'add'
MODE_READ = 'read'
MODE_BURN = 'burn'
RUNNER_HELP = {
    MODE_ADD: 'Add entry to diary',
    MODE_READ: 'Show diary',
    MODE_BURN: 'Burn entry',
}


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
        default=DateRange(None, None),
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
