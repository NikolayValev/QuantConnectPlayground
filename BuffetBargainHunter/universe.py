# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from AlgorithmImports import *
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class LowPBRatioUniverseSelectionModel(FundamentalUniverseSelectionModel):
    
    def __init__(self, universe_settings: UniverseSettings = None, coarse_size: int = 500, fine_size: int = 5) -> None:
        super().__init__(universe_settings)
        self.coarse_size = coarse_size
        self.fine_size = fine_size

    def select(self, algorithm: QCAlgorithm, fundamentals: Iterable[Fundamental]) -> Iterable[Symbol]:
        fundamentals = [f for f in fundamentals if f.has_fundamental_data and f.valuation_ratios.pb_ratio != 0]
        sorted_by_dollar_volume = sorted(fundamentals, key=lambda c: c.dollar_volume)[-self.coarse_size:]
        return [c.symbol for c in sorted(sorted_by_dollar_volume, key=lambda x: x.valuation_ratios.pb_ratio)[:self.fine_size]]