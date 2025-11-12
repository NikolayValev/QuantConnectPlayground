#region imports
from AlgorithmImports import *
#endregion


class ValueAlphaModel(AlphaModel):
    
    _securities = []
    _month = -1

    def __init__(self, portfolio_size):
        self._portfolio_size = portfolio_size

    def update(self, algorithm: QCAlgorithm, data: Slice) -> List[Insight]:
        # Only rebalance when there is QuoteBar data
        if data.quote_bars.count == 0:
            return []
        
        # Rebalance monthly
        if self._month == data.time.month:
            return []
        self._month = data.time.month
        
        # Create insights to long the securities with the lowest price-to-book ratio
        insights = []
        tradable_securities = [security for security in self._securities if security.symbol in data.quote_bars and security.price > 0 and security.fundamentals]
        for security in sorted(tradable_securities, key=lambda security: security.fundamentals.valuation_ratios.pb_ratio)[:self._portfolio_size]:
            insights.append(Insight.price(security.symbol, Expiry.END_OF_MONTH, InsightDirection.UP))
        return insights

    def on_securities_changed(self, algorithm: QCAlgorithm, changes: SecurityChanges) -> None:
        for security in changes.removed_securities:
            if security in self._securities:
                self._securities.remove(security)
        self._securities.extend(changes.added_securities)
