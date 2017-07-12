import math

import backtrader as bt
from backtrader.analyzers import Returns as BtReturns


class Returns(BtReturns):
    '''
    Calculate the total, average, compound, and annualized returns

    Extends the original backtrader `Returns` class to allow minute
    timeframes and 24 hour markets.
    '''

    _TANN = dict(BtReturns._TANN)
    _TANN.update({
        bt.TimeFrame.Minutes: 525600.0,
        bt.TimeFrame.Days: 365.0,
    })
