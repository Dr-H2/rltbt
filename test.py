import rltbt.indicators
from rltbt.filereader import parse_csv
from rltbt.trade import *

import pandas as pd
import numpy as np

TICK_SIZE=.25
indicator = rltbt.indicators.Indicators()
input_df = parse_csv('~/python_work/SkynetTheMarketCrusher/data/ESU0-test.csv')

result = get_trade_result(input_df[['time', 'open', 'high', 'low', 'last']].values, going_long=True, stop_offset=25, target_offset=50, TICK_SIZE=TICK_SIZE, use_trailing=True, trailing_offset=25, slippage=1)
input_df['long result'] = result
result = get_trade_result(input_df[['time', 'open', 'high', 'low', 'last']].values, going_long=False, stop_offset=25, target_offset=50, TICK_SIZE=TICK_SIZE, use_trailing=True, trailing_offset=25, slippage=1)
input_df['short result'] = result
print(input_df[:30][['time', 'open', 'high', 'low', 'last', 'long result', 'short result']])
