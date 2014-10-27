__copyright__ = 'Copyright(c) Gordon Elliott 2014'

"""
    Applies defined rules to maintain wallets at certain levels.
    There are two operations the leveller can carry out:
        top up: increases the level of funds in a wallet to meet the specified
                threshold
        clear down: reduce the level of funds in a wallet to meet the
                specified threshold

    Consider a small change wallet on mobile device. In the event that the
    mobile device is lost it is desirable that there are not too many funds
    on it. On the other hand it is tedious to constantly keep topping up a
    wallet that is being used regularly.

    Secondly consider a current account and a savings account. It is desirable
    to keep most funds in the savings account provided that there are sufficient
    funds in the current account to deal with day-to-day expenditure.
"""