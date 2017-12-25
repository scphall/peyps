import os
import re
from sys import stdout
import json
import uuid
from collections import defaultdict
import datetime as dt

import textwrap
import pandas as pd

from peyps.utils import red, yellow, Names


WIDTH = 80


class Diary(object):
    def __init__(self):
        self.path = os.getenv('PEYPSPATH', os.getenv('HOME'))
        self.path = os.path.join(self.path, '.peyps')
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        self._diary = {}

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, tb):
        self.write()

    @property
    def df(self):
        if self._diary is not None:
            return self.to_df()
        else:
            raise ValueError('No diary to read yet!')

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
        self.display(n=1)

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
        stdout.write('Removed diary entry {}'.format(hash))
        Diary._stdout_row(hash, self.to_df(hash).iloc[0])
        self._diary.pop(hash)

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
