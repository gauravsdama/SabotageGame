# Hidden Saboteur UI copy

This is the human-owned source of truth for every user-facing string in the
Flask prototype. Stable IDs remain unchanged when text is edited. Runtime text
must match this inventory exactly.

## Shared shell and home

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.brand.mark` | Brand mark | HS | All templates |
| `game.brand.name` | Brand | Hidden Saboteur | All templates |
| `game.home.meta.title` | Browser title | Hidden Saboteur | `HOME_PAGE` |
| `game.home.scope` | Runtime scope | Local party game | `HOME_PAGE` |
| `game.home.hero` | Main heading | Find the hidden saboteur before the team falls apart. | `HOME_PAGE` |
| `game.home.intro` | Game premise | Create a room, share the code, assign secret roles, run tasks, and vote before the saboteur gets away with the points. | `HOME_PAGE` |
| `game.home.create.title` | Create heading | Create room | `HOME_PAGE` |
| `game.home.create.description` | Create explanation | Start a fresh game and invite players with a short room code. | `HOME_PAGE` |
| `game.home.create.action` | Create action | Create Game Room | `HOME_PAGE` |
| `game.home.join.title` | Join heading | Join room | `HOME_PAGE` |
| `game.home.join.label` | Room input label | Game code | `HOME_PAGE` |
| `game.home.join.placeholder` | Room input example | A1B2C3 | `HOME_PAGE` |
| `game.home.join.action` | Join action | Join Game | `HOME_PAGE` |

## Join and lobby

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.join.meta.title` | Browser title | Join Hidden Saboteur | `JOIN_PAGE` |
| `game.join.heading` | Main heading | Enter your player name. | `JOIN_PAGE` |
| `game.join.description` | Room context | You are joining room {game code}. Your role stays hidden until the game starts. | `JOIN_PAGE` |
| `game.join.name.label` | Name label | Player name | `JOIN_PAGE` |
| `game.join.name.placeholder` | Name example | Gaurav | `JOIN_PAGE` |
| `game.join.action` | Join action | Join Room | `JOIN_PAGE` |
| `game.lobby.meta.title` | Browser title | Hidden Saboteur Lobby | `LOBBY_PAGE` |
| `game.lobby.dashboard-link` | Navigation | My Dashboard | `LOBBY_PAGE` |
| `game.lobby.heading` | Main heading | Room {game code} | `LOBBY_PAGE` |
| `game.lobby.description` | Host guidance | Share the room code, wait for players, then start once everyone is ready. | `LOBBY_PAGE` |
| `game.lobby.code.label` | Accessible code label | Game code | `LOBBY_PAGE` |
| `game.lobby.started` | Room status | Started | `LOBBY_PAGE` |
| `game.lobby.waiting` | Room status | Waiting | `LOBBY_PAGE` |
| `game.lobby.player-count` | Room status | {count} players | `LOBBY_PAGE` |
| `game.lobby.players.title` | Player list heading | Players | `LOBBY_PAGE` |
| `game.lobby.players.empty` | Empty state | No players have joined yet. | `LOBBY_PAGE` |
| `game.lobby.start` | Host-only action | Start Game | `LOBBY_PAGE` |

