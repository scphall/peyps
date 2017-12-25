import argparse
from peyps.diary import Diary

MODE_ADD = 'add'
MODE_READ = 'read'
MODE_BURN = 'burn'
RUNNER_HELP = {
    MODE_ADD: 'Add entry to diary',
    MODE_READ: 'Show diary',
    MODE_BURN: 'Burn entry',
}


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
        '-n',
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
            d.display(n=args.n)
        elif args.mode == MODE_BURN:
            d.burn(args.hash)

    #from IPython import embed
    #embed()
