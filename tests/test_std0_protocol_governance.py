import pytest

from honest_agent import ExtensionClass, ProtocolError, negotiate_version, parse_version, require_known_major, validate_extension


def test_version_negotiation_selects_highest_compatible_minor():
    assert negotiate_version(["1.0", "1.1", "2.0"], supported_minor=1) == "1.1"
    assert parse_version("1.7").minor == 7


def test_version_negotiation_rejects_major_downgrade_or_malformed_versions():
    with pytest.raises(ProtocolError):
        negotiate_version(["2.0"], supported_major=1, supported_minor=1)
    with pytest.raises(ProtocolError):
        require_known_major("2.0")
    with pytest.raises(ProtocolError):
        parse_version("1")
    with pytest.raises(ProtocolError):
        parse_version("1.x")


def test_extensions_must_be_namespaced_and_classified():
    assert validate_extension("x-example.org:trace", ExtensionClass.INFORMATIONAL) == "informational"
    assert validate_extension("x-example.org:restrict", ExtensionClass.RESTRICTIVE) == "restrictive"
    with pytest.raises(ProtocolError):
        validate_extension("trace", ExtensionClass.INFORMATIONAL)
    with pytest.raises(ProtocolError):
        validate_extension("x-example.org:trace", "unknown")
