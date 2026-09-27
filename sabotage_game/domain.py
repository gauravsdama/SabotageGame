"""Round state and atomic game transitions."""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field
from enum import StrEnum


class Phase(StrEnum):
    LOBBY = "lobby"
    TASKS = "tasks"
    VOTING = "voting"
    FINISHED = "finished"


class GameError(Exception):
    """A rejected domain action with an HTTP-compatible status."""

    def __init__(self, status_code: int) -> None:
        super().__init__(status_code)
        self.status_code = status_code


@dataclass(slots=True)
class Player:
    name: str
    role: str | None = None
    has_seen_role: bool = False


@dataclass(slots=True)
class Game:
    code: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    phase: Phase = Phase.LOBBY
    players: dict[str, Player] = field(default_factory=dict)
    host_id: str | None = None
    saboteur_id: str | None = None
    sabotages: int = 0
    saboteur_points: int = 0
    assigned_order: list[str] = field(default_factory=list)
    task_index: int = 0
    votes: dict[str, str] = field(default_factory=dict)
    saboteur_out: bool | None = None

    @property
    def started(self) -> bool:
        return self.phase is not Phase.LOBBY

    @property
    def voting_active(self) -> bool:
        return self.phase is Phase.VOTING

    @property
    def finished(self) -> bool:
        return self.phase is Phase.FINISHED

    @property
    def num_tasks(self) -> int:
        return len(self.assigned_order)

    def add_player(self, player_id: str, name: str, *, as_host: bool, max_players: int) -> None:
        if self.phase is not Phase.LOBBY:
            raise GameError(409)
        if len(self.players) >= max_players:
            raise GameError(409)
        if player_id in self.players:
            raise GameError(409)
        self.players[player_id] = Player(name=name)
        if as_host:
            if self.host_id is not None:
                del self.players[player_id]
                raise GameError(409)
            self.host_id = player_id
        self._changed()

    def start(self, player_id: str) -> None:
        if self.phase is not Phase.LOBBY:
            raise GameError(409)
        if player_id != self.host_id:
            raise GameError(403)
        player_ids = list(self.players)
        if len(player_ids) < 2:
            raise GameError(409)

        self.saboteur_id = secrets.choice(player_ids)
        for pid, player in self.players.items():
            player.role = "Saboteur" if pid == self.saboteur_id else "Innocent"
        self.assigned_order = secrets.SystemRandom().sample(player_ids, len(player_ids) // 2)
        self.phase = Phase.TASKS
        self._changed()

    def reveal_role(self, player_id: str) -> None:
        if self.phase not in {Phase.TASKS, Phase.VOTING}:
            raise GameError(409)
        player = self._player(player_id)
        if player.has_seen_role:
            raise GameError(409)
        player.has_seen_role = True
        self._changed()

    def perform_task(self, player_id: str, action: str | None) -> None:
        if self.phase is not Phase.TASKS:
            raise GameError(409)
        player = self._player(player_id)
        if not player.has_seen_role:
            raise GameError(409)
        if action not in {"complete", "sabotage"}:
            raise GameError(400)
        if self.task_index >= self.num_tasks or self.assigned_order[self.task_index] != player_id:
            raise GameError(409)
        if action == "sabotage":
            if player.role != "Saboteur":
                raise GameError(403)
            self.sabotages += 1

        self.task_index += 1
        if self.task_index == self.num_tasks:
            self.phase = Phase.VOTING
        self._changed()

    def cast_vote(self, player_id: str, target_id: str | None) -> bool:
        if self.phase is not Phase.VOTING:
            raise GameError(409)
        if not self._player(player_id).has_seen_role:
            raise GameError(409)
        if target_id not in self.players:
            raise GameError(400)
        if player_id in self.votes:
            raise GameError(409)
        self.votes[player_id] = target_id
        if len(self.votes) == len(self.players):
            self._finish_vote()
        self._changed()
        return self.finished

    def _finish_vote(self) -> None:
        votes_for_saboteur = sum(target == self.saboteur_id for target in self.votes.values())
        self.saboteur_out = votes_for_saboteur >= (len(self.players) // 2) + 1
        self.saboteur_points = 0 if self.saboteur_out else self.sabotages
        self.phase = Phase.FINISHED

    def _player(self, player_id: str) -> Player:
        try:
            return self.players[player_id]
        except KeyError as error:
            raise GameError(403) from error

    def _changed(self) -> None:
        self.updated_at = time.time()
