from flask import Flask, render_template_string, request, redirect, url_for, session
import random
import string

app = Flask(__name__)
app.secret_key = "super_secret_key_for_sessions"

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
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hidden Saboteur - Home</title>
    <!-- Auto-refresh every 5s to see if changes happen -->
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Welcome to the Hidden Saboteur Game</h1>
    <p>Create a new game or join an existing one.</p>
    <h2>Create New Game</h2>
    <form action="/create_game" method="POST">
        <button type="submit">Create Game Room</button>
    </form>
    <h2>Join Existing Game</h2>
    <form action="/join_game" method="GET">
        <label for="game_code">Enter Game Code:</label>
        <input type="text" name="game_code" required>
        <button type="submit">Join</button>
    </form>
</body>
</html>
"""

JOIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Join Game</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Join Game: {{ game_code }}</h1>
    <form action="{{ url_for('join_game_post', game_code=game_code) }}" method="POST">
        <label for="player_name">Your Name:</label>
        <input type="text" name="player_name" required>
        <button type="submit">Join</button>
    </form>
    <p><a href="{{ url_for('home') }}">Back to Home</a></p>
</body>
</html>
"""

LOBBY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Lobby</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Game Lobby - Code: {{ game_code }}</h1>
    <p>Players in this game:</p>
    <ul>
        {% for pid, info in players.items() %}
            <li>{{ info.name }}</li>
        {% endfor %}
    </ul>
    {% if not started %}
        <p>Share this code with others to join: <strong>{{ game_code }}</strong></p>
        <form method="POST" action="{{ url_for('start_game', game_code=game_code) }}">
            <button type="submit">Start Game</button>
        </form>
    {% else %}
        <p>The game has started!</p>
    {% endif %}
    <p><a href="{{ url_for('player_dashboard') }}">Go to My Dashboard</a></p>
