__copyright__ = 'Copyright(c) Gordon Elliott 2014'

import parse

from behave import register_type
from decimal import Decimal

@parse.with_pattern(r"-?\d*\.?\d*")
def parse_decimal(text):
    return Decimal(text)

register_type(Decimal=parse_decimal)


def wallet_from_name(context, wallet_name):
    if wallet_name == 'source':
        wallet = context.source
    elif wallet_name == 'destination':
        wallet = context.destination
    else:
        raise ValueError('Unknown wallet {}'.format(wallet_name))
    return wallet

