"""Bounded, process-local room storage."""

from __future__ import annotations

import copy
import secrets
import string
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager

from .domain import Game, GameError, Phase


class RoomStore:
    def __init__(
        self,
        *,
        max_rooms: int = 64,
        max_players: int = 16,
        room_ttl_seconds: int = 6 * 60 * 60,
        finished_ttl_seconds: int = 60 * 60,
    ) -> None:
        self.max_rooms = max_rooms
        self.max_players = max_players
        self.room_ttl_seconds = room_ttl_seconds
        self.finished_ttl_seconds = finished_ttl_seconds
        self._games: dict[str, Game] = {}
        self._lock = threading.RLock()

    def create(self) -> Game:
        with self._lock:
            self._purge_expired(time.time())
            if len(self._games) >= self.max_rooms:
                raise GameError(503)
            for _ in range(100):
                code = "".join(
                    secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)
                )
                if code not in self._games:
                    game = Game(code=code)
                    self._games[code] = game
                    return copy.deepcopy(game)
        raise GameError(503)

    def snapshot(self, code: str) -> Game | None:
        with self._lock:
            game = self._games.get(code)
            if game is None or self._is_expired(game, time.time()):
                return None
            return copy.deepcopy(game)

    @contextmanager
    def locked(self, code: str) -> Iterator[Game]:
        with self._lock:
            game = self._games.get(code)
            if game is None:
                raise GameError(404)
            if self._is_expired(game, time.time()):
                del self._games[code]
                raise GameError(404)
            yield game

    def clear(self) -> None:
        with self._lock:
            self._games.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._games)

    def _purge_expired(self, now: float) -> None:
        expired = [code for code, game in self._games.items() if self._is_expired(game, now)]
        for code in expired:
            del self._games[code]

    def _is_expired(self, game: Game, now: float) -> bool:
        ttl = self.finished_ttl_seconds if game.phase is Phase.FINISHED else self.room_ttl_seconds
        return now - game.updated_at >= ttl
