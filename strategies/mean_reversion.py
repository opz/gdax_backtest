from backtrader import Strategy, Order
from backtrader.indicators import BollingerBands, SimpleMovingAverage, MACD
from backtrader.sizers import PercentSizer

from indicators.movingadf import MovingADF


class MeanReversionStrategy(Strategy):
    """
    Mean reversion strategy based on Bollinger Band signals

    Parameters:
        period: The lookback period for indicators.
        devfactor: The number of standard deviations to use
            with bollinger bands.
        adf_threshold: The maximum Dickey-Fuller p-value during which
            trading occurs.
        percent_stake: The percentage of the total stake to use for each
            trade made by the strategy.
    """

    params = (
        ('period', 60),
        ('devfactor', 2),
        ('adf_threshold', 0.5),
        ('percent_stake', 90),
    )

    def __init__(self):
        self.buyorder = None
        self.buyorder_executed = None

        self.sellorder = None
        self.sellorder_executed = None

        self.bbands = BollingerBands(self.data, period=self.p.period,
                devfactor=self.p.devfactor, movav=SimpleMovingAverage)

        self.movadf = MovingADF(self.data, period=self.p.period,
                dupe_period=self.p.period)

        self.macd = MACD(
            period_me1=self.p.period // 2,
            period_me2=self.p.period,
            period_signal=self.p.period // 3
        )

        self.sizer = PercentSizer(percents=self.p.percent_stake)

    def notify_order(self, order):
        """
        Handle order event

        Only one position is open at a time.

        :param order: the order generating the event
        """

        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:

            if order.isbuy():
                # Indicate that a position has been open
                self.buyorder_executed = order

                print('BUY EXECUTED PRICE: {:.2f}'.format(order.executed.price))

            if order.issell():
                # Clear out closed positions so new ones can be opened
                self.buyorder = None
                self.buyorder_executed = None
                self.sellorder = None

                print('SELL EXECUTED PRICE: {:.2f}'.format(order.executed.price))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            return

    def next(self):
        """
        Process the next tick in the time series

        Buy and sell orders are sent based on Bollinger Band signals. Trading
        only occurs when indicators are showing potentially mean reverting
        price behaviour.

        All orders placed are limit orders. When an order is unfulfilled, and
        a repeat buy/sell signal is detected, the order is reissued at the
        updated price.
        """

        # Check indicators for potentially mean reverting price behaviour
        movadf_threshold = self.movadf.lines.movadf[0] < self.p.adf_threshold
        macd_threshold = self.macd.lines.macd[0] < 0

        # If a position is still open...
        if self.buyorder_executed:

            # Check for a sell signal from the Bollinger Bands indicator
            if self.data.close[0] > self.bbands.lines.top[0]:

                # If an existing sell order is still unfulfilled, cancel it
                if self.sellorder:
                    self.cancel(self.sellorder)

                # Issue a limit sell order at the latest price
                self.sellorder = self.close(exectype=Order.Limit)

                print('SELL, Close: {:.2f}, Middle: {:.2f}'.format(self.data.close[0], self.bbands.lines.mid[0]))

        # If no positions are open and price behaviour is mean reverting...
        elif movadf_threshold and macd_threshold:

            # Check for a buy signal from the Bollinger Bands indicator
            if self.data.close[0] < self.bbands.lines.bot[0]:

                # If an existing buy order is still unfulfilled, cancel it
                if self.buyorder:
                    self.cancel(self.buyorder)

                # Issue a limit buy order at the latest price
                self.buyorder = self.buy(exectype=Order.Limit)

                print('BUY, Close: {:.2f}, Bottom: {:.2f}'.format(self.data.close[0], self.bbands.lines.bot[0]))
