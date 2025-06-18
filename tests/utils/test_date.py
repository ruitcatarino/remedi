from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.utils.date import to_utc


def test_naive_datetime_converted_to_utc():
    """Test that naive datetime is converted to UTC using local_tz."""
    naive_dt = datetime(2023, 6, 15, 12, 0, 0)
    local_tz = "America/New_York"

    result = to_utc(naive_dt, local_tz)

    assert result.tzinfo == ZoneInfo("UTC")
    # In June, NYC is UTC-4 (EDT), so 12:00 EDT = 16:00 UTC
    assert result == datetime(2023, 6, 15, 16, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_naive_datetime_winter_time():
    """Test naive datetime conversion during standard time (winter)."""
    naive_dt = datetime(2023, 1, 15, 12, 0, 0)
    local_tz = "America/New_York"

    result = to_utc(naive_dt, local_tz)

    # In January, NYC is UTC-5 (EST), so 12:00 EST = 17:00 UTC
    assert result == datetime(2023, 1, 15, 17, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_aware_datetime_converted_to_utc():
    """Test that timezone-aware datetime is converted to UTC."""
    tz = ZoneInfo("Europe/London")
    aware_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=tz)

    result = to_utc(aware_dt, "America/New_York")  # local_tz should be ignored

    # London in June is UTC+1 (BST), so 12:00 BST = 11:00 UTC
    assert result == datetime(2023, 6, 15, 11, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_already_utc_datetime_unchanged():
    """Test that UTC datetime remains unchanged."""
    utc_dt = datetime(2023, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

    result = to_utc(utc_dt, "America/New_York")

    assert result == utc_dt
    assert result.tzinfo == ZoneInfo("UTC")


def test_tokyo_timezone_conversion():
    """Test conversion with Tokyo timezone."""
    naive_dt = datetime(2023, 6, 15, 12, 0, 0)
    result = to_utc(naive_dt, "Asia/Tokyo")
    assert result == datetime(2023, 6, 15, 3, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_paris_timezone_conversion():
    """Test conversion with Paris timezone."""
    naive_dt = datetime(2023, 6, 15, 12, 0, 0)
    result = to_utc(naive_dt, "Europe/Paris")
    assert result == datetime(2023, 6, 15, 10, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_sydney_timezone_conversion():
    """Test conversion with Sydney timezone."""
    naive_dt = datetime(2023, 6, 15, 12, 0, 0)
    result = to_utc(naive_dt, "Australia/Sydney")
    assert result == datetime(2023, 6, 15, 2, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_microseconds_preserved():
    """Test that microseconds are preserved in conversion."""
    naive_dt = datetime(2023, 6, 15, 12, 30, 45, 123456)
    result = to_utc(naive_dt, "America/New_York")
    assert result == datetime(2023, 6, 15, 16, 30, 45, 123456, tzinfo=ZoneInfo("UTC"))


def test_invalid_timezone_raises_error():
    """Test that invalid timezone raises ZoneInfoNotFoundError."""
    naive_dt = datetime(2023, 6, 15, 12, 0, 0)

    with pytest.raises(Exception):
        to_utc(naive_dt, "Invalid/Timezone")


def test_year_boundary_conversion():
    """Test conversion at year boundaries."""
    # New Year's Eve in different timezone
    nye_dt = datetime(2023, 12, 31, 23, 0, 0)
    result = to_utc(nye_dt, "Asia/Tokyo")  # UTC+9

    # 23:00 JST on Dec 31 = 14:00 UTC on Dec 31
    assert result == datetime(2023, 12, 31, 14, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_los_angeles_conversion():
    """Test Los Angeles timezone conversion."""
    naive_dt = datetime(2023, 6, 15, 9, 0, 0)
    result = to_utc(naive_dt, "America/Los_Angeles")
    assert result == datetime(2023, 6, 15, 16, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_berlin_conversion():
    """Test Berlin timezone conversion."""
    naive_dt = datetime(2023, 6, 15, 14, 0, 0)
    result = to_utc(naive_dt, "Europe/Berlin")
    assert result == datetime(2023, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))


def test_shanghai_conversion():
    """Test Shanghai timezone conversion."""
    naive_dt = datetime(2023, 6, 15, 20, 0, 0)
    result = to_utc(naive_dt, "Asia/Shanghai")
    assert result == datetime(2023, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("UTC"))


@pytest.mark.parametrize(
    "local_tz,naive_time,expected_utc_time",
    [
        (
            "America/Los_Angeles",
            datetime(2023, 6, 15, 9, 0),
            datetime(2023, 6, 15, 16, 0),
        ),
        ("Europe/Berlin", datetime(2023, 6, 15, 14, 0), datetime(2023, 6, 15, 12, 0)),
        ("Asia/Shanghai", datetime(2023, 6, 15, 20, 0), datetime(2023, 6, 15, 12, 0)),
        (
            "Australia/Melbourne",
            datetime(2023, 6, 15, 22, 0),
            datetime(2023, 6, 15, 12, 0),
        ),
        ("America/Chicago", datetime(2023, 6, 15, 11, 0), datetime(2023, 6, 15, 16, 0)),
    ],
)
def test_parametrized_timezone_conversions(local_tz, naive_time, expected_utc_time):
    """Parametrized test for multiple timezone conversions."""
    result = to_utc(naive_time, local_tz)
    assert result == expected_utc_time.replace(tzinfo=ZoneInfo("UTC"))
