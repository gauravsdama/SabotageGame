# Sabotage Game

Sabotage Game is a small Flask party-game prototype for separate browser sessions on one computer or a trusted local network. Players join with a room code, receive hidden roles, take turns completing tasks, and vote for the saboteur at the end of the round.

The project is an educational prototype, not a hosted game service. All rooms and player state live in one Python process and disappear when the server stops.

## Run locally

Requires Python 3 and Flask.

```bash
uv sync --python 3.12 --locked
uv run python sabotageGame.py
```

Open `http://127.0.0.1:5000`. For a trusted local-network session, start with
`SABOTAGE_HOST=0.0.0.0 uv run python sabotageGame.py`; other players can then
open `http://<HOST_LAN_IP>:5000`. This is live shared state in one Python
process, not an internet-hosted or production multiplayer service.

## Round flow

1. One player creates a room and shares its six-character code.
2. At least two players join and the host starts the round.
3. One player is selected as the saboteur. The remaining players are innocents.
4. Half of the players, rounded down, receive a turn in random order. A saboteur assigned a turn may record a sabotage instead of completing it.
5. After the task turns, every player votes. A strict majority must identify the saboteur.

Waiting pages refresh periodically to show shared state changes. Pages with an
available role, task, start, or vote action do not refresh underneath the player.

## Local limits

The process keeps at most 64 rooms, 16 players per room, unfinished rooms for
six hours, and finished rooms for one hour. These defaults can be adjusted with
`SABOTAGE_MAX_ROOMS`, `SABOTAGE_MAX_PLAYERS`,
`SABOTAGE_ROOM_TTL_SECONDS`, and `SABOTAGE_FINISHED_TTL_SECONDS`.

## Current limitations

- State is held by a bounded in-memory store; there is no database, recovery, or multi-process support.
- The app uses Flask's development server. Do not expose it to the public internet.
- The default session secret is generated at process start, so browser sessions end when the server restarts. Set `SECRET_KEY` only when stable local sessions are needed.
- There is no authentication, reconnect flow, cross-process coordination, rate limiting, or production server.
- Mutating forms use session-bound CSRF tokens and bounded form bodies, but those safeguards do not make the development server suitable for an untrusted network.
- Game rules and scoring are intentionally minimal.

For a portfolio review, run it on a trusted local network and treat it as a demonstration of Flask routing, sessions, and shared round state.

## Verify

```bash
uv run pytest -q
uv run ruff format --check sabotageGame.py sabotage_game tests scripts
uv run ruff check sabotageGame.py sabotage_game tests scripts
uv run pip-audit
uv run python scripts/release_guard.py
uv build
uv run python scripts/verify_distribution.py
```
