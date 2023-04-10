"""
A module to compose the subscription payload for the listener.
"""
import toolz.curried as toolz

from entities import LIVE_WORLDS


def subscription(payload: dict) -> dict:
    """Add the keys for a subscription payload"""
    return payload | {"service": "event", "action": "subscribe"}


@toolz.curry
def with_worlds(worlds: list[int], payload: dict) -> dict:
    """Specify the worlds to listen to. Use LIVE_WORLDS for the open servers."""
    # Asking for ints because it's more intuitive
    return payload | {"worlds": list(map(str, worlds))}


@toolz.curry
def with_events(names: list[str], payload: dict) -> dict:
    """Ask for certain events to be sent to the listener"""
    return payload | {"eventNames": names}


def with_items(payload: dict) -> dict:
    """Ask for items to be listened to."""
    event_names = payload.get("eventNames", [])
    return {
        **payload,
        "eventNames": event_names + ["ItemAdded"],
        # Ask for all characters in existence to be listened to
        "characters": ["all"],
        # Ensures that only characters from the requested worlds are sent
        "logicalAndCharactersWithWorlds": True,
    }
