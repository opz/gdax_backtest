import array

from statsmodels.tsa.stattools import adfuller

from backtrader import Indicator


class MovingADF(Indicator):
    """
    Moving Augmented Dickey-Fuller indicator

    Instead of recalculating the formula for every single timestep, a single
    set of statistics is calculated and reused over a certain period. This
    design decision improves the backtesting runtime at the cost of introducing
    look-ahead bias.

    Parameters:
        period: The lookback period for calculating Augmented Dickey-Fuller.
        dupe_period: The period to reuse calculated statistics for.

    Lines:
        movadf: The calculated statistics for each time step.
    """

    lines = ('movadf',)

    params = (
        ('period', 20),
        ('dupe_period', 20),
    )

    def __init__(self):
        # Get array contained in line object
        close = self.data.close.array

        movadf = array.array('f', [float('nan')] * len(close))

        # Loop through dupe_period long sections of the array
        for i in range(self.p.period, len(close), self.p.dupe_period):

            # Calculate Dickey-Fuller statistics
            results = adfuller(close[i - self.p.period:i])

            # Reuse statistics across entire section
            for j in range(i - self.p.dupe_period, i):
                movadf[j] = results[1]

        # Assign new array to the indicator line
        self.lines.movadf.array = movadf
