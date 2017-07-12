#!/usr/bin/env python3

import argparse

import backtrader as bt

from analyzers.sharpe import SharpeRatio
from analyzers.returns import Returns
from feeds.gdaxcsv import GDAXCSVData
from strategies.mean_reversion import MeanReversionStrategy


def get_args():
    """
    Parse command line arguments

    :returns: tuple(gdax_data, timeframe)
        - gdax_data: filename of GDAX CSV
        - timeframe: GDAX data timeframe
    :rtype: tuple(string, int)
    """

    # Initialize argparse, use raw text so help can include newline characters
    DESCRIPTION = 'Backtest a GDAX trading strategy.'
    parser = argparse.ArgumentParser(description=DESCRIPTION,
            formatter_class=argparse.RawTextHelpFormatter)

    #
    # GDAX CSV FILE ARGUMENT
    #

    CSV_ARG = 'csv_file'
    CSV_HELP = 'CSV file of GDAX data'

    parser.add_argument(CSV_ARG, help=CSV_HELP)

    #
    # TIMEFRAME ARGUMENT
    #

    TIMEFRAME_ARG = 't'
    TIMEFRAME_ARG_FULL = '-' + TIMEFRAME_ARG
    TIMEFRAME_CHOICES = [
        bt.TimeFrame.Minutes,
        bt.TimeFrame.Days,
        bt.TimeFrame.Weeks,
        bt.TimeFrame.Months,
        bt.TimeFrame.Years,
    ]
    TIMEFRAME_HELP = 'Timeframe used for GDAX data.\n'

    # Describe the mapping between each timeframe and its integer flag
    for i, choice in enumerate(TIMEFRAME_CHOICES):
        choice_name = bt.TimeFrame.getname(choice, 1)
        TIMEFRAME_HELP += '{:d}: {}'.format(choice, choice_name)

        # Mark the default setting
        if i == 0:
            TIMEFRAME_HELP += ' (default)'

        TIMEFRAME_HELP += '\n'

    parser.add_argument(TIMEFRAME_ARG_FULL, type=int, choices=TIMEFRAME_CHOICES,
            default=TIMEFRAME_CHOICES[0], help=TIMEFRAME_HELP)

    #
    # RETRIEVE ARGUMENTS
    #

    args = parser.parse_args()

    gdax_data = getattr(args, CSV_ARG)
    timeframe = getattr(args, TIMEFRAME_ARG)

    return gdax_data, timeframe


if __name__ == '__main__':
    gdax_data, timeframe = get_args()

    data = GDAXCSVData(
        dataname=gdax_data,
        timeframe=timeframe,
    )

    cerebro = bt.Cerebro()

    cerebro.addstrategy(MeanReversionStrategy)

    cerebro.addanalyzer(Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    RISKFREERATE = 0.04
    cerebro.addanalyzer(SharpeRatio, _name='sharperatio',
            timeframe=timeframe, riskfreerate=RISKFREERATE,
            annualize=True)

    cerebro.adddata(data)

    strats = cerebro.run()
    strat = strats[0]

    strat.analyzers.returns.pprint()
    strat.analyzers.drawdown.pprint()
    strat.analyzers.sharperatio.pprint()

    cerebro.plot()
