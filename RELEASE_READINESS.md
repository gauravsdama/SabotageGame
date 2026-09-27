# Release readiness

Last verified: 2026-09-15

## Verdict

Ready for public source review as a local/LAN party-game prototype once the
current working tree is committed. It is not ready for public-internet hosting
or production multiplayer claims.

## Audience and project story

The intended user is a portfolio reviewer or small group running separate
browser sessions on one computer or a trusted LAN. Gaurav Dama built the Flask
prototype and its in-memory round flow: create, join, host start, hidden roles,
assigned task turns, final voting, and results.

The runtime records the room host, prevents non-host starts and late joins,
uses unpredictable player IDs and collision-checked room codes, and owns each
round through one explicit phase. Locked POST transitions reject malformed,
unauthorized, and repeated actions; the last task starts voting atomically and
the last vote records the server-owned result.

## Release surface and privacy

- Repository history and remotes identify Gaurav Dama as the original author.
- `LICENSE`, `THIRD_PARTY_NOTICES.md`, package metadata, `uv.lock`, CI, tests,
  and archive verification are present. The owner approved the MIT license on
  2026-09-15.
- Environment files, virtual environments, caches, build outputs, and macOS
  metadata are ignored and rejected by the release guard.
- The server defaults to loopback with debug mode off. LAN binding requires an
  explicit `SABOTAGE_HOST=0.0.0.0` choice.
- The in-memory store defaults to 64 rooms, 16 players per room, a six-hour
  active-room lifetime, and a one-hour finished-room lifetime. Mutating forms
  use session-bound CSRF tokens and a 16 KiB request limit.
- `docs/product/UI_COPY.md` inventories every static and dynamic UI string and
  defines the real multi-session product boundary.

## Verification evidence

```text
uv lock --check
uv run ruff format --check sabotageGame.py sabotage_game tests scripts
uv run ruff check sabotageGame.py sabotage_game tests scripts
uv run pytest -q                         # 9 passed
uv run pip-audit                         # no known vulnerabilities
uv run python scripts/release_guard.py
uv build
uv run python scripts/verify_distribution.py
```

Browser verification used two isolated browser contexts to create and join a
room, confirm that only the host saw the start action, reveal roles, complete
the assigned task, cast both votes, and render results. A 320 px overflow check
passed, and no console errors, page errors, or failed requests were observed.

Current screenshots:

- `docs/screenshots/home.png`
- `docs/screenshots/two-player-lobby.png`
- `docs/screenshots/player-dashboard.png`
- `docs/screenshots/results.png`

## Remaining boundaries

- There is no persistence, reconnect flow, authentication, cross-process
  coordination, rate limiting, or production server. Do not expose this build
  to the public internet.
- The current task mechanics are button-driven placeholders rather than a
  content-rich game. That limitation should remain explicit in any demo.
- A clean-clone CI run remains an external check after the owner commits the
  working tree.
