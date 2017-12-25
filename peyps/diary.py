import os
import textwrap
from sys import stdout
import re
import json
import uuid
import pandas as pd
from collections import defaultdict
from datetime import datetime


WIDTH = 80


class Names(object):
    date = 'date'
    time = 'time'
    tags = 'tags'
    note = 'note'
    hash = 'hash'


class Diary(object):
    def __init__(self):
        self.path = os.getenv('PEYPSPATH', os.getenv('HOME'))
        self.path = os.path.join(self.path, '.peyps')
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)
        self._diary = {}

    def read(self):
        with open(self.path, 'r') as f:
            self._diary.update(json.load(f))

    def write(self):
        with open(self.path, 'w') as f:
            json.dump(self._diary, f)

    def add(self, note, ds=None):
        time = datetime.now()
        self._diary[uuid.uuid4().hex[:8]] = {
            Names.date: str(time.date() if ds is None else ds),
            Names.tags: re.findall(r'#(\w+)', note),
            Names.note: note,
            Names.time: str(time),
        }

    def __enter__(self):
        self.read()
        return self

    def __exit__(self, type, value, tb):
        self.write()

    def remove(self, hash):
        self._diary.pop(hash)

    @property
    def df(self):
        if self._diary is not None:
            df = pd.DataFrame.from_dict(self._diary).T
            df[Names.date] = pd.to_datetime(df[Names.date]).dt.date
            df[Names.time] = pd.to_datetime(df[Names.time])
            df = df.sort_values(Names.time)
            return df

    def _date_as_key(self):
        date_dict = defaultdict(list)
        for hash, v in self._diary.items():
            date_dict[v[Names.date]].append({
                Names.hash: hash,
                Names.note: v[Names.note],
                Names.time: v[Names.time],
                Names.tags: v[Names.tags],
            })

        for date, v in date_dict.items():
            date_dict[date] = sorted(v, key=lambda x: x[Names.time])
        return date_dict

    @staticmethod
    def _stdout_row(hash, row):
        time_str = '{:%H:%M}'.format(row[Names.time])
        head = '{time}{fill}{hash}'.format(
            time=time_str,
            fill=' ' * (WIDTH - len(time_str) - len(hash)),
            hash=hash,
        )
        stdout.write(
            '{head}\n{note}\n\n'.format(
                head=head,
                note=textwrap.fill(row[Names.note], width=WIDTH),
            )
        )

    def burn(self, hash):
        entry = self._diary.pop(hash)
        stdout.write('Removed diary entry {}'.format(hash))
        Diary._stdout_row(hash, entry)

    def display(self, df=None, n=None):
        if df is None:
            df = self.df
        if n is not None:
            df = df.tail(n)
        gb = df.groupby(Names.date)
        for date, df in gb:
            date_str = '{:%Y-%m-%d (%a)}'.format(date)
            stdout.write('\n{}\n{}\n'.format(date_str, '=' * len(date_str)))
            for h_row in df.iterrows():
                Diary._stdout_row(*h_row)








