#!/usr/bin/env python3
"""
Connection configuration for Telegram Inspector
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional, Tuple

CONFIG_PATH = Path(__file__).parent / "connection.json"


@dataclass
class ConnectionSettings:
    mode: str = "direct"  # direct | tor | proxy
    proxy_type: str = "socks5"  # socks5 | socks4 | http
    proxy_host: str = "127.0.0.1"
    proxy_port: int = 9050
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None


class ConnectionConfig:
    def __init__(self) -> None:
        self.path = CONFIG_PATH
        self._settings = self._load()

    def _load(self) -> ConnectionSettings:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                return ConnectionSettings(**data)
            except Exception:
                pass
        # defaults
        return ConnectionSettings()

    def save(self) -> None:
        self.path.write_text(
            json.dumps(asdict(self._settings), indent=2), encoding="utf-8"
        )

    # Public API
    def get_mode(self) -> str:
        return self._settings.mode

    def set_mode(self, mode: str) -> None:
        self._settings.mode = mode

    def set_proxy(
        self,
        proxy_type: str,
        host: str,
        port: int,
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        self._settings.proxy_type = proxy_type
        self._settings.proxy_host = host
        self._settings.proxy_port = int(port)
        self._settings.proxy_username = username or None
        self._settings.proxy_password = password or None

    def get_proxy_tuple(
        self,
    ) -> Optional[Tuple[Any, str, int, bool, Optional[str], Optional[str]]]:
        """Return a PySocks proxy tuple for Telethon or None for direct mode."""
        if self._settings.mode == "direct":
            return None

        try:
            import socks
        except Exception:
            # PySocks is required for proxy/tor
            return None

        t = self._settings.proxy_type.lower()
        if t == "socks5":
            proxy_type = socks.SOCKS5
        elif t == "socks4":
            proxy_type = socks.SOCKS4
        elif t == "http":
            proxy_type = socks.HTTP
        else:
            proxy_type = socks.SOCKS5

        host = self._settings.proxy_host
        port = int(self._settings.proxy_port)
        return (
            proxy_type,
            host,
            port,
            True,
            self._settings.proxy_username,
            self._settings.proxy_password,
        )

    def set_tor_defaults(self) -> None:
        self._settings.mode = "tor"
        self._settings.proxy_type = "socks5"
        self._settings.proxy_host = "127.0.0.1"
        self._settings.proxy_port = 9050
        self._settings.proxy_username = None
        self._settings.proxy_password = None

    def is_proxy_mode(self) -> bool:
        return self._settings.mode in ("tor", "proxy")

    def as_dict(self) -> dict:
        return asdict(self._settings)
