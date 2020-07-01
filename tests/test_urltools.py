import time

import pytest
from pytest import raises

from YPipeline.Utils.UrlTools import (
    base_url,
    generate_price_params,
    generate_price_urls,
)


# PATCH TIME TO GET FIXED NOW (time.time())
@pytest.fixture()
def patchtime(monkeypatch):
    def mytime():
        return 10

    monkeypatch.setattr(time, "time", mytime)


all_interval = [
    {"range": "5d", "includePrePost": True, "events": "div,splits", "interval": "1m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "2m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "5m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "15m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "30m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "90m"},
    {"range": "1mo", "includePrePost": True, "events": "div,splits", "interval": "1h"},
    {
        "period1": 0,
        "period2": 10,
        "includePrePost": True,
        "events": "div,splits",
        "interval": "1d",
    },
    {
        "period1": 0,
        "period2": 10,
        "includePrePost": True,
        "events": "div,splits",
        "interval": "5d",
    },
    {
        "period1": 0,
        "period2": 10,
        "includePrePost": True,
        "events": "div,splits",
        "interval": "1wk",
    },
    {
        "period1": 0,
        "period2": 10,
        "includePrePost": True,
        "events": "div,splits",
        "interval": "1mo",
    },
    {
        "period1": 0,
        "period2": 10,
        "includePrePost": True,
        "events": "div,splits",
        "interval": "3mo",
    },
]
test_price_urls = [
    ([], []),
    (["abc"], [f"{base_url}chart/{'abc'}"]),
    (["a", "b"], [f"{base_url}chart/{'a'}", f"{base_url}chart/{'b'}"]),
]
test_price_params_fail: list = [
    (None, None, None, None),
    (None, None, "a", None),
    (None, None, None, "b"),
    (None, None, None, {}),
    (None, None, {}, None),
    (None, None, None, "01-01-2020"),
    (None, None, "01-01-2020", None),
    ("a", None, None, None),
    ("a", "1m", None, None),
]

test_price_params_pass = [
    (
        "a",
        "b",
        None,
        None,
        [{"range": "a", "includePrePost": 1, "events": "div,splits", "interval": "b"}],
    ),
    (
        "1d",
        "b",
        None,
        None,
        [{"range": "1d", "includePrePost": 1, "events": "div,splits", "interval": "b"}],
    ),
    (
        "a",
        "1d",
        None,
        None,
        [{"range": "a", "includePrePost": 1, "events": "div,splits", "interval": "1d"}],
    ),
    (
        "max",
        "1m",
        None,
        None,
        [
            {
                "range": "5d",
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1m",
            }
        ],
    ),
    (
        "1d",
        "1m",
        None,
        None,
        [
            {
                "range": "1d",
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1m",
            }
        ],
    ),
    (
        "1d",
        "1h",
        None,
        None,
        [
            {
                "range": "1d",
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1h",
            }
        ],
    ),
    (
        "max",
        "1h",
        None,
        None,
        [
            {
                "range": "1mo",
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1h",
            }
        ],
    ),
    (
        None,
        "1d",
        None,
        None,
        [
            {
                "period1": 0,
                "period2": 10,
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1d",
            }
        ],
    ),
    (
        "max",
        "1d",
        None,
        None,
        [
            {
                "period1": 0,
                "period2": 10,
                "includePrePost": 1,
                "events": "div,splits",
                "interval": "1d",
            }
        ],
    ),
    (
        "1d",
        "all",
        None,
        None,
        [
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "1m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "2m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "5m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "15m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "30m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "90m",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "1h",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "1d",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "5d",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "1wk",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "1mo",
            },
            {
                "range": "1d",
                "includePrePost": True,
                "events": "div,splits",
                "interval": "3mo",
            },
        ],
    ),
]


@pytest.mark.parametrize("symbollist,expected", test_price_urls)
def test___generate_price_url__pass(symbollist, expected):
    assert generate_price_urls(symbollist) == expected


@pytest.mark.parametrize("period,interval,start,end", test_price_params_fail)
def test___generate_price_params___fail(patchtime, period, interval, start, end):
    with raises((TypeError, ValueError)):
        generate_price_params(period, interval, start, end)


@pytest.mark.parametrize("period,interval,start,end,expected", test_price_params_pass)
def test___generate_price_params___pass(
    patchtime, period, interval, start, end, expected
):
    assert expected == generate_price_params(period, interval, start, end)
