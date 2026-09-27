from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from sabotage_game.domain import GameError, Phase
from sabotage_game.store import RoomStore
from sabotage_game.web import create_app


@pytest.fixture
def store() -> RoomStore:
    return RoomStore(max_rooms=4, max_players=4)


@pytest.fixture
def app(store):
    application = create_app(store=store)
    application.config.update(TESTING=True, SECRET_KEY="test-secret")
    return application


def csrf(client) -> str:
    client.get("/")
    with client.session_transaction() as current_session:
        return current_session["csrf_token"]


def post(client, path: str, data: dict[str, str] | None = None):
    payload = {"csrf_token": csrf(client)}
    payload.update(data or {})
    return client.post(path, data=payload)


def create_and_join(client, store: RoomStore, name: str = "Host") -> tuple[str, str]:
    response = post(client, "/create_game")
    game_code = re.search(r"game_code=([A-Z0-9]{6})", response.location).group(1)
    response = post(client, f"/join_game/{game_code}", {"player_name": name})
    assert response.status_code == 303
    with client.session_transaction() as current_session:
        player_id = current_session["player_id"]
    assert store.snapshot(game_code).host_id == player_id
    return game_code, player_id


def join(client, game_code: str, name: str) -> str:
    response = post(client, f"/join_game/{game_code}", {"player_name": name})
    assert response.status_code == 303
    with client.session_transaction() as current_session:
        return current_session["player_id"]


def start_two_player_game(app, store):
    host = app.test_client()
    guest = app.test_client()
    game_code, host_id = create_and_join(host, store)
    guest_id = join(guest, game_code, "Guest")
    assert post(host, f"/start_game/{game_code}").status_code == 303
    return host, guest, game_code, host_id, guest_id


def test_host_start_is_atomic_and_repeated_start_is_rejected(app, store) -> None:
    host, guest, game_code, _, _ = start_two_player_game(app, store)
    late = app.test_client()

    assert post(late, f"/join_game/{game_code}", {"player_name": "Late"}).status_code == 409
    assert post(guest, f"/start_game/{game_code}").status_code == 409
    assert post(host, f"/start_game/{game_code}").status_code == 409
    game = store.snapshot(game_code)
    assert game.phase is Phase.TASKS
    assert len(game.assigned_order) == 1
    assert sum(player.role == "Saboteur" for player in game.players.values()) == 1


def test_get_requests_do_not_mutate_game_state(app, store) -> None:
    host, _, game_code, _, _ = start_two_player_game(app, store)
    before = store.snapshot(game_code)

    assert host.get("/dashboard").status_code == 200
    assert host.get(f"/lobby/{game_code}").status_code == 303
    assert store.snapshot(game_code) == before


def test_missing_invalid_and_repeated_task_actions_are_rejected(app, store) -> None:
    host, guest, game_code, host_id, guest_id = start_two_player_game(app, store)
    clients = {host_id: host, guest_id: guest}
    assigned_id = store.snapshot(game_code).assigned_order[0]
    assigned_client = clients[assigned_id]
    assert post(assigned_client, f"/reveal_role/{game_code}").status_code == 303

    assert post(assigned_client, f"/do_task/{game_code}").status_code == 400
    assert post(assigned_client, f"/do_task/{game_code}", {"action": "invalid"}).status_code == 400
    assert post(assigned_client, f"/do_task/{game_code}", {"action": "complete"}).status_code == 303
    assert store.snapshot(game_code).phase is Phase.VOTING
    assert post(assigned_client, f"/do_task/{game_code}", {"action": "complete"}).status_code == 409


def test_unauthorized_sabotage_does_not_advance_turn(app, store) -> None:
    host, guest, game_code, host_id, guest_id = start_two_player_game(app, store)
    clients = {host_id: host, guest_id: guest}
    with store.locked(game_code) as game:
        assigned_id = game.assigned_order[0]
        game.players[assigned_id].role = "Innocent"
    assigned_client = clients[assigned_id]
    post(assigned_client, f"/reveal_role/{game_code}")

    assert post(assigned_client, f"/do_task/{game_code}", {"action": "sabotage"}).status_code == 403
    game = store.snapshot(game_code)
    assert game.task_index == 0
    assert game.sabotages == 0


