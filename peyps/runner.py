#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
import argparse
import re
from collections import namedtuple
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from peyps.diary import Diary
from peyps.run_utils import ListToStringAction, ListToDateRangeAction
from peyps.run_utils import DateRange

MODE_ADD = 'add'
MODE_READ = 'read'
MODE_BURN = 'burn'
MODE_INFO = 'info'
RUNNER_HELP = {
    MODE_ADD: 'Add entry to diary',
    MODE_READ: 'Show diary entries',
    MODE_BURN: 'Burn entry',
    # MODE_INFO: 'TODO',
}


def parser_args_add(parser):
    """
    Parser arguments for `peyps add`.
    """
    parser.add_argument(
        'entry',
        nargs='+',
        action=ListToStringAction,
        help='',
    )


def parser_args_read(parser):
    """
    Parser arguments for `peyps read`.
    """
    parser.add_argument(
        '-t', '--tags',
        nargs='+',
        type=str,
        help='Search for tags in entries',
    )
    parser.add_argument(
        '-d', '--date',
        action=ListToDateRangeAction,
        nargs='+',
        help=(
            'Search in date range: from (upto), '
            'either ISO format date, or text (eg 1m2w)'
        ),
        default=DateRange(None, None),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--head',
        type=int,
        required=False,
        help='Top of page',
    )
    group.add_argument(
        '-n', '--tail',
        type=int,
        required=False,
        help='Bottom of page',
    )


def parser_args_burn(parser):
    """
    Parser arguments for `peyps burn`.
    """
    parser.add_argument(
        'index',
        type=str,
        help='Burn the entry index... never to be seen again',
    )


def parse_args():
    """
    Parse all arguments.
    """
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
    import argcomplete
    argcomplete.autocomplete(parser)
    return parser.parse_args()


def run():
    """
    Run!
    """
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
            d.burn(args.index)
