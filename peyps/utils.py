#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import logging


_logger = logging.getLogger(__name__)


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
    uuid = 'uuid'


def red(text):
    return '{}{}{}'.format(RED, text, RESET)


def yellow(text):
    return '{}{}'.format(YELLOW, text)


def reset(text):
    return RESET


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)-7s:%(name)-10s| %(message)s "
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
