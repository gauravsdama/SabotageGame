# Hidden Saboteur UI copy

This is the human-owned source of truth for every user-facing string in the
Flask prototype. Stable IDs remain unchanged when text is edited. Runtime text
must match this inventory exactly.

## Static portfolio demo

The GitHub Pages demo follows the same create, join, role, task, vote, and result
sequence as the Flask game. It keeps the round in the current browser and assigns
the host as the saboteur so every state can be tested without a second session.
Its visible copy is maintained in `docs/demo/index.html` and `docs/demo/app.js`.

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `demo.heading` | Demo heading | Sabotage Game | `docs/demo/index.html` |
| `demo.instructions` | Demo scope | Create a room, join another player, reveal your role, take a task turn, and vote. | `docs/demo/index.html` |
| `demo.create` | Room creation | Create room / Host name / Create room | `docs/demo/index.html` |
| `demo.join` | Lobby | Join room / Player name / Join room / Start game | `docs/demo/index.html` |
| `demo.role` | Role reveal | Your role / Reveal my role / Saboteur / Start task turn | `docs/demo/index.html` |
| `demo.task` | Task turn | Your task turn / Complete task / Sabotage task | `docs/demo/index.html` |
| `demo.vote` | Voting | Vote for the saboteur / Player / Submit vote | `docs/demo/index.html` |
| `demo.result` | Result | Saboteur identified. / The saboteur survives. | `docs/demo/app.js` |

## Shared shell and home

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.brand.mark` | Brand mark | HS | All templates |
| `game.brand.name` | Brand | Hidden Saboteur | All templates |
| `game.home.meta.title` | Browser title | Hidden Saboteur | `base.html` |
| `game.home.scope` | Runtime scope | Local party game | `home.html` |
| `game.home.hero` | Main heading | Find the hidden saboteur before the team falls apart. | `home.html` |
| `game.home.intro` | Game premise | Create a room, share the code, assign secret roles, run tasks, and vote before the saboteur gets away with the points. | `home.html` |
| `game.home.create.title` | Create heading | Create room | `home.html` |
| `game.home.create.description` | Create explanation | Start a fresh game and invite players with a short room code. | `home.html` |
| `game.home.create.action` | Create action | Create Game Room | `home.html` |
| `game.home.join.title` | Join heading | Join room | `home.html` |
| `game.home.join.label` | Room input label | Game code | `home.html` |
| `game.home.join.placeholder` | Room input example | A1B2C3 | `home.html` |
| `game.home.join.action` | Join action | Join Game | `home.html` |

## Join and lobby

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.join.meta.title` | Browser title | Join Hidden Saboteur | `join.html` |
| `game.join.heading` | Main heading | Enter your player name. | `join.html` |
| `game.join.description` | Room context | You are joining room {game code}. Your role stays hidden until the game starts. | `join.html` |
| `game.join.name.label` | Name label | Player name | `join.html` |
| `game.join.name.placeholder` | Name example | Gaurav | `join.html` |
| `game.join.action` | Join action | Join Room | `join.html` |
| `game.lobby.meta.title` | Browser title | Hidden Saboteur Lobby | `lobby.html` |
| `game.lobby.dashboard-link` | Navigation | My Dashboard | `lobby.html` |
| `game.lobby.heading` | Main heading | Room {game code} | `lobby.html` |
| `game.lobby.description` | Host guidance | Share the room code, wait for players, then start once everyone is ready. | `lobby.html` |
| `game.lobby.code.label` | Accessible code label | Game code | `lobby.html` |
| `game.lobby.waiting` | Room status | Waiting | `lobby.html` |
| `game.lobby.player-count` | Room status | {count} players | `lobby.html` |
| `game.lobby.players.title` | Player list heading | Players | `lobby.html` |
| `game.lobby.players.empty` | Empty state | No players have joined yet. | `lobby.html` |
| `game.lobby.start` | Host-only action | Start Game | `lobby.html` |

