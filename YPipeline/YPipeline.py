# -*- coding: utf-8 -*-

base_url = "https://query2.finance.yahoo.com/v8/finance/"


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


class YahooManual:
    def __init__(self, symbols: Symbols):
        self._symbols = symbols
        self._cache = None
    
    