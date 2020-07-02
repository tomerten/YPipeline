# -*- coding: utf-8 -*-
import itertools
from typing import List

from .Utils.DateTimeTools import validate_date
from .Utils.UrlTools import (
    InvalidIntervalError,
    InvalidPeriodError,
    generate_price_params,
    generate_price_urls,
    valid_intevals,
    valid_periods,
)


class Symbols:
    def __init__(self, yahoo_symbols: List):
        self.symbols = yahoo_symbols

    def add(self, symbol):
        self.symbols.append(symbol)

    def search(self, symbol):
        if symbol in self.symbols:
            return (symbol, self.symbols.index(symbol))

    def delete(self, symbol):
        try:
            self.symbols.remove(symbol)
        except ValueError:
            pass

    def get(self):
        return self.symbols


class YahooManual:
    def __init__(self, symbols: Symbols):
        self._symbols = symbols
        self._cache = None

    def _input_validation(self, period, interval, start, end) -> None:
        """
        Private method to assert of
        input is valid.
        """
        if period not in valid_periods:
            raise InvalidPeriodError

        if interval not in valid_intevals:
            raise InvalidIntervalError

        if start:
            validate_date(start)

        if end:
            validate_date(end)

    @property
    def available_intervals(self):
        return valid_intevals

    @property
    def available_periods(self):
        return valid_periods

    def get(self, symbols, period="max", interval="1d", start=None, end=None):
        if self._cache is None:
            urllist = generate_price_urls(self._symbols.get())
            paramslist = generate_price_params(period, interval, start, end)
            combinations = list(itertools.product(urllist, paramslist))
            return combinations
