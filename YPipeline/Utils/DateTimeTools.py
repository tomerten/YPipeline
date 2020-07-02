import time
from datetime import datetime as dt
from typing import Dict, Optional, Union


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


def validate_date(_date: Union[dt, str]) -> None:
    """
    Validation of date. Date in string or datetime
    format are accepted.

    Parameters:
    _date: str, datetime.datetime
        date the validate

    """
    if isinstance(_date, str):
        try:
            dt.strptime(_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Incorrect date str format")
    elif isinstance(_date, dt):
        pass
    else:
        raise TypeError("Invalid date type!")


def clean_start_end_period(
    start: Optional[Union[dt, str, int]],
    end: Optional[Union[dt, str, int]],
    period: Optional[str],
) -> Dict[str, Union[str, int]]:
    """
    Method to clean up start and end positions
    for getting yahoo historical price data.

    Parameters:
    -----------
    start: None|str|datetime
        start date of requested time window
    end: None|datetime|str
        end of requested time window
    period: str 
        interval period of time series

    return: dict
        parameter dict for request

    """
    if start or period is None or period.lower() == "max":
        if start is None:
            start = 0
        elif isinstance(start, dt):
            start = int(time.mktime(start.timetuple()))
        else:
            start = int(time.mktime(time.strptime(str(start), "%Y-%m-%d")))
        if end is None:
            end = int(time.time())
        elif isinstance(end, dt):
            end = int(time.mktime(end.timetuple()))
        else:
            end = int(time.mktime(time.strptime(str(end), "%Y-%m-%d")))

        # ANNOTATION NECESSARY TO PASS MYPY TESTS
        params: Dict[str, Union[str, int]] = {"period1": start, "period2": end}
    else:
        period = period.lower()
        params = {"range": period}

    return params
