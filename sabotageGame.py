import os
import secrets
import string

from flask import Flask, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# GAMES will store all ongoing games in memory:
# GAMES[game_code] = {
#     "players": {
#         player_id: {
#             "name": str,
#             "role": "Saboteur" or "Innocent",
#             "has_seen_role": bool,
#             "has_voted": False
#         },
#         ...
#     },
#     "started": bool,
#     "saboteur_id": str,
#     "sabotages": int,         # how many times sabotage occurred
#     "saboteur_points": int,   # points if saboteur survives final vote
#     "assigned_order": [list_of_player_ids_for_tasks],
#     "task_index": int,        # which assigned task we are on
#     "num_tasks": int,
#     "votes": {},              # who each player voted for in final vote
#     "voting_active": bool,    # True after tasks are done
#     "finished": bool          # True once final results are shown
# }

GAMES = {}

# --------------------------------------
# Inline HTML Templates with Auto-Refresh
# --------------------------------------
PAGE_STYLES = """
<style>
    :root {
        --bg: #f3f0eb;
        --ink: #171717;
        --muted: #625f59;
        --panel: #fffdfa;
        --line: #d9d1c5;
        --red: #b4332b;
        --red-dark: #7f211d;
        --gold: #cc9a38;
        --green: #247a61;
        --shadow: 0 24px 70px rgba(48, 30, 21, 0.14);
    }

    * { box-sizing: border-box; }
    body {
        min-width: 320px;
        margin: 0;
        color: var(--ink);
        background:
            linear-gradient(135deg, rgba(180, 51, 43, 0.08), transparent 32%),
            linear-gradient(45deg, transparent 0 48%, rgba(23, 23, 23, 0.045) 48% 52%, transparent 52%),
            var(--bg);
        background-size: auto, 36px 36px, auto;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    a { color: inherit; }
    .shell {
        width: min(1120px, calc(100% - 32px));
        margin: 0 auto;
        padding: 26px 0 56px;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 54px;
    }

    .brand {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        text-decoration: none;
        font-weight: 900;
    }

    .brand-mark {
        display: grid;
        width: 44px;
        height: 44px;
        place-items: center;
        border-radius: 8px;
        color: #fff8ef;
        background: var(--red-dark);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.8rem;
        letter-spacing: 0;
    }

    .nav-link, button, .button {
        display: inline-flex;
        min-height: 44px;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 10px 14px;
        background: rgba(255, 253, 250, 0.86);
        color: var(--ink);
        font: inherit;
        font-weight: 800;
        text-decoration: none;
        cursor: pointer;
    }

    button.primary, .button.primary {
        border-color: var(--red-dark);
        background: var(--red-dark);
        color: #fff8ef;
    }

    button.danger {
        border-color: var(--red);
        background: var(--red);
        color: #fff8ef;
    }

    button:hover, .button:hover, .nav-link:hover {
        transform: translateY(-1px);
    }

    h1, h2, h3, p { margin-top: 0; }
    h1 {
        max-width: 740px;
        margin-bottom: 16px;
        font-size: clamp(2.4rem, 7vw, 5.2rem);
        line-height: 0.95;
        letter-spacing: 0;
    }

    h2 { margin-bottom: 14px; font-size: 1.4rem; }
    h3 { margin-bottom: 10px; font-size: 1.1rem; }
    p { color: var(--muted); line-height: 1.65; }

    .eyebrow {
        margin: 0 0 12px;
        color: var(--red-dark);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.78rem;
        font-weight: 900;
        text-transform: uppercase;
    }

    .hero-grid, .content-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(320px, 0.92fr);
        gap: 28px;
        align-items: start;
    }

    .panel {
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 24px;
        background: rgba(255, 253, 250, 0.94);
        box-shadow: var(--shadow);
    }

    .form-stack, .stack {
        display: grid;
        gap: 14px;
    }

    label {
        display: block;
        margin-bottom: 7px;
        color: #35312b;
        font-size: 0.86rem;
        font-weight: 850;
    }

    input, select {
        width: 100%;
        min-height: 46px;
        border: 1px solid #cfc4b8;
        border-radius: 8px;
        padding: 10px 12px;
        background: #ffffff;
        color: var(--ink);
        font: inherit;
    }

    input:focus, select:focus, button:focus, a:focus {
        outline: 3px solid rgba(180, 51, 43, 0.22);
        outline-offset: 2px;
    }

    .code-card {
        display: grid;
        min-height: 220px;
        place-items: center;
        border: 1px dashed rgba(127, 33, 29, 0.38);
        border-radius: 8px;
        background: #fff8ef;
        text-align: center;
    }

    .code-card strong {
        color: var(--red-dark);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: clamp(2.6rem, 9vw, 5.4rem);
        letter-spacing: 0;
    }

    ul {
        display: grid;
        gap: 8px;
        margin: 14px 0 0;
        padding: 0;
        list-style: none;
    }

    li {
        border: 1px solid rgba(217, 209, 197, 0.86);
        border-radius: 8px;
        padding: 11px 12px;
        background: rgba(255, 255, 255, 0.58);
        font-weight: 750;
    }

    .status-row, .action-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
    }

    .pill {
        display: inline-flex;
        min-height: 34px;
        align-items: center;
        border-radius: 8px;
        padding: 7px 10px;
        color: #2c2a27;
        background: #eee5d8;
        font-size: 0.84rem;
        font-weight: 850;
    }

    .pill.red { color: #fff8ef; background: var(--red-dark); }
    .pill.green { color: #f6fff9; background: var(--green); }
    .pill.gold { background: #f5dfad; }

    .divider {
        height: 1px;
        margin: 18px 0;
        background: var(--line);
    }

    @media (max-width: 820px) {
        .topbar { align-items: flex-start; flex-direction: column; margin-bottom: 34px; }
        .hero-grid, .content-grid { grid-template-columns: 1fr; }
        .panel { padding: 20px; }
    }
</style>
"""


