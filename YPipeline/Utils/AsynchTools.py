from asyncio import Semaphore
from typing import Tuple, Union

import pandas as pd
from termcolor import colored

from aiohttp import ClientError, ClientSession
from aiohttp.http import HttpProcessingError

from .. import log
from .ParseTools import parse_prices


async def fetch(url: str, params: dict, session: ClientSession) -> dict:
    """
    Asynchronous fetching of urls.

    Parameters:
    -----------
    url: str
        url to fetch
    params: dict
        parameters for request
    session: ClientSession
        aiohttp client session
    return: dict
        json repsonse
    """
    async with session.get(url, params=params) as response:
        if response.status == 200:
            color: str = "green"
            log.debug(
                colored(
                    f"{url.split('/')[-1]:8} - {response.status} - {params.get('interval', '')} {params.get('t', '')}",
                    color,
                )
            )
        else:
            color = "red"
            log.info(
                colored(
                    f"{url.split('/')[-1]:8} - {response.status} - {params.get('interval', '')} {params.get('t', '')}",
                    color,
                )
            )
        json = await response.json()

        return json


async def bound_fetch(sem: Semaphore, url: str, params: dict, session: ClientSession):
    """
    Method to restric the open files (request) in asynch fetch.

    REF: https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html

    sem: Semaphore
        internal counter https://docs.python.org/3/library/asyncio-sync.html#asyncio.Semaphore
    url: str
        url to download
    params: dict
        parameters for request
    session: ClientSession
        aiohttp client session
    return: dict
        json response

    """
    async with sem:
        return await fetch(url, params, session)


async def aparse_summary(sem: Semaphore, symbol: str, session: ClientSession) -> dict:
    """
    Simple method to read summary table from Yahoo main page
    for a symbol.

    Parameters:
    -----------
    sem: Semaphore
    symbol: str
        Yahoo finance symbol
    session: ClientSession
    return: dict
        dict version of the summary table
    """
    url_summ = "https://finance.yahoo.com/quote/"
    url = url_summ + symbol

    try:
        resp = await bound_fetch(sem, url, {}, session)
        df = pd.concat(pd.read_html(resp.text()))
        df.columns = ["key", "value"]

        return dict(zip(df.key.values, df["value"].values))

    except (ClientError, HttpProcessingError) as e:
        log.error(
            "aiohttp exception for %s [%s]: %s",
            url,
            getattr(e, "status", None),
            getattr(e, "message", None),
        )

        return {}

    except Exception as e:
        log.info(e)
        # logger.exception(
        #     "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        # )
        log.exception(colored(f"{url.split('/')[-1]}", "red"))

        return {}


async def aparse_prices(
    sem: Semaphore, tup: Tuple[str, dict], session: ClientSession
) -> Tuple[
    Union[str, None],
    Union[pd.DataFrame, None],
    Union[pd.DataFrame, None],
    Union[pd.DataFrame, None],
]:
    """
    Asynch getting and parsing of yahoo prices.

    sem: Semaphore
        internal counter for open files
    tup: Tuple[str, dict]
        (url, parameters for request dict)
    session: ClientSession
        aoihttp client session
    return: Tuple
        (interval, price data, dividens, splits)

    """
    try:
        url, params = tup
        resp = await bound_fetch(sem, url, params, session)
        resp = resp["chart"]["result"][0]
        interval, pricedata, div, split = parse_prices(resp)

        log.debug(
            colored(f"{url.split('/')[-1]:8} - interval {interval} - OK", "green")
        )

        return interval, pricedata, div, split

    except (ClientError, HttpProcessingError) as e:
        log.error(
            "aiohttp exception for %s [%s]: %s",
            tup[0],
            getattr(e, "status", None),
            getattr(e, "message", None),
        )

        return None, None, None, None

    except Exception as e:
        log.info(e)
        # logger.exception(
        #     "Non-aiohttp exception occured:  %s", getattr(e, "__dict__", {})
        # )
        log.exception(colored(f"{tup[0].split('/')[-1]}", "red"))

        return None, None, None, None
