'''
Class Indicators encapsulates all the indicators.

Currently available indicators:
    ema:            Exponential Moving Average
                    required parameter: length

    ma:             Simple Moving Average
                    required parameter: length

    study_angle:    Study Angle
                    required parameters: length, value_per_point

    cci:            Commodity Channel Index
                    required parameter: length
                    optional parameters: moving_average, multiplier

    t3:             T3 indicator
                    required parameter: length
                    optional parameters: moving_average, multiplier

Usage:
    Call Indicators.indicator() to get the results.

Input for Indicators.indicator() method:
    data: the input data. It can be a pandas Series, numpy array or a list.
    indicator_name: a string indicating the name of the indicator.
    (extra parameters): for each indicator, it has a specific set of input parameters like 'length'. Specify them after the indicator_name.

'''

import pandas as pd
import numpy as np


class Indicators:

    def __init__(self):
        self._moving_average_table = {'ma': self._ma, 'ema': self._ema} # add to the list if a new moving average is programmed

    def _ema(self, inp, length):

        assert isinstance(inp, list) or isinstance(inp, np.ndarray)
        c = 2 / (length + 1)
        result = []
        for i in range(len(inp)):
            if i == 0:
                result.append(inp[0])
            elif i < length - 1:
                if result[-1] == 0:
                    result.append( 2 / (i + 2) * inp[i] + (1 - 2 / (i + 2)) * inp[i-1] )
                else:
                    result.append( 2 / (i + 2) * inp[i] + (1 - 2 / (i + 2)) * result[-1] )
            else:
                if result[-1] == 0:
                    result.append( c * inp[i] + (1 - c) * inp[i-1] )
                else:
                    result.append( c * inp[i] + (1 - c) * result[-1] )
        return result

    def _ma(self, inp, length):

        assert isinstance(inp, list) or isinstance(inp, np.ndarray)
        result = []
        rolling_sum = 0
        for i in range(len(inp)):
            if i < length:
                rolling_sum = rolling_sum + inp[i]
                result.append( rolling_sum / (i + 1) )
            else:
                rolling_sum = rolling_sum + inp[i] - inp[i - length]
                result.append( rolling_sum / length )
        return result

    def _study_angle(self, inp, length, value_per_point):

        assert isinstance(inp, list) or isinstance(ind, np.ndarray)
        result = []
        for i in range(len(inp)):
            if i < length:
                result.append(0)
            elif i >= length:
                result.append( math.atan( (inp[i] - inp[i - length]) / (length * value_per_point) ) * 180 / math.pi )
        return result

    def _cci(self, inp, length, moving_average=None, multiplier = .015):

        assert isinstance(inp, list) or isinstance(inp, np.ndarray)
        if moving_average == None: # default to simple moving average
            moving_average = self._ma
        result = []
        ma_list = moving_average(inp, length)
        for i in range(len(inp)):
            if i < length:
                denom = 0
                for j in range(i + 1):
                    denom = denom + abs( ma_list[i] - inp[j] )
                if denom == 0:
                    denom = 1e-5 #Avoid division by zero
                result.append( (inp[i] - ma_list[i]) / denom * (i + 1) / multiplier )
            else:
                denom = 0
                for j in range(i - length + 1, i + 1):
                    denom = denom + abs( ma_list[i] - inp[j] )
                if denom == 0:
                    denom = 1e-5 #Avoid division by zero
                result.append( (inp[i] - ma_list[i]) / denom * length / multiplier )
        return result

    def _t3(self, inp, length, moving_average=None, multiplier=.84):

        assert isinstance(inp, list) or isinstance(inp, np.ndarray)
        if moving_average == None: # default to ema
            moving_average = self._ema
        result = []
        emas = [np.array(moving_average(inp, length))]
        for i in range(1, 6):
            emas.append(np.array(moving_average(emas[-1], length)))
        result = -(multiplier ** 3) * emas[5] + \
                  3 * (multiplier ** 2) * (1 + multiplier) * emas[4] - \
                  3 * multiplier * ((1 + multiplier) ** 2) * emas[3] + \
                  ((1 + multiplier) ** 3) * emas[2]
        return list(result)



    def indicator(data, indicator_name, **kwargs):

        inp = data
        result = []
        if isinstance(inp, pd.core.series.Series):
            inp = inp.tolist()
        elif isinstance(inp, list) or isinstance(inp, np.ndarray):
            pass
        else:
            raise TypeError(f'The type {type(inp)} of the input data is not supported.')
        ###### remark: I can let it handle DataFrame if there is the need. So far there is no need.


        if isinstance(indicator_name, str):
            if indicator_name.lower() == 'ma':
                length = self._get_length(kwargs)
                result = self._ma(inp, length)

            elif indicator_name.lower() == 'ema':
                length = self._get_length(kwargs)
                result = self._ema(inp, length)

            elif indicator_name.lower() == 'study angle':
                length = self._get_length(kwargs)
                value_per_point = self._get_value_per_point(kwargs, default=1.)
                result = self._study_angle(inp, length, value_per_point)

            elif indicator_name.lower() == 'cci':
                length = self._get_length(kwargs)
                moving_average = self._get_moving_average(kwargs, default=self._ma)
                multiplier = self._get_multiplier(kwargs, default=.015)
                result = self._cci(inp, length, moving_average = moving_average, multiplier = multiplier)

            elif indicator_name.lower() == 't3':
                length = self._get_length(kwargs)
                moving_average = self._get_moving_average(kwargs, default=self._ema)
                multiplier = self._get_multiplier(kwargs, default=.84)
                result = self._t3(inp, length, moving_average = moving_average, multiplier = multiplier)

            else:
                raise NameError('The indicator is unspecified or unsupported.')
        else:
            raise TypeError('The indicator name must be a string.')


        if type(data) == pd.core.series.Series:
            return pd.Series(result)
        else:
            return result

    # private functions to get parameters and raise the correct error
    # maybe it's not necessary. I put return None after each error.

    def _get_length(self, kwargs, mandatory=True): # no default length here.
        if 'length' not in param.keys() and mandatory:
            raise NameError(f'Length must be specified.')
            return None
        elif not isinstance(param['length'], int):
            raise TypeError('Length must be an integer.')
            return None
        elif param['length'] <= 0:
            raise ValueError('Length must be a positive integer.')
            return None
        return param['length']

    def _get_moving_average(self, kwargs, default=None, mandatory=False): # default is simple moving average
        if 'moving_average' not in kwargs:
            if mandatory:
                raise NameError('moving_average must be specified.')
            if default == None:
                return self._ma
            else:
                return default
        elif kwargs['moving_average'] in self._moving_average_table:
            return self._moving_average_table[kwargs['moving_average']]
        else:
            raise ValueError('The moving average keyword is not recognized.')
            return None

    def _get_multiplier(self, kwargs, default=.015, mandatory=False):
        if 'multiplier' not in kwargs:
            if mandatory:
                raise NameError('multiplier must be specified.')
            return default
        elif isinstance(kwargs['multiplier'], int) or isinstance(kwargs['multiplier'], float):
            return kwargs['multiplier']
        else:
            raise TypeError('multiplier must be an integer or float.')
            return None

    def _get_value_per_point(kwargs, default=1., mandatory=False):
        if 'value_per_point' not in kwargs:
            if mandatory:
                raise NameError('value_per_point must be specified.')
            return default
        elif isinstance(kwargs['value_per_point'], int) or isinstance(kwargs['value_per_point'], float):
            return kwargs['value_per_point']
        else:
            raise ValueError('value_per_point must be an integer or float.')
