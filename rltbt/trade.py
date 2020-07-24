import pandas as pd
import numpy as np
from datetime import datetime, date, time



def in_trading_hour(tt):
    '''
        This function checks whether we are within the allowed time period to trade (pretty much the future market hour without the last hour before close).
    '''

    if tt < time(18,0,0) and tt > time(16,5,0):
        return False
    return True


def get_trade_result(inp, indices=None, going_long=True, stop_offset=12, target_offset=12, TICK_SIZE=.25, enter_on_close=True, slippage=0,
                        use_trailing=False, trailing_offset=12):

    '''
        This function gets all the trade result as a list
        Input:
            inp:                a numpy array of shape (??, 5). The four columns have to be exactly: time (time object), open (float), high (float), low (float), last (float)
            indices:            a list of indices of candle entries that we will test on. By default we test all entries (i.e., indices=range(inp.shape[0])).
            going_long:         True => we go long at the candle entry; False => we go short.
            stop_offset:        the offset for stop loss (in ticks).
            target_offset:      the offset for target (in ticks).
            TICK_SIZE:          a constant number indicating the size of each tick.
            enter_on_close:     True => we enter at the close of the current candle; False => we enter at the open of the next candle
            slippage:           the slippage happening at the entry of each trade (in ticks). Use it to simulate the worst case scenario.
            use_trailing:       True => we trail the stop loss at the close of each candle; False => the stop loss will be fixed and the trailing_offset will be ignored.
            trailing_offset:    the offset of trailing stop
    '''

    if inp.ndim != 2:
        raise ValueError(f'expect input to be 2 dimensional, but get {inp.ndim} dimension.')
    if inp.shape[1] != 5:
        raise ValueError(f'expect an array of shape (??, 5), but get {inp.shape}.')
    if indices is None:
        indices = range(inp.shape[0])

    result = []
    TIME, OPEN, HIGH, LOW, LAST = 0, 1, 2, 3, 4

    for i in range(len(indices)):
        ind = indices[i]
        if (i == len(indices) - 1) or not in_trading_hour(inp[ind][TIME]):
            result.append(0)
            continue

        if enter_on_close or ind + 1 >= len(inp):
            entry = inp[ind][LAST] + (2 * going_long - 1) * slippage * TICK_SIZE
        else:
            entry = inp[ind + 1][OPEN] + (2 * going_long - 1) * slippage * TICK_SIZE

        if going_long:
            stop = entry - stop_offset * TICK_SIZE
            target = entry + target_offset * TICK_SIZE
        else:
            stop = entry + stop_offset * TICK_SIZE
            target = entry - target_offset * TICK_SIZE

        flag = 0 #If the trade can hit target/stop within trading hour, flag becomes 1

        ######The following loop will break if one of the following happens:
        ######    The next candle is the last candle in the data file;
        ######    The next candle is outside the trading hour;
        ######    The next candle is a different trading day (not calendar day).
        while ind + 1 < len(inp) and in_trading_hour(inp[ind+1][TIME]) and not (inp[ind][TIME].hour <= 16 and inp[ind+1][TIME].hour >= 18):

            if ind == indices[i]: # if the current candle is the entry, we do not check stop/target because we just entered at the close.
                ind = ind + 1
                continue

            ######going_long is a boolean value, but it can be converted to a number. True is 1 and False is 0.
            ######The following is just a slick trick to detect whether we hit the target/stop and it works for both long and short.

            tgt_end = going_long * inp[ind][HIGH] - (1 - going_long) * inp[ind][LOW] # equals the high if we go long, and low if we go short
            stp_end = going_long * inp[ind][LOW] - (1 - going_long) * inp[ind][HIGH] # equals the low if we go long, and high if we go short

            if tgt_end >= (2 * going_long - 1) * target:
                result.append((2 * going_long - 1) * (target - entry))
                flag = 1
                break
            if stp_end <= (2 * going_long - 1) * stop:
                result.append((2 * going_long - 1) * (stop - entry))
                flag = 1
                break

            if use_trailing:
                if abs(abs(tgt_end) - stop) > trailing_offset * TICK_SIZE:
                    stop = abs(tgt_end) - (2 * going_long - 1) * trailing_offset * TICK_SIZE # update trailing stop at each candle close

            ind = ind + 1

        ######If the above loop breaks without hitting target/stop, we exit at the close of the current candle.
        if flag == 0:
            if ind == indices[i]: # this only happens when the next candle is already 1) the last candle; 2) outside trading hour; 3) in the next trading day. In this case, the trade shouldn't happen at all.
                result.append(0)
            else:
                result.append((2 * going_long - 1) * (inp[ind][LAST] - entry)) # exit at the close of the current candle.

    return result

def max_drawdown(inp):
    '''
        The following function get the maximal drawdown. There should be a better way than looping through the array.
        For faster iteration, make sure the 'inp' argument is a list.
    '''

    max_dd = 0
    max_runup = 0
    for i in range(len(inp)):
        max_runup = max(max_runup, inp[i])
        #if max_runup - inp[i] > max_dd: print(i, inp[i]) #This command is for debug only. It displays the P&L when it breaks through the previous max_dd
        max_dd = max(max_dd, max_runup - inp[i])

    return max_dd