@app.context_processor
def inject_styles():
    return {"styles": PAGE_STYLES}


HOME_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hidden Saboteur</title>
    {{ styles|safe }}
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <a class="brand" href="{{ url_for('home') }}">
                <span class="brand-mark">HS</span>
                <span>Hidden Saboteur</span>
            </a>
            <span class="pill gold">Local party game</span>
        </header>

        <section class="hero-grid">
            <div>
                <h1>Find the hidden saboteur before the team falls apart.</h1>
                <p>Create a room, share the code, assign secret roles, run tasks, and vote before the saboteur gets away with the points.</p>
            </div>

            <div class="panel form-stack">
                <form action="{{ url_for('create_game') }}" method="POST" class="form-stack">
                    <h2>Create room</h2>
                    <p>Start a fresh game and invite players with a short room code.</p>
                    <button type="submit" class="primary">Create Game Room</button>
                </form>

                <div class="divider"></div>

                <form action="{{ url_for('join_game') }}" method="GET" class="form-stack">
                    <h2>Join room</h2>
                    <div>
                        <label for="game_code">Game code</label>
                        <input id="game_code" type="text" name="game_code" maxlength="6" placeholder="A1B2C3" required>
                    </div>
                    <button type="submit">Join Game</button>
                </form>
            </div>
        </section>
    </main>
</body>
</html>
"""

JOIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Join Hidden Saboteur</title>
    {{ styles|safe }}
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <a class="brand" href="{{ url_for('home') }}">
                <span class="brand-mark">HS</span>
                <span>Hidden Saboteur</span>
            </a>
            <a class="nav-link" href="{{ url_for('home') }}">Home</a>
        </header>

        <section class="content-grid">
            <div>
                <h1>Enter your player name.</h1>
                <p>You are joining room <strong>{{ game_code }}</strong>. Your role stays hidden until the game starts.</p>
            </div>
            <form class="panel form-stack" action="{{ url_for('join_game_post', game_code=game_code) }}" method="POST">
                <div>
                    <label for="player_name">Player name</label>
                    <input id="player_name" type="text" name="player_name" maxlength="40" placeholder="Gaurav" required>
                </div>
                <button type="submit" class="primary">Join Room</button>
            </form>
        </section>
    </main>
</body>
</html>
"""

