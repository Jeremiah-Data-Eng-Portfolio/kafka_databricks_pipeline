from streaming.transforms.quality_rules import required_fields_present


def test_required_fields_present_flags_missing_message() -> None:
    ok, missing = required_fields_present({"user": "abc"})
    assert ok is False
    assert missing == ("message",)