</body>
</html>
"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>My Dashboard</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Hello, {{ player_name }}</h1>
    <p>Game Code: {{ game_code }}</p>

    {% if finished %}
        <h3>The game has ended. See final results:</h3>
        <a href="{{ url_for('show_results_redirect', game_code=game_code) }}">View Results</a>
        <hr>
        <p><a href="{{ url_for('lobby', game_code=game_code) }}">Back to Lobby</a></p>
        </body></html>
        <!-- end early because the game is done -->
        {% exit() %} 
    {% endif %}

    {% if not started %}
        <p>The game has not started yet. Wait for the host to start the game or return to the lobby.</p>
        <a href="{{ url_for('lobby', game_code=game_code) }}">Return to Lobby</a>
    {% else %}
        <h3>Your Role:</h3>
        {% if has_seen_role %}
            <p><strong>{{ role }}</strong></p>
        {% else %}
            <form method="POST" action="{{ url_for('reveal_role', game_code=game_code) }}">
                <button type="submit">Reveal My Role</button>
            </form>
        {% endif %}

        <hr>
        <p><strong>Total Sabotages So Far:</strong> {{ sabotages }}</p>

        <!-- Show assigned tasks list if any -->
        {% if assigned_order %}
            <p>Tasks assigned to these players (random order):</p>
            <ul>
                {% for ap in assigned_order %}
                    <li>
                       {{ players[ap].name }}
                       {% if loop.index0 == task_index %}
                          <strong>(Current Task)</strong>
                       {% endif %}
                    </li>
                {% endfor %}
            </ul>
        {% endif %}

        {% if has_seen_role %}
            {% if voting_active %}
                <!-- Final Voting Phase -->
                {% if has_voted %}
                    <h2>You have voted. Waiting for others...</h2>
                {% else %}
                    <h2>Vote: Who is the Saboteur?</h2>
                    <form method="POST" action="{{ url_for('cast_vote', game_code=game_code) }}">
                        <label for="vote">Choose a player:</label>
                        <select name="vote" required>
                            {% for pid, info in players.items() %}
                                <option value="{{ pid }}">{{ info.name }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit">Submit Vote</button>
                    </form>
                {% endif %}
            {% else %}
                <!-- Task Phase -->
                {% if task_index < num_tasks %}
                    {% set current_player = assigned_order[task_index] %}
                    {% if my_pid == current_player %}
                        <h3>It's YOUR turn to handle the task.</h3>
                        {% if role == 'Saboteur' %}
                            <form method="POST" action="{{ url_for('do_task', game_code=game_code) }}">
                                <button type="submit" name="action" value="complete">Complete Task</button>
                                <button type="submit" name="action" value="sabotage">Sabotage Task</button>
                            </form>
                        {% else %}
                            <!-- Innocent can only complete -->
                            <form method="POST" action="{{ url_for('do_task', game_code=game_code) }}">
                                <button type="submit" name="action" value="complete">Complete Task</button>
                            </form>
                        {% endif %}
                    {% else %}
                        <p>Waiting for {{ players[current_player].name }} to complete their task.</p>
                    {% endif %}
                {% else %}
                    <h2>All Tasks Done</h2>
                    <p>Voting will begin soon (or refresh to see if it started).</p>
                {% endif %}
            {% endif %}
        {% endif %}
    {% endif %}
    <hr>
    <p><a href="{{ url_for('lobby', game_code=game_code) }}">Back to Lobby</a></p>
</body>
</html>
"""

RESULT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Game Results</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Game Over!</h1>
    <p>The Saboteur was: <strong>{{ sab_name }}</strong> (ID: {{ sab_id }})</p>
    <p>Total Sabotages: {{ sabotages }}</p>
    {% if saboteur_out %}
        <h2>The saboteur was voted out! Innocents Win.</h2>
        <p>Saboteur points: 0</p>
    {% else %}
        <h2>The saboteur survived the final vote!</h2>
        <p>Saboteur points: {{ sab_points }}</p>
    {% endif %}

    <h3>Final Votes:</h3>
    <ul>
      {% for voter_id, target_id in votes.items() %}
        <li>{{ players[voter_id].name }} voted for {{ players[target_id].name }}</li>
      {% endfor %}
    </ul>

    <p><a href="{{ url_for('home') }}">Return Home</a></p>
</body>
</html>
"""

# --------------------------------------
# Helper Functions
# --------------------------------------
def generate_game_code(length=6):
    """Generate a random game code of letters/numbers."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_player_id():
    """Generate a unique player ID."""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

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
    """Create a new game and redirect to the lobby."""
    game_code = generate_game_code()
    GAMES[game_code] = {
        "players": {},
        "started": False,
        "saboteur_id": None,
        "sabotages": 0,
        "saboteur_points": 0,
        "assigned_order": [],
        "task_index": 0,
        "num_tasks": 0,
        "votes": {},
        "voting_active": False,
        "finished": False
    }
    return redirect(url_for("lobby", game_code=game_code))

@app.route("/join_game", methods=["GET"])
def join_game():
    """Enter a game code to join."""
    game_code = request.args.get("game_code")
    if not game_code or game_code not in GAMES:
        return redirect(url_for("home"))
    return render_template_string(JOIN_PAGE, game_code=game_code)

@app.route("/join_game/<game_code>", methods=["POST"])
def join_game_post(game_code):
    """User enters name to join the game."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    player_name = request.form.get("player_name")
    if not player_name:
        return redirect(url_for("join_game", game_code=game_code))

    pid = generate_player_id()
    GAMES[game_code]["players"][pid] = {
        "name": player_name,
        "role": None,
        "has_seen_role": False,
        "has_voted": False
    }
    session["game_code"] = game_code
    session["player_id"] = pid

    return redirect(url_for("lobby", game_code=game_code))

@app.route("/lobby/<game_code>")
def lobby(game_code):
    """Lobby: show all players, wait for host to start."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    players = game["players"]
    started = game["started"]

    return render_template_string(
        LOBBY_PAGE,
        game_code=game_code,
        players=players,
        started=started
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
    if game["started"]:
        return redirect(url_for("lobby", game_code=game_code))

    player_ids = list(game["players"].keys())
    if len(player_ids) < 2:
        # Need at least 2 players
        return redirect(url_for("lobby", game_code=game_code))

    # Pick saboteur
    sab_id = random.choice(player_ids)
    game["saboteur_id"] = sab_id

    # Assign roles
    for pid in player_ids:
        if pid == sab_id:
            game["players"][pid]["role"] = "Saboteur"
        else:
            game["players"][pid]["role"] = "Innocent"

    # Assign tasks to half the players (rounded down)
    num_tasks = len(player_ids) // 2
    assigned = random.sample(player_ids, num_tasks)
    random.shuffle(assigned)

    game["num_tasks"] = num_tasks
    game["assigned_order"] = assigned
    game["task_index"] = 0
    game["sabotages"] = 0
    game["saboteur_points"] = 0
    game["votes"] = {}
    game["voting_active"] = False
    game["finished"] = False

    game["started"] = True
    return redirect(url_for("lobby", game_code=game_code))

@app.route("/dashboard")
def player_dashboard():
    """Personal dashboard for the current player."""
    game = get_current_game()
    if not game:
        return redirect(url_for("home"))

    pid = get_my_player_id()
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
        my_pid=pid
    )

@app.route("/reveal_role/<game_code>", methods=["POST"])
def reveal_role(game_code):
    """Mark that the player has seen their role."""
    if game_code not in GAMES:
        return redirect(url_for("home"))
    game = GAMES[game_code]

    pid = get_my_player_id()
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

    pid = get_my_player_id()
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

    pid = get_my_player_id()
    if pid not in game["players"]:
        return redirect(url_for("home"))

    vote_for = request.form.get("vote")
    if vote_for in game["players"]:
        game["votes"][pid] = vote_for

    # Check if all players have voted
    if len(game["votes"]) == len(game["players"]):
        # Tally & finalize game
        return redirect(url_for("finalize_vote", game_code=game_code))

    return redirect(url_for("player_dashboard"))

@app.route("/finalize_vote/<game_code>")
def finalize_vote(game_code):
    """Once everyone voted, see if the saboteur is majority. Then finalize."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    if game["finished"]:
        return redirect(url_for("player_dashboard"))

    sab_id = game["saboteur_id"]
    votes = game["votes"]
    # Count how many are for sab
    vote_count_for_sab = sum(1 for v in votes.values() if v == sab_id)
    majority_needed = (len(game["players"]) // 2) + 1

    # If sab is voted out, saboteur_out = True => sab has 0 points
    saboteur_out = (vote_count_for_sab >= majority_needed)

    if saboteur_out:
        # sab out => no points
        game["saboteur_points"] = 0
    else:
        # sab not out => saboteur_points = sabotages
        game["saboteur_points"] = game["sabotages"]

    # Mark game finished
    game["finished"] = True
    return redirect(url_for("display_results", game_code=game_code, saboteur_out="1" if saboteur_out else "0"))

@app.route("/results/<game_code>")
def display_results(game_code):
    """Show the final results page after voting."""
    if game_code not in GAMES:
        return redirect(url_for("home"))

    game = GAMES[game_code]
    sab_out_flag = request.args.get("saboteur_out", "0")
    saboteur_out = (sab_out_flag == "1")

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
        players=players
    )

@app.route("/show_results/<game_code>")
def show_results_redirect(game_code):
    """Convenience redirect to final results."""
    return redirect(url_for("display_results", game_code=game_code))

# --------------------------------------
# Run the server
# --------------------------------------
if __name__ == "__main__":
    # Host on 0.0.0.0 so others on LAN can join.
    app.run(host="0.0.0.0", port=5000, debug=True)
