from streaming.transforms.dedupe import build_event_key


def test_build_event_key_is_stable() -> None:
    assert build_event_key("twitch_chat", 1, 42) == "twitch_chat:1:42"