## Player dashboard

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.dashboard.meta.title` | Browser title | Hidden Saboteur Dashboard | `dashboard.html` |
| `game.dashboard.lobby-link` | Navigation | Lobby | `dashboard.html` |
| `game.dashboard.heading` | Main heading | Hello, {player name} | `dashboard.html` |
| `game.dashboard.description` | Room context | Room {game code} is your current game. Keep your role private and watch the task order. | `dashboard.html` |
| `game.dashboard.started` | Game status | Game started | `dashboard.html` |
| `game.dashboard.waiting` | Game status | Waiting to start | `dashboard.html` |
| `game.dashboard.sabotages` | Game status | {count} sabotages | `dashboard.html` |
| `game.dashboard.voting` | Game status | Voting active | `dashboard.html` |
| `game.dashboard.ended.title` | Finished state | Game ended | `dashboard.html` |
| `game.dashboard.ended.description` | Finished state | The final results are ready. | `dashboard.html` |
| `game.dashboard.results` | Finished action | View Results | `dashboard.html` |
| `game.dashboard.wait.title` | Pre-start state | Waiting for host | `dashboard.html` |
| `game.dashboard.wait.description` | Pre-start state | The game has not started yet. Return to the lobby while more players join. | `dashboard.html` |
| `game.dashboard.return` | Pre-start action | Return to Lobby | `dashboard.html` |
| `game.role.title` | Role heading | Your role | `dashboard.html` |
| `game.role.saboteur` | Secret role | Saboteur | Game state / `dashboard.html` |
| `game.role.innocent` | Secret role | Innocent | Game state / `dashboard.html` |
| `game.role.reveal` | Private action | Reveal My Role | `dashboard.html` |
| `game.tasks.order` | Task list heading | Task order | `dashboard.html` |
| `game.tasks.current` | Task status | Current | `dashboard.html` |
| `game.vote.recorded.title` | Submitted state | Vote recorded | `dashboard.html` |
| `game.vote.recorded.description` | Submitted state | Waiting for the rest of the players. | `dashboard.html` |
| `game.vote.title` | Voting heading | Vote for the saboteur | `dashboard.html` |
| `game.vote.label` | Vote input label | Choose a player | `dashboard.html` |
| `game.vote.submit` | Vote action | Submit Vote | `dashboard.html` |
| `game.task.turn` | Active-turn heading | Your task turn | `dashboard.html` |
| `game.task.complete` | Task action | Complete Task | `dashboard.html` |
| `game.task.sabotage` | Secret task action | Sabotage Task | `dashboard.html` |
| `game.task.wait.title` | Other-player turn | Waiting on task | `dashboard.html` |
| `game.task.wait.description` | Other-player turn | {player name} is handling the current task. | `dashboard.html` |

## Results

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.results.meta.title` | Browser title | Hidden Saboteur Results | `results.html` |
| `game.results.new` | Navigation | New Game | `results.html` |
| `game.results.innocents.title` | Innocent win | Innocents win. | `results.html` |
| `game.results.innocents.description` | Innocent win | The group identified the saboteur before they could keep the points. | `results.html` |
| `game.results.saboteur.title` | Saboteur win | The saboteur survives. | `results.html` |
| `game.results.saboteur.description` | Saboteur win | The final vote missed the saboteur, so the sabotage points stand. | `results.html` |
| `game.results.saboteur` | Result fact | Saboteur: {player name} | `results.html` |
| `game.results.sabotages` | Result fact | {count} sabotages | `results.html` |
| `game.results.points` | Result fact | {count} points | `results.html` |
| `game.results.votes.title` | Vote list heading | Final votes | `results.html` |
| `game.results.vote` | Vote list row | {voter name} voted for {player name} | `results.html` |
| `game.results.votes.empty` | Empty state | No votes were recorded. | `results.html` |

## Product and state boundary

- The current application is a live, in-memory Flask prototype for separate
  browser sessions on one machine or a trusted LAN. It is not a static,
  pass-and-play demo and is not a hosted multiplayer service.
- Verify create, join, host-only start, role reveal, assigned task, sabotage,
  all-player vote, both result outcomes, late-join rejection, refresh, and
  invalid-room recovery states.
- Keep keyboard-visible focus, semantic labels, a 320 px layout, 200% zoom,
  and reduced-motion compatibility.
