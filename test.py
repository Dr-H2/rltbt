import rltbt.indicators
from rltbt.filereader import parse_csv
import pandas as pd
import numpy as np

indicator = rltbt.indicators.Indicators()
df = parse_csv('~/python_work/SkynetTheMarketCrusher/data/ESU0-test.csv')
print(df.head(20))
