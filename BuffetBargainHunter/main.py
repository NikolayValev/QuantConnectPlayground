# region imports
from AlgorithmImports import *

from universe import LowPBRatioUniverseSelectionModel
from alpha import ValueAlphaModel
# endregion


class BuffetBargainHunterAlgorithm(QCAlgorithm):

    _undesired_symbols_from_previous_deployment = []
    _checked_symbols_from_previous_deployment = False

    def initialize(self):
        self.set_end_date(datetime.now())
        self.set_start_date(self.end_date - timedelta(5*365))
        self.set_cash(1_000_000)
        
        self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE, AccountType.MARGIN)

        self.settings.minimum_order_margin_portfolio_percentage = 0

        self.set_security_initializer(BrokerageModelSecurityInitializer(self.brokerage_model, FuncSecuritySeeder(self.get_last_known_prices)))

        self.universe_settings.data_normalization_mode = DataNormalizationMode.RAW
        self.universe_settings.schedule.on(self.date_rules.month_start())
        self.add_universe_selection(LowPBRatioUniverseSelectionModel(
            self.universe_settings,
            self.get_parameter("coarse_size", 500),
            self.get_parameter("fine_size", 250)
        ))

        self.add_alpha(ValueAlphaModel(self.get_parameter("portfolio_size", 100)))

        self.set_portfolio_construction(EqualWeightingPortfolioConstructionModel(self))

        self.add_risk_management(NullRiskManagementModel())

        self.set_execution(ImmediateExecutionModel()) 

        self.set_warm_up(timedelta(31))

    def on_data(self, data):
        # Exit positions that aren't backed by existing insights.
        # If you don't want this behavior, delete this method definition.
        if not self.is_warming_up and not self._checked_symbols_from_previous_deployment:
            for security_holding in self.portfolio.values():
                if not security_holding.invested:
                    continue
                symbol = security_holding.symbol
                if not self.insights.has_active_insights(symbol, self.utc_time):
                    self._undesired_symbols_from_previous_deployment.append(symbol)
            self._checked_symbols_from_previous_deployment = True
        
        for symbol in self._undesired_symbols_from_previous_deployment:
            if self.is_market_open(symbol):
                self.liquidate(symbol, tag="Holding from previous deployment that's no longer desired")
                self._undesired_symbols_from_previous_deployment.remove(symbol)
