from app.main import calculate_severity


def test_critical_earthquake():
    assert calculate_severity(6.0) == "CRITICAL"


def test_high_earthquake():
    assert calculate_severity(5.0) == "HIGH"


def test_medium_earthquake():
    assert calculate_severity(4.0) == "MEDIUM"


def test_low_earthquake():
    assert calculate_severity(3.9) == "LOW"


def test_missing_magnitude():
    assert calculate_severity(None) == "UNKNOWN"