## Player dashboard

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.dashboard.meta.title` | Browser title | Hidden Saboteur Dashboard | `DASHBOARD_PAGE` |
| `game.dashboard.lobby-link` | Navigation | Lobby | `DASHBOARD_PAGE` |
| `game.dashboard.heading` | Main heading | Hello, {player name} | `DASHBOARD_PAGE` |
| `game.dashboard.description` | Room context | Room {game code} is your current game. Keep your role private and watch the task order. | `DASHBOARD_PAGE` |
| `game.dashboard.started` | Game status | Game started | `DASHBOARD_PAGE` |
| `game.dashboard.waiting` | Game status | Waiting to start | `DASHBOARD_PAGE` |
| `game.dashboard.sabotages` | Game status | {count} sabotages | `DASHBOARD_PAGE` |
| `game.dashboard.voting` | Game status | Voting active | `DASHBOARD_PAGE` |
| `game.dashboard.ended.title` | Finished state | Game ended | `DASHBOARD_PAGE` |
| `game.dashboard.ended.description` | Finished state | The final results are ready. | `DASHBOARD_PAGE` |
| `game.dashboard.results` | Finished action | View Results | `DASHBOARD_PAGE` |
| `game.dashboard.wait.title` | Pre-start state | Waiting for host | `DASHBOARD_PAGE` |
| `game.dashboard.wait.description` | Pre-start state | The game has not started yet. Return to the lobby while more players join. | `DASHBOARD_PAGE` |
| `game.dashboard.return` | Pre-start action | Return to Lobby | `DASHBOARD_PAGE` |
| `game.role.title` | Role heading | Your role | `DASHBOARD_PAGE` |
| `game.role.saboteur` | Secret role | Saboteur | Game state / `DASHBOARD_PAGE` |
| `game.role.innocent` | Secret role | Innocent | Game state / `DASHBOARD_PAGE` |
| `game.role.reveal` | Private action | Reveal My Role | `DASHBOARD_PAGE` |
| `game.tasks.order` | Task list heading | Task order | `DASHBOARD_PAGE` |
| `game.tasks.current` | Task status | Current | `DASHBOARD_PAGE` |
| `game.vote.recorded.title` | Submitted state | Vote recorded | `DASHBOARD_PAGE` |
| `game.vote.recorded.description` | Submitted state | Waiting for the rest of the players. | `DASHBOARD_PAGE` |
| `game.vote.title` | Voting heading | Vote for the saboteur | `DASHBOARD_PAGE` |
| `game.vote.label` | Vote input label | Choose a player | `DASHBOARD_PAGE` |
| `game.vote.submit` | Vote action | Submit Vote | `DASHBOARD_PAGE` |
| `game.task.turn` | Active-turn heading | Your task turn | `DASHBOARD_PAGE` |
| `game.task.complete` | Task action | Complete Task | `DASHBOARD_PAGE` |
| `game.task.sabotage` | Secret task action | Sabotage Task | `DASHBOARD_PAGE` |
| `game.task.wait.title` | Other-player turn | Waiting on task | `DASHBOARD_PAGE` |
| `game.task.wait.description` | Other-player turn | {player name} is handling the current task. | `DASHBOARD_PAGE` |
| `game.task.done.title` | Transition state | All tasks done | `DASHBOARD_PAGE` |
| `game.task.done.description` | Transition state | Voting will begin on refresh. | `DASHBOARD_PAGE` |

## Results

| ID | State / component | Current source text | Location |
| --- | --- | --- | --- |
| `game.results.meta.title` | Browser title | Hidden Saboteur Results | `RESULT_PAGE` |
| `game.results.new` | Navigation | New Game | `RESULT_PAGE` |
| `game.results.innocents.title` | Innocent win | Innocents win. | `RESULT_PAGE` |
| `game.results.innocents.description` | Innocent win | The group identified the saboteur before they could keep the points. | `RESULT_PAGE` |
| `game.results.saboteur.title` | Saboteur win | The saboteur survives. | `RESULT_PAGE` |
| `game.results.saboteur.description` | Saboteur win | The final vote missed the saboteur, so the sabotage points stand. | `RESULT_PAGE` |
| `game.results.saboteur` | Result fact | Saboteur: {player name} | `RESULT_PAGE` |
| `game.results.sabotages` | Result fact | {count} sabotages | `RESULT_PAGE` |
| `game.results.points` | Result fact | {count} points | `RESULT_PAGE` |
| `game.results.votes.title` | Vote list heading | Final votes | `RESULT_PAGE` |
| `game.results.vote` | Vote list row | {voter name} voted for {player name} | `RESULT_PAGE` |
| `game.results.votes.empty` | Empty state | No votes were recorded. | `RESULT_PAGE` |

## Product and state boundary

- The current application is a live, in-memory Flask prototype for separate
  browser sessions on one machine or a trusted LAN. It is not a static,
  pass-and-play demo and is not a hosted multiplayer service.
- Verify create, join, host-only start, role reveal, assigned task, sabotage,
  all-player vote, both result outcomes, late-join rejection, refresh, and
  invalid-room recovery states.
- Keep keyboard-visible focus, semantic labels, a 320 px layout, 200% zoom,
  and reduced-motion compatibility.
