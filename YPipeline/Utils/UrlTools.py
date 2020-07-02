# -*- coding: utf-8 -*
from datetime import datetime as dt
from typing import List, Optional, Union

from .DateTimeTools import clean_start_end_period

base_url = "https://query2.finance.yahoo.com/v8/finance/"

valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

valid_intevals = [
    "1m",
    "2m",
    "5m",
    "15m",
    "30m",
    "90m",
    "1h",
    "1d",
    "5d",
    "1wk",
    "1mo",
    "3mo",
    "all",
]


class InvalidPeriodError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "InvalidPeriodError, {0} ".format(self.message)
        else:
            return "InvalidPeriodError: Invalid period for price time-series."


class InvalidIntervalError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "InvalidIntervalError, {0} ".format(self.message)
        else:
            return "InvalidIntervalError: Invalid interval for price time-series."


def generate_price_urls(symbollist: list) -> list:
    """
    Method to generate yahoo price urls.

    Parameters:
    -----------
    symbollist: list 
        list of valid yahoo symbols

    return: list
        list of urls

    """
    return [f"{base_url}chart/{symbol}" for symbol in symbollist]


def generate_price_params(
    _period: str,
    _interval: str,
    _start: Optional[Union[dt, str, int]],
    _end: Optional[Union[dt, str, int]],
) -> List[dict]:
    """
    Private method to generate parameter
    dictionary to pass to requests for
    downloading the historical price data.

    Parameters:
    -----------
    _period: str
        historical time period
    _interval: str
        time series interval value
    _start: str|int|datetime.datetime
        optional start date
    _end: str|int|datetime.datetime  
        optional end date

    return: 
        list of dictionaries with parameter settings

    """
    paramslist = []

    # CASE SINGLE INTERVAL IS REQUESTED
    if _interval != "all":
        # RESTRICT PERIODS IF NECESSARY
        if _interval == "1m":
            if valid_periods.index(_period) < valid_periods.index("5d"):
                _period = _period
            else:
                _period = "5d"

        elif _interval[-1] == "m" or _interval[-1] == "h":
            if valid_periods.index(_period) < valid_periods.index("1mo"):
                _period = _period
            else:
                _period = "1mo"
        elif _period is None:
            _period = "max"
        else:
            _period = _period

        # SET UP PARAMETERS
        params = clean_start_end_period(_start, _end, _period)
        params["includePrePost"] = 1
        params["events"] = "div,splits"
        params["interval"] = _interval.lower()

        paramslist.append(params.copy())

    # CASE ALL INTERVALS ARE REQUESTED
    else:
        for interval in valid_intevals[:-1]:
            # RESTRICT PERIODS IF NECESSARY
            if interval == "1m":
                if valid_periods.index(_period) < valid_periods.index("5d"):
                    _period = _period
                else:
                    _period = "5d"
            elif interval[-1] == "m" or interval[-1] == "h":
                if valid_periods.index(_period) < valid_periods.index("1mo"):
                    _period = _period
                else:
                    _period = "1mo"
            elif _period is None:
                _period = "max"
            else:
                _period = _period
            params = clean_start_end_period(_start, _end, _period)
            params["includePrePost"] = 1
            params["events"] = "div,splits"
            params["interval"] = interval.lower()

            paramslist.append(params.copy())

    return paramslist
