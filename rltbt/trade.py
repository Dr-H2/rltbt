import pandas as pd
import numpy as np
from datetime import datetime, date, time



###### The following function checks whether we are within the allowed time period to trade. Feel free to modify the start and end time.
def in_trading_hour(tt):
    if tt < time(18,0,0) and tt > time(16,5,0):
        return False
    return True


def get_trade_result(indices, inp, going_long = True, stop_offset = 12, target_offset = 12):

    ######indices is a list of indices of candles that we will test on.
    ######inp format: time, high, low, last
    ######if going_long is False, we go short.
    ######stop_offset and target_offset are in ticks.

    result = []
    TIME, HIGH, LOW, LAST = 0, 1, 2, 3

    for i in range(len(indices)):
        ind = indices[i]
        if (i == len(indices) - 1) or not in_trading_hour(inp[ind][TIME]):
            result.append(0)
            continue

        entry = inp[ind][LAST]
        if going_long:
            stop = entry - stop_offset * TICK_SIZE
            target = entry + target_offset * TICK_SIZE
        else:
            stop = entry + stop_offset * TICK_SIZE
            target = entry - target_offset * TICK_SIZE

        flag = 0 #If the trade can hit target/stop within trading hour, flag=1

        ######The following loop will break if one of the following happens:
        ######    The next candle is the last candle in the data file;
        ######    The next candle is outside trading hour;
        ######    The next candle is a different trading day (not calendar day).
        ind = ind + 1
        while ind + 1 < len(inp) and in_trading_hour(inp[ind+1][TIME]) and not (inp[ind][TIME].hour <= 16 and inp[ind+1][TIME].hour >= 18):
            ######going_long is a boolean value, but it can be converted to a number. True is 1 and False is 0.
            ######The following is just a slick trick to detect whether we hit the target/stop and it works for both long and short.
            if going_long * inp[ind][HIGH] - (1 - going_long) * inp[ind][LOW] >= (2 * going_long - 1) * target:
                result.append(target_offset * TICK_SIZE)
                flag = 1
                break
            if going_long * inp[ind][LOW] - (1 - going_long) * inp[ind][HIGH] <= (2 * going_long - 1) * stop:
                result.append(-stop_offset * TICK_SIZE)
                flag = 1
                break
            ind = ind + 1

        ######If the above loop breaks without hitting target/stop, we exit at the close of the current candle.
        if flag == 0:
            result.append((2 * going_long - 1) * (inp[ind][LAST] - entry))

    return result

###### The following function get the maximal drawdown. There should be a better way than looping through the array
def max_drawdown(inp):
    max_dd = 0
    max_runup = 0
    for i in range(len(inp)):
        max_runup = max(max_runup, inp[i])
        #if max_runup - inp[i] > max_dd: print(i, inp[i]) #This command is for debug only. It displays the P&L when it breaks through the previous max_dd
        max_dd = max(max_dd, max_runup - inp[i])

    return max_dd
