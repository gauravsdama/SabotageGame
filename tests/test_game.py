from __future__ import annotations

import re

import pytest

import sabotageGame


@pytest.fixture(autouse=True)
def clean_games():
    sabotageGame.app.config.update(TESTING=True)
    sabotageGame.GAMES.clear()
    yield
    sabotageGame.GAMES.clear()


def create_and_join(client, name: str = "Host") -> str:
    response = client.post("/create_game")
    game_code = re.search(r"game_code=([A-Z0-9]{6})", response.location).group(1)
    response = client.post(f"/join_game/{game_code}", data={"player_name": name})
    assert response.status_code == 302
    return game_code


def join(client, game_code: str, name: str) -> str:
    client.post(f"/join_game/{game_code}", data={"player_name": name})
    with client.session_transaction() as current_session:
        return current_session["player_id"]


def test_creator_becomes_host_and_only_host_can_start() -> None:
    host = sabotageGame.app.test_client()
    guest = sabotageGame.app.test_client()
    game_code = create_and_join(host)
    join(guest, game_code, "Guest")

    guest.post(f"/start_game/{game_code}")
    assert sabotageGame.GAMES[game_code]["started"] is False

    host.post(f"/start_game/{game_code}")
    assert sabotageGame.GAMES[game_code]["started"] is True


def test_started_game_rejects_new_players() -> None:
    host = sabotageGame.app.test_client()
    guest = sabotageGame.app.test_client()
    late = sabotageGame.app.test_client()
    game_code = create_and_join(host)
    join(guest, game_code, "Guest")
    host.post(f"/start_game/{game_code}")

    response = late.post(f"/join_game/{game_code}", data={"player_name": "Late"})
    assert response.location.endswith("/")
    assert len(sabotageGame.GAMES[game_code]["players"]) == 2


def test_complete_vote_finalizes_without_public_mutating_get() -> None:
    host = sabotageGame.app.test_client()
    guest = sabotageGame.app.test_client()
    game_code = create_and_join(host)
    guest_id = join(guest, game_code, "Guest")
    with host.session_transaction() as current_session:
        host_id = current_session["player_id"]

    game = sabotageGame.GAMES[game_code]
    game.update(
        started=True,
        voting_active=True,
        saboteur_id=guest_id,
        sabotages=1,
        votes={},
    )
    game["players"][guest_id]["role"] = "Saboteur"
    game["players"][host_id]["role"] = "Innocent"

    host.post(f"/cast_vote/{game_code}", data={"vote": guest_id})
    response = guest.post(f"/cast_vote/{game_code}", data={"vote": guest_id})
    assert response.location.endswith(f"/results/{game_code}")
    assert game["finished"] is True
    assert game["saboteur_out"] is True
    assert game["saboteur_points"] == 0
    assert host.get(f"/finalize_vote/{game_code}").status_code == 404


def test_results_ignore_query_string_outcome() -> None:
    host = sabotageGame.app.test_client()
    game_code = create_and_join(host)
    with host.session_transaction() as current_session:
        host_id = current_session["player_id"]
    game = sabotageGame.GAMES[game_code]
    game.update(
        finished=True,
        saboteur_id=host_id,
        saboteur_out=False,
        sabotages=2,
        saboteur_points=2,
        votes={},
    )
    response = host.get(f"/results/{game_code}?saboteur_out=1")
    assert b"The saboteur survives." in response.data


def test_two_browser_sessions_complete_a_round() -> None:
    host = sabotageGame.app.test_client()
    guest = sabotageGame.app.test_client()
    game_code = create_and_join(host)
    guest_id = join(guest, game_code, "Guest")
    with host.session_transaction() as current_session:
        host_id = current_session["player_id"]

    host.post(f"/start_game/{game_code}")
    game = sabotageGame.GAMES[game_code]
    assert game["started"] is True
    assert game["num_tasks"] == 1
    assert game["saboteur_id"] in {host_id, guest_id}

    host.post(f"/reveal_role/{game_code}")
    guest.post(f"/reveal_role/{game_code}")
    clients = {host_id: host, guest_id: guest}
    assigned_id = game["assigned_order"][0]
    clients[assigned_id].post(f"/do_task/{game_code}", data={"action": "complete"})
    assert game["task_index"] == 1

    host.get("/dashboard")
    assert game["voting_active"] is True
    host.post(f"/cast_vote/{game_code}", data={"vote": game["saboteur_id"]})
    response = guest.post(f"/cast_vote/{game_code}", data={"vote": game["saboteur_id"]})
    assert response.location.endswith(f"/results/{game_code}")
    results = guest.get(response.location)
    assert results.status_code == 200
    assert b"Innocents win." in results.data
