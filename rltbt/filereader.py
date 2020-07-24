'''
The function parse_csv() turns a SierraChart output txt file into a pandas DataFrame. It also adds three extra columns: date, time, and datetime for the convenience of frequent date/time operations.

Input:
    path:       indicating the file path.
    extra_col:  optional. A list indicating the extra columns that one needs to keep.

Output:
    a pandas Dataframe with columns: date, time, datetime, open, high, low, last, volume, num of trades, (extra columns indicated by the user)
'''
import pandas as pd
from datetime import datetime, date, time

def parse_csv(path: str, extra_col: list=[]):

    data_df = pd.read_csv(path, skipinitialspace = True)

    data_df.rename(columns = {'Date':'date', 'Time':'time', 'Open':'open', 'High':'high', \
                              'Low':'low', 'Last':'last', 'Volume':'volume', '# of Trades':'num of trades'}, inplace = True)

    input_df = data_df[['date', 'time', 'open', 'high', 'low', 'last', 'volume', 'num of trades'] + extra_col].copy() # copy the selected dataframe

    # Turns date, time into date and time objects, and combine to get a datetime object in the new column 'datetime'
    input_df['date'] = input_df['date'].apply(lambda x: datetime.strptime(x.strip(), '%Y/%m/%d').date())
    input_df['time'] = input_df['time'].apply(lambda x: datetime.strptime(x.strip().split('.', 1)[0], '%H:%M:%S').time())
    input_df['datetime'] = input_df.apply(lambda x: datetime.combine(x['date'], x['time']), axis = 1)

    return input_df