LOBBY_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <title>Hidden Saboteur Lobby</title>
    {{ styles|safe }}
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <a class="brand" href="{{ url_for('home') }}">
                <span class="brand-mark">HS</span>
                <span>Hidden Saboteur</span>
            </a>
            <a class="nav-link" href="{{ url_for('player_dashboard') }}">My Dashboard</a>
        </header>

        <section class="content-grid">
            <div>
                <h1>Room {{ game_code }}</h1>
                <p>Share the room code, wait for players, then start once everyone is ready.</p>
                <div class="code-card" aria-label="Game code">
                    <strong>{{ game_code }}</strong>
                </div>
            </div>

            <div class="panel">
                <div class="status-row">
                    <span class="pill {% if started %}green{% else %}gold{% endif %}">
                        {% if started %}Started{% else %}Waiting{% endif %}
                    </span>
                    <span class="pill">{{ players|length }} players</span>
                </div>
                <h2>Players</h2>
                {% if players %}
                    <ul>
                        {% for pid, info in players.items() %}
                            <li>{{ info.name }}</li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p>No players have joined yet.</p>
                {% endif %}

                {% if not started and is_host %}
                    <div class="divider"></div>
                    <form method="POST" action="{{ url_for('start_game', game_code=game_code) }}">
                        <button type="submit" class="primary">Start Game</button>
                    </form>
                {% endif %}
            </div>
        </section>
    </main>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <title>Hidden Saboteur Dashboard</title>
    {{ styles|safe }}
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <a class="brand" href="{{ url_for('home') }}">
                <span class="brand-mark">HS</span>
                <span>Hidden Saboteur</span>
            </a>
            <a class="nav-link" href="{{ url_for('lobby', game_code=game_code) }}">Lobby</a>
        </header>

        <section class="content-grid">
            <div>
                <h1>Hello, {{ player_name }}</h1>
                <p>Room <strong>{{ game_code }}</strong> is your current game. Keep your role private and watch the task order.</p>
                <div class="status-row">
                    <span class="pill {% if started %}green{% else %}gold{% endif %}">
                        {% if started %}Game started{% else %}Waiting to start{% endif %}
                    </span>
                    <span class="pill red">{{ sabotages }} sabotages</span>
                    {% if voting_active %}<span class="pill gold">Voting active</span>{% endif %}
                </div>
            </div>

            <div class="panel stack">
                {% if finished %}
                    <h2>Game ended</h2>
                    <p>The final results are ready.</p>
                    <a class="button primary" href="{{ url_for('show_results_redirect', game_code=game_code) }}">View Results</a>
                {% elif not started %}
                    <h2>Waiting for host</h2>
                    <p>The game has not started yet. Return to the lobby while more players join.</p>
                    <a class="button" href="{{ url_for('lobby', game_code=game_code) }}">Return to Lobby</a>
                {% else %}
                    <h2>Your role</h2>
                    {% if has_seen_role %}
                        <span class="pill {% if role == 'Saboteur' %}red{% else %}green{% endif %}">{{ role }}</span>
                    {% else %}
                        <form method="POST" action="{{ url_for('reveal_role', game_code=game_code) }}">
                            <button type="submit" class="primary">Reveal My Role</button>
                        </form>
                    {% endif %}

                    {% if assigned_order %}
                        <div class="divider"></div>
                        <h2>Task order</h2>
                        <ul>
                            {% for ap in assigned_order %}
                                <li>
                                    {{ players[ap].name }}
                                    {% if loop.index0 == task_index %}
                                        <span class="pill gold">Current</span>
                                    {% endif %}
                                </li>
                            {% endfor %}
                        </ul>
                    {% endif %}

                    {% if has_seen_role %}
                        <div class="divider"></div>
                        {% if voting_active %}
                            {% if has_voted %}
                                <h2>Vote recorded</h2>
                                <p>Waiting for the rest of the players.</p>
                            {% else %}
                                <h2>Vote for the saboteur</h2>
                                <form class="form-stack" method="POST" action="{{ url_for('cast_vote', game_code=game_code) }}">
                                    <div>
                                        <label for="vote">Choose a player</label>
                                        <select id="vote" name="vote" required>
                                            {% for pid, info in players.items() %}
                                                <option value="{{ pid }}">{{ info.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                    <button type="submit" class="primary">Submit Vote</button>
                                </form>
                            {% endif %}
                        {% elif task_index < num_tasks %}
                            {% set current_player = assigned_order[task_index] %}
                            {% if my_pid == current_player %}
                                <h2>Your task turn</h2>
                                <form class="action-row" method="POST" action="{{ url_for('do_task', game_code=game_code) }}">
                                    <button type="submit" name="action" value="complete" class="primary">Complete Task</button>
                                    {% if role == 'Saboteur' %}
                                        <button type="submit" name="action" value="sabotage" class="danger">Sabotage Task</button>
                                    {% endif %}
                                </form>
                            {% else %}
                                <h2>Waiting on task</h2>
                                <p>{{ players[current_player].name }} is handling the current task.</p>
                            {% endif %}
                        {% else %}
                            <h2>All tasks done</h2>
                            <p>Voting will begin on refresh.</p>
                        {% endif %}
                    {% endif %}
                {% endif %}
            </div>
        </section>
    </main>
</body>
</html>
"""

RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hidden Saboteur Results</title>
    {{ styles|safe }}
</head>
<body>
    <main class="shell">
        <header class="topbar">
            <a class="brand" href="{{ url_for('home') }}">
                <span class="brand-mark">HS</span>
                <span>Hidden Saboteur</span>
            </a>
            <a class="nav-link" href="{{ url_for('home') }}">New Game</a>
        </header>

        <section class="content-grid">
            <div>
                {% if saboteur_out %}
                    <h1>Innocents win.</h1>
                    <p>The group identified the saboteur before they could keep the points.</p>
                {% else %}
                    <h1>The saboteur survives.</h1>
                    <p>The final vote missed the saboteur, so the sabotage points stand.</p>
                {% endif %}
                <div class="status-row">
                    <span class="pill red">Saboteur: {{ sab_name }}</span>
                    <span class="pill">{{ sabotages }} sabotages</span>
                    <span class="pill gold">{{ sab_points }} points</span>
                </div>
            </div>

            <div class="panel">
                <h2>Final votes</h2>
                {% if votes %}
                    <ul>
                        {% for voter_id, target_id in votes.items() %}
                            <li>{{ players[voter_id].name }} voted for {{ players[target_id].name }}</li>
                        {% endfor %}
                    </ul>
                {% else %}
                    <p>No votes were recorded.</p>
                {% endif %}
            </div>
        </section>
    </main>
</body>
</html>
"""


# --------------------------------------
# Helper Functions
# --------------------------------------
def generate_game_code(length=6):
    """Generate a random game code of letters/numbers."""
    chars = string.ascii_uppercase + string.digits
    for _ in range(100):
        game_code = "".join(secrets.choice(chars) for _ in range(length))
        if game_code not in GAMES:
            return game_code
    raise RuntimeError("Could not allocate a unique game code")


def generate_player_id():
    """Generate a unique player ID."""
    return secrets.token_urlsafe(18)


def session_player_for(game_code):
    """Return the current session's player ID only for its active room."""
    if session.get("game_code") != game_code:
        return None
    return session.get("player_id")


def get_current_game():
    """Get the game dictionary for the user's session."""
    game_code = session.get("game_code")
    if not game_code or game_code not in GAMES:
        return None
    return GAMES[game_code]


def get_my_player_id():
    """Get the player's unique ID from session."""
    return session.get("player_id")


# --------------------------------------
# ROUTES
# --------------------------------------
@app.route("/")
def home():
    return render_template_string(HOME_PAGE)


@app.route("/create_game", methods=["POST"])
def create_game():
    """Create a new game and send its creator through the player join step."""
    game_code = generate_game_code()
    GAMES[game_code] = {
        "players": {},
        "host_id": None,
        "started": False,
        "saboteur_id": None,
        "sabotages": 0,
        "saboteur_points": 0,
        "assigned_order": [],
        "task_index": 0,
        "num_tasks": 0,
        "votes": {},
        "voting_active": False,
        "finished": False,
        "saboteur_out": None,
    }
    session.clear()
    session["pending_host_game_code"] = game_code
    return redirect(url_for("join_game", game_code=game_code))


@app.route("/join_game", methods=["GET"])
def join_game():
    """Enter a game code to join."""
    game_code = request.args.get("game_code", "").strip().upper()
    if not game_code or game_code not in GAMES:
        return redirect(url_for("home"))
    if GAMES[game_code]["started"]:
        return redirect(url_for("home"))
    return render_template_string(JOIN_PAGE, game_code=game_code)


@app.route("/join_game/<game_code>", methods=["POST"])
def join_game_post(game_code):
    """User enters name to join the game."""
    if game_code not in GAMES:
        return redirect(url_for("home"))
    if GAMES[game_code]["started"]:
        return redirect(url_for("home"))

    player_name = request.form.get("player_name", "").strip()[:40]
    if not player_name:
        return redirect(url_for("join_game", game_code=game_code))

    pid = generate_player_id()
    GAMES[game_code]["players"][pid] = {
        "name": player_name,
        "role": None,
        "has_seen_role": False,
        "has_voted": False,
    }
    session["game_code"] = game_code
    session["player_id"] = pid
    if session.pop("pending_host_game_code", None) == game_code:
        GAMES[game_code]["host_id"] = pid

    return redirect(url_for("lobby", game_code=game_code))


@app.route("/lobby/<game_code>")
def lobby(game_code):
    """Lobby: show all players, wait for host to start."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    players = game["players"]
    started = game["started"]
    pid = session_player_for(game_code)

    return render_template_string(
        LOBBY_PAGE,
        game_code=game_code,
        players=players,
        started=started,
        is_host=pid is not None and pid == game["host_id"],
    )


@app.route("/start_game/<game_code>", methods=["POST"])
def start_game(game_code):
    """Host starts the game:
    - 1 saboteur
    - tasks assigned to half the players
    - random order
    """
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    if session_player_for(game_code) != game["host_id"]:
        return redirect(url_for("lobby", game_code=game_code))
    if game["started"]:
        return redirect(url_for("lobby", game_code=game_code))

    player_ids = list(game["players"].keys())
    if len(player_ids) < 2:
        # Need at least 2 players
        return redirect(url_for("lobby", game_code=game_code))

    # Pick saboteur
    sab_id = secrets.choice(player_ids)
    game["saboteur_id"] = sab_id

    # Assign roles
    for pid in player_ids:
        if pid == sab_id:
            game["players"][pid]["role"] = "Saboteur"
        else:
            game["players"][pid]["role"] = "Innocent"

    # Assign tasks to half the players (rounded down)
    num_tasks = len(player_ids) // 2
    assigned = list(secrets.SystemRandom().sample(player_ids, num_tasks))
    secrets.SystemRandom().shuffle(assigned)

    game["num_tasks"] = num_tasks
    game["assigned_order"] = assigned
    game["task_index"] = 0
    game["sabotages"] = 0
    game["saboteur_points"] = 0
    game["votes"] = {}
    game["voting_active"] = False
    game["finished"] = False
    game["saboteur_out"] = None

    game["started"] = True
    return redirect(url_for("lobby", game_code=game_code))


@app.route("/dashboard")
def player_dashboard():
    """Personal dashboard for the current player."""
    game_code = session.get("game_code")
    game = get_current_game()
    if not game or not game_code:
        return redirect(url_for("home"))

    pid = session_player_for(game_code)
    if pid not in game["players"]:
        return redirect(url_for("home"))

    player_info = game["players"][pid]

    # If all tasks are done but we haven't started voting or finished game, start final voting
    if game["started"] and not game["finished"]:
        if game["task_index"] >= game["num_tasks"] and not game["voting_active"]:
            # All tasks complete -> begin final voting
            game["voting_active"] = True
            game["votes"] = {}

    return render_template_string(
        DASHBOARD_PAGE,
        game_code=session["game_code"],
        player_name=player_info["name"],
        started=game["started"],
        finished=game["finished"],
        role=player_info["role"],
        has_seen_role=player_info["has_seen_role"],
        sabotages=game["sabotages"],
        assigned_order=game["assigned_order"],
        task_index=game["task_index"],
        num_tasks=game["num_tasks"],
        voting_active=game["voting_active"],
        has_voted=(pid in game["votes"]),
        players=game["players"],
        my_pid=pid,
    )


@app.route("/reveal_role/<game_code>", methods=["POST"])
def reveal_role(game_code):
    """Mark that the player has seen their role."""
    if game_code not in GAMES:
        return redirect(url_for("home"))
    game = GAMES[game_code]

    pid = session_player_for(game_code)
    if pid not in game["players"]:
        return redirect(url_for("home"))

    game["players"][pid]["has_seen_role"] = True
    return redirect(url_for("player_dashboard"))


@app.route("/do_task/<game_code>", methods=["POST"])
def do_task(game_code):
    """The current assigned player chooses to complete or sabotage the task."""
    if game_code not in GAMES:
        return redirect(url_for("home"))
    game = GAMES[game_code]

    pid = session_player_for(game_code)
    if pid not in game["players"]:
        return redirect(url_for("home"))

    # If we've already done all tasks or game ended, no action
    if game["task_index"] >= game["num_tasks"] or game["finished"]:
        return redirect(url_for("player_dashboard"))

    current_player = game["assigned_order"][game["task_index"]]
    if pid != current_player:
        # Not your turn
        return redirect(url_for("player_dashboard"))

    action = request.form.get("action", "complete")
    if action not in {"complete", "sabotage"}:
        return redirect(url_for("player_dashboard"))

    # Only a saboteur can sabotage
    if action == "sabotage" and game["players"][pid]["role"] == "Saboteur":
        game["sabotages"] += 1

    # Move to next task (no immediate voting)
    game["task_index"] += 1

    return redirect(url_for("player_dashboard"))


@app.route("/cast_vote/<game_code>", methods=["POST"])
def cast_vote(game_code):
    """Each player casts one final vote for who they think is the Saboteur."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    if not game["voting_active"] or game["finished"]:
        # No active voting or game ended
        return redirect(url_for("player_dashboard"))

    pid = session_player_for(game_code)
    if pid not in game["players"]:
        return redirect(url_for("home"))

    vote_for = request.form.get("vote")
    if vote_for in game["players"]:
        game["votes"][pid] = vote_for

    # Check if all players have voted
    if len(game["votes"]) == len(game["players"]):
        finalize_vote(game)
        return redirect(url_for("display_results", game_code=game_code))

    return redirect(url_for("player_dashboard"))


def finalize_vote(game):
    """Finalize a complete vote as part of the last voter's POST request."""
    sab_id = game["saboteur_id"]
    votes = game["votes"]
    # Count how many are for sab
    vote_count_for_sab = sum(1 for v in votes.values() if v == sab_id)
    majority_needed = (len(game["players"]) // 2) + 1

    # If sab is voted out, saboteur_out = True => sab has 0 points
    saboteur_out = vote_count_for_sab >= majority_needed

    if saboteur_out:
        # sab out => no points
        game["saboteur_points"] = 0
    else:
        # sab not out => saboteur_points = sabotages
        game["saboteur_points"] = game["sabotages"]

    # Mark game finished
    game["finished"] = True
    game["saboteur_out"] = saboteur_out


@app.route("/results/<game_code>")
def display_results(game_code):
    """Show the final results page after voting."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    if not game["finished"] or session_player_for(game_code) not in game["players"]:
        return redirect(url_for("player_dashboard"))
    saboteur_out = game["saboteur_out"]

    sab_id = game["saboteur_id"]
    sab_name = game["players"][sab_id]["name"]
    sabotages = game["sabotages"]
    sab_points = game["saboteur_points"]
    votes = game["votes"]
    players = game["players"]

    return render_template_string(
        RESULT_PAGE,
        sab_name=sab_name,
        sab_id=sab_id,
        sabotages=sabotages,
        sab_points=sab_points,
        saboteur_out=saboteur_out,
        votes=votes,
        players=players,
    )


@app.route("/show_results/<game_code>")
def show_results_redirect(game_code):
    """Convenience redirect to final results."""
    return redirect(url_for("display_results", game_code=game_code))


# --------------------------------------
# Run the server
# --------------------------------------
if __name__ == "__main__":
    app.run(host=os.getenv("SABOTAGE_HOST", "127.0.0.1"), port=5000, debug=False)
