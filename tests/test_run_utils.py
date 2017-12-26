#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from peyps.run_utils import str2date, makedate


class TestMakeDate(TestCase):
    def test_makedate(self):
        self.assertEqual(
            date(2017, 1, 1),
            makedate('2017-01-01'),
        )


class TestStr2Date(TestCase):
    def test_iso(self):
        self.assertEqual(
            date(2017, 1, 1),
            str2date('2017-01-01'),
        )

    def test_rel_month(self):
        d = date.today() - relativedelta(months=1)
        self.assertEqual(d, str2date('1m'))
        self.assertEqual(d, str2date('1month'))
        d = date.today() - relativedelta(months=3)
        self.assertEqual(d, str2date('3months'))

    def test_rel_week(self):
        d = date.today() - timedelta(days=7)
        self.assertEqual(d, str2date('1w'))
        self.assertEqual(d, str2date('1week'))
        d = date.today() - timedelta(days=21)
        self.assertEqual(d, str2date('3weeks'))

    def test_rel_day(self):
        d = date.today() - timedelta(days=6)
        self.assertEqual(d, str2date('6d'))
        self.assertEqual(d, str2date('6days'))
        d = date.today() - timedelta(days=2)
        self.assertEqual(d, str2date('2day'))
        self.assertEqual(d, str2date('2day'))

    def test_rel_multi(self):
        d = date.today() - relativedelta(months=1, weeks=2, days=1)
        self.assertEqual(d, str2date('1m2w1'))
        self.assertEqual(d, str2date('1m2w1d'))
        self.assertEqual(d, str2date('1month2weeks1day'))