def test_votes_reject_missing_unknown_and_repeat_then_finalize(app, store) -> None:
    host, guest, game_code, host_id, guest_id = start_two_player_game(app, store)
    clients = {host_id: host, guest_id: guest}
    for client in clients.values():
        post(client, f"/reveal_role/{game_code}")
    assigned_id = store.snapshot(game_code).assigned_order[0]
    post(clients[assigned_id], f"/do_task/{game_code}", {"action": "complete"})
    saboteur_id = store.snapshot(game_code).saboteur_id

    assert post(host, f"/cast_vote/{game_code}").status_code == 400
    assert post(host, f"/cast_vote/{game_code}", {"vote": "unknown"}).status_code == 400
    assert post(host, f"/cast_vote/{game_code}", {"vote": saboteur_id}).status_code == 303
    assert post(host, f"/cast_vote/{game_code}", {"vote": saboteur_id}).status_code == 409
    response = post(guest, f"/cast_vote/{game_code}", {"vote": saboteur_id})
    assert response.location.endswith(f"/results/{game_code}")
    game = store.snapshot(game_code)
    assert game.phase is Phase.FINISHED
    assert game.saboteur_out is True
    results = guest.get(f"{response.location}?saboteur_out=0")
    assert results.status_code == 200
    assert b"Innocents win." in results.data
    assert guest.get(f"/show_results/{game_code}").location.endswith(f"/results/{game_code}")


def test_csrf_body_limit_and_security_headers(app, store) -> None:
    client = app.test_client()
    home = client.get("/")
    assert home.headers["Cache-Control"] == "no-store"
    assert home.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in home.headers["Content-Security-Policy"]
    assert client.post("/create_game").status_code == 400
    csrf(client)
    assert client.post("/create_game", data={"csrf_token": "wrong"}).status_code == 403
    assert (
        client.post(
            "/create_game", data={"csrf_token": csrf(client), "x": "a" * 17_000}
        ).status_code
        == 413
    )
    assert len(store) == 0


def test_lifecycle_bounds_rooms_players_and_expiry(app) -> None:
    store = RoomStore(max_rooms=1, max_players=1, room_ttl_seconds=1)
    bounded_app = create_app(store=store)
    bounded_app.config.update(TESTING=True, SECRET_KEY="test-secret")
    host = bounded_app.test_client()
    guest = bounded_app.test_client()
    game_code, _ = create_and_join(host, store)

    assert post(guest, f"/join_game/{game_code}", {"player_name": "Guest"}).status_code == 409
    assert post(guest, "/create_game").status_code == 503
    with store.locked(game_code) as game:
        game.updated_at = time.time() - 2
    assert store.snapshot(game_code) is None
    assert post(guest, "/create_game").status_code == 303
    assert len(store) == 1


def test_actionable_pages_do_not_auto_refresh(app, store) -> None:
    host = app.test_client()
    guest = app.test_client()
    game_code, _ = create_and_join(host, store)
    join(guest, game_code, "Guest")

    assert b'http-equiv="refresh"' not in host.get(f"/lobby/{game_code}").data
    assert b'http-equiv="refresh"' in guest.get(f"/lobby/{game_code}").data
    post(host, f"/start_game/{game_code}")
    assert b'http-equiv="refresh"' not in host.get("/dashboard").data


def test_store_lock_allows_only_one_concurrent_transition() -> None:
    store = RoomStore()
    game = store.create()
    with store.locked(game.code) as current:
        current.add_player("one", "One", as_host=True, max_players=4)
        current.add_player("two", "Two", as_host=False, max_players=4)
        current.start("one")
        assigned_id = current.assigned_order[0]
        current.reveal_role(assigned_id)
    barrier = Barrier(2)

    def act() -> int:
        barrier.wait()
        try:
            with store.locked(game.code) as current:
                current.perform_task(assigned_id, "complete")
        except GameError as error:
            return error.status_code
        return 303

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = sorted(executor.map(lambda _: act(), range(2)))
    assert statuses == [303, 409]
    assert store.snapshot(game.code).phase is Phase.VOTING
