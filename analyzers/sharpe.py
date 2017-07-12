from backtrader import TimeFrame
from backtrader.analyzers import SharpeRatio as BtSharpeRatio


class SharpeRatio(BtSharpeRatio):
    """
    Calculate the Sharpe ratio of a strategy

    Extends the original backtrader `SharpeRatio` class to allow minute
    timeframes and 24 hour markets.
    """

    RATEFACTORS = dict(BtSharpeRatio.RATEFACTORS)
    RATEFACTORS.update({
        TimeFrame.Minutes: 525600,
        TimeFrame.Days: 365,
    })
