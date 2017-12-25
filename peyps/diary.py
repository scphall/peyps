import os
import textwrap
from sys import stdout
import re
import json
import uuid
import pandas as pd
from collections import defaultdict
import datetime as dt


WIDTH = 80


RED = u'\u001b[31;1m'
GREEN = u'\u001b[32;1m'
YELLOW = u'\u001b[33;1m'
BLUE = u'\u001b[34;1m'
MAGENTA = u'\u001b[35;1m'
CYAN = u'\u001b[36;1m'
RESET = u'\u001b[0m'


class Names(object):
    date = 'date'
    time = 'time'
    tags = 'tags'
    note = 'note'
    hash = 'hash'


def red(text):
    return '{}{}{}'.format(RED, text, RESET)


def yellow(text):
    return '{}{}'.format(YELLOW, text)


def reset(text):
    return RESET


class Diary(object):
    def __init__(self):
        self.path = os.getenv('PEYPSPATH', os.getenv('HOME'))
        self.path = os.path.join(self.path, '.peyps')
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        self._diary = {}

    def open(self):
        with open(self.path, 'r') as f:
            self._diary.update(json.load(f))

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self._diary, f)

    def add(self, note, ds=None):
        time = dt.datetime.now()
        self._diary[uuid.uuid4().hex[:8]] = {
            Names.date: str(time.date() if ds is None else ds),
            Names.tags: list(set(re.findall(r'#(\w+)', note))),
            Names.note: note,
            Names.time: str(time),
        }


    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.write()

    def remove(self, hash):
        self._diary.pop(hash)

    def to_df(self, hash=None):
        ddict = self._diary
        df = pd.DataFrame.from_dict(ddict).T
        df[Names.date] = pd.to_datetime(df[Names.date]).dt.date
        df[Names.time] = pd.to_datetime(df[Names.time])
        df = df.sort_values(Names.time)
        if hash is not None:
            if isinstance(hash, basestring):
                hash = [hash]
            df = df[df.index.isin(hash)]
        return df

    @property
    def df(self):
        if self._diary is not None:
            return self.to_df()
        else:
            raise ValueError('No diary to read yet!')

    @staticmethod
    def _stdout_row(hash, row):
        time_str = '{:%Y-%m-%d %H:%M}'.format(row[Names.time])
        fill = ' ' * (WIDTH - len(time_str) - len(hash))
        head = '{time}{fill}{hash}'.format(
            time=yellow(time_str),
            fill=fill,
            hash=red(hash),
        )
        stdout.write(
            '{head}\n{note}\n\n'.format(
                head=head,
                note=textwrap.fill(row[Names.note], width=WIDTH),
            )
        )

    def stdout_hash(self, hash):
        Diary._stdout_row(
            hash,
            self.to_df(self._diary[hash]).iloc[0]
        )

    def burn(self, hash):
        entry = self._diary.pop(hash)
        stdout.write('Removed diary entry {}'.format(hash))
        Diary._stdout_row(hash, entry)

    def display(self, df=None, n=None):
        if df is None:
            df = self.df
        df = df.sort_values(Names.time)
        if n is not None:
            df = df.tail(n)
        for h_row in df.iterrows():
            Diary._stdout_row(*h_row)

    def read(self, tags=None, date_from=None, date_upto=None,
             head=None, tail=None):
        df = self.df
        if tags is not None:
            tags = set([t.lstrip('#') for t in tags])
            mask = df.tags.apply(lambda x: len(x) > len(set(x) - tags))
            df = df[mask]
        if date_from is not None:
            df = df[df.date >= date_from]
        if date_upto is not None:
            df = df[df.date <= date_upto]
        if head is not None:
            df = df.head(head)
        if tail is not None:
            df = df.tail(tail)
        self.display(df)
