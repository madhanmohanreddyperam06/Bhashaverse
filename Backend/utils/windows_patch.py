"""
Bhashaverse - Windows AsyncIO Silence Patch
Completely suppresses harmless WinError 10054 / 10053 ConnectionResetError
in Python ProactorEventLoop when client browsers reload, close tabs, or disconnect sockets.
"""

import sys


def apply_windows_asyncio_fix() -> None:
    """Safely monkey-patch _ProactorBasePipeTransport._call_connection_lost on Windows."""
    if not sys.platform.startswith("win"):
        return

    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _safe_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, ConnectionAbortedError, OSError) as err:
                if getattr(err, "winerror", None) in (10054, 10053, 10038, None) or isinstance(err, (ConnectionResetError, ConnectionAbortedError)):
                    try:
                        if getattr(self, "_sock", None) is not None:
                            self._sock.close()
                            self._sock = None
                        if getattr(self, "_server", None) is not None:
                            self._server._detach(self)
                            self._server = None
                        self._called_connection_lost = True
                    except Exception:
                        pass
                else:
                    raise

        _ProactorBasePipeTransport._call_connection_lost = _safe_call_connection_lost
    except Exception:
        pass


apply_windows_asyncio_fix()
