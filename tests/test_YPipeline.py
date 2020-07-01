from YPipeline.Utils.DateTimeTools import validate_date


def test___validate_date():
    validate_date("2020-01-01")
    assert True
