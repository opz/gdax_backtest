import collections
import io

from backtrader.feeds import GenericCSVData


class ReversibleCSVData(GenericCSVData):
    """
    Extends :class:`GenericCSVData` with a `reverse` parameter

    Setting the `reverse` parameter to `True` reverses the data feed's order
    as it is read from the CSV.

    Parameters:
        reverse: Set to `True` to reverse the data feed.
    """

    # Automagically extend GenericCSVData.params
    params = (
        ('reverse', False),
    )

    def start(self):
        super(ReversibleCSVData, self).start()

        if not self.p.reverse:
            return

        dq = collections.deque()

        for line in self.f:
            dq.appendleft(line)

        f = io.StringIO(newline=None)
        f.writelines(dq)
        f.seek(0)

        self.f.close()
        self.f = f
