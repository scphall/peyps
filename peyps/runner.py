import argparse
from peyps.diary import Diary

MODE_ADD = 'add'


def parse_args():
    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument(
        '--add',
        required=False,
    )
    return parser.parse_args()


def run():
    args = parse_args()
    d = Diary()
    d.read()
    d.add(args.add)
    d.write()
    q = d._date_as_key()
    d.display()
    #from IPython import embed
    #embed()
