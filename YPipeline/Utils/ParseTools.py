from typing import Tuple, Union

import numpy as np
import pandas as pd

from .. import log


def parse_quotes_as_frame(data: dict) -> pd.DataFrame:
    """
    Private method to parse raw yahoo price data
    into a dataframe.

    :param data: raw yahoo json data
    :type data: dict
    :return: dataframe version of the data
    :rtype: pd.DataFrame
    """
    # GET INFO FROM THE METADATA
    try:
        symbol, exchange, currency, interval, priceHint = tuple(
            data.get("meta", {}).get(i)
            for i in [
                "symbol",
                "exchangeName",
                "currency",
                "dataGranularity",
                "priceHint",
            ]
        )

        date_list = data["timestamp"]
        ohlc_list = data["indicators"]["quote"][0]

        volume_list = ohlc_list["volume"]
        open_list = ohlc_list["open"]
        close_list = ohlc_list["close"]
        low_list = ohlc_list["low"]
        high_list = ohlc_list["high"]

        quotes = pd.DataFrame(
            {
                "open": open_list,
                "high": high_list,
                "low": low_list,
                "close": close_list,
                "volume": volume_list,
            }
        )
        if "adjclose" in data["indicators"]:
            adjclose_list = data["indicators"]["adjclose"][0]["adjclose"]
        else:
            adjclose_list = close_list

        quotes["adjclose"] = adjclose_list
        quotes["symbol"] = symbol
        quotes["currency"] = currency
        quotes["exchange"] = exchange

        quotes.index = pd.to_datetime(date_list, unit="s")
        quotes.sort_index(inplace=True)

        # ROUND ALL THE VALUES IN THE FRAME TO
        # FIXED NUMBER OF DECIMALS - EXTRACTED FROM
        # METADATA
        quotes = np.round(quotes, priceHint)

        # REFORMAT VOLUME AS INTEGERS - DATA REDUCTION
        quotes["volume"] = quotes["volume"].fillna(0).astype(np.int64)

        quotes.dropna(inplace=True)

        # SET QUOTES INDEX TO DATETIME USING LOCALIZATION !!!!
        quotes.index = quotes.index.tz_localize("UTC").tz_convert(
            data["meta"]["exchangeTimezoneName"]
        )

        if (interval[-1] == "m") or (interval[-1] == "h"):
            quotes.index = [ts.isoformat() for ts in quotes.index]
            quotes.index.name = "datetime"
        else:
            quotes.index = pd.to_datetime(quotes.index.date)
            quotes.index = [ts.strftime("%Y-%m-%d") for ts in quotes.index]
            quotes.index.name = "date"

        return quotes

    except (TypeError, AttributeError, KeyError, ValueError, IndexError) as e:
        # IF THERE ARE NO TIMESTAMPS RETURN EMPTY FRAME
        # SAME FOR IF THERE IS NO METADATA
        log.info(f"Invalid data {e}")

        quotes = pd.DataFrame(
            columns=["open", "high", "low", "close", "adjclose", "volume"]
        )
        return quotes


def parse_actions_as_frame(
    data: dict,
) -> Union[Tuple[pd.DataFrame, pd.DataFrame], Tuple[None, None]]:
    """
    Private method to parse
    dividends and splits as
    dataframe.

    :param data: raw yahoo action data
    :type data: JSON|dict
    :return: (dividend, splits)
    :rtype: tuple
    """
    try:

        symbol, currency, priceHint = tuple(
            data.get("meta", {}).get(i) for i in ["symbol", "currency", "priceHint"]
        )
        divdc = data["events"].get("dividends", None)
        spldc = data["events"].get("splits", None)

    except (TypeError, AttributeError, ValueError, IndexError):
        # IF THERE ARE NO TIMESTAMPS RETURN EMPTY FRAME
        # SAME FOR IF THERE IS NO METADATA
        log.info(f"Invalid data actions {data}")

        return None, None

    except KeyError:
        # There is no events key
        return None, None

    dividend = None
    split = None

    if divdc:
        try:
            dividend = pd.DataFrame(data=list(divdc.values()))
            dividend.set_index("date", inplace=True)
            dividend.index = pd.to_datetime(dividend.index, unit="s")
            dividend.sort_index(inplace=True)
            dividend.columns = ["dividends"]
            dividend.index = [ts.strftime("%Y-%m-%d") for ts in dividend.index]
            dividend.index.name = "date"
            dividend = np.round(dividend, priceHint)
            dividend["symbol"] = symbol
            dividend["currency"] = currency
        except (KeyError, TypeError, ValueError, AttributeError):
            dividend = None

    if spldc:
        try:
            split = pd.DataFrame(data=list(spldc.values()))
            split.set_index("date", inplace=True)
            split.index = pd.to_datetime(split.index, unit="s")
            split.sort_index(inplace=True)
            split["splits"] = split["numerator"] / split["denominator"]
            split.index = [ts.strftime("%Y-%m-%d") for ts in split.index]
            split.index.name = "date"
            split["symbol"] = symbol
        except (KeyError, TypeError, ValueError, AttributeError):
            split = None

    return dividend, split


def parse_prices(
    data: Union[dict, None]
) -> Tuple[
    Union[str, None],
    Union[pd.DataFrame, None],
    Union[pd.DataFrame, None],
    Union[pd.DataFrame, None],
]:
    """
    Private method to clean price/actions data.

    data:  dict
        raw json data
    return: Tuple
        price time-series interval, prices, dividends and splits
    """
    if data is not None:
        meta = data.get("meta")
        if meta is not None:
            interval = meta.get("dataGranularity")
        else:
            interval = None

        quotes = parse_quotes_as_frame(data)
        dividends, splits = parse_actions_as_frame(data)
        return interval, quotes, dividends, splits
    else:
        return None, None, None, None
