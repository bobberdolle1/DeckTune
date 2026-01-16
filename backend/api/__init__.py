"""API module - RPC handlers and event emitters."""

from .rpc import DeckTuneRPC
from .events import EventEmitter
from .stream import StatusStreamManager

__all__ = ["DeckTuneRPC", "EventEmitter", "StatusStreamManager"]
