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
        self.close()

    def df(self):
        if self._diary is not None:
            return self.to_df()
        else:
            raise ValueError('No diary to read yet!')

    def open(self):
        with open(self.path, 'r') as f:
            self._diary.update(json.load(f))

    def close(self):
        with open(self.path, 'w') as f:
            json.dump(self._diary, f, indent=4)

    def add(self, note, ds=None):
        time = dt.datetime.now()
        if len(self._diary) == 0:
            ind = 0
        else:
            ind = max(map(int, self._diary.keys())) + 1
        self._diary['{:03}'.format(ind)] = {
            Names.date: str(time.date() if ds is None else ds),
            Names.tags: list(set(re.findall(r'#(\w+)', note))),
            Names.note: note,
            Names.time: str(time),
            Names.uuid: uuid.uuid4().hex[8:]
        }
        self.display(n=1)

    def remove(self, ind):
        self._diary.pop(ind)

    def to_df(self, ind=None):
        ddict = self._diary
        df = pd.DataFrame.from_dict(ddict).T
        df[Names.date] = pd.to_datetime(df[Names.date]).dt.date
        df[Names.time] = pd.to_datetime(df[Names.time])
        df = df.sort_values(Names.time)
        if ind is not None:
            if isinstance(ind, basestring):
                ind = [ind]
            df = df[df.index.isin(ind)]
        return df

    @staticmethod
    def _stdout_row(ind, row):
        time_str = '{:%Y-%m-%d %H:%M}'.format(row[Names.time])
        fill = ' ' * (WIDTH - len(time_str) - len(ind))
        head = '{time}{fill}{ind}'.format(
            time=yellow(time_str),
            fill=fill,
            ind=red(ind),
        )
        stdout.write(
            '{head}\n{note}\n\n'.format(
                head=head,
                note=textwrap.fill(row[Names.note], width=WIDTH),
            )
        )

    def stdout_ind(self, ind):
        Diary._stdout_row(
            ind,
            self.to_df(self._diary[ind]).iloc[0]
        )

    def burn(self, ind):
        stdout.write('Removed diary entry {}'.format(ind))
        Diary._stdout_row(ind, self.to_df(ind).iloc[0])
        self._diary.pop(ind)

    def display(self, df=None, n=None):
        if df is None:
            df = self.df()
        df = df.sort_values(Names.time)
        if n is not None:
            df = df.tail(n)
        for h_row in df.iterrows():
            Diary._stdout_row(*h_row)

    def read(self, tags=None, date_from=None, date_upto=None,
             head=None, tail=None):
        df = self.df()
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
