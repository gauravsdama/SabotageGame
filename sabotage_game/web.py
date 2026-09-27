"""Flask routes and request-boundary protections."""

from __future__ import annotations

import hmac
import os
import secrets

from flask import Flask, Response, redirect, render_template, request, session, url_for

from .domain import Game, GameError, Phase
from .store import RoomStore


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def create_app(*, store: RoomStore | None = None) -> Flask:
    application = Flask(__name__)
    application.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    application.config.update(
        MAX_CONTENT_LENGTH=16 * 1024,
        MAX_FORM_MEMORY_SIZE=16 * 1024,
        MAX_FORM_PARTS=16,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    trusted_hosts = os.getenv("SABOTAGE_TRUSTED_HOSTS")
    if trusted_hosts:
        application.config["TRUSTED_HOSTS"] = [
            host.strip() for host in trusted_hosts.split(",") if host.strip()
        ]

    rooms = (
        store
        if store is not None
        else RoomStore(
            max_rooms=_positive_int("SABOTAGE_MAX_ROOMS", 64),
            max_players=_positive_int("SABOTAGE_MAX_PLAYERS", 16),
            room_ttl_seconds=_positive_int("SABOTAGE_ROOM_TTL_SECONDS", 6 * 60 * 60),
            finished_ttl_seconds=_positive_int("SABOTAGE_FINISHED_TTL_SECONDS", 60 * 60),
        )
    )
    application.extensions["room_store"] = rooms

    def csrf_token() -> str:
        token = session.get("csrf_token")
        if not isinstance(token, str):
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return token

    @application.before_request
    def protect_mutations() -> Response | None:
        if request.method != "POST":
            return None
        expected = session.get("csrf_token")
        supplied = request.form.get("csrf_token")
        if not isinstance(expected, str) or not isinstance(supplied, str):
            return Response(status=400)
        if not hmac.compare_digest(expected, supplied):
            return Response(status=403)
        return None

    @application.after_request
    def secure_response(response: Response) -> Response:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    def rejected(error: GameError) -> Response:
        return Response(status=error.status_code)

    def player_id_for(game: Game) -> str | None:
        if session.get("game_code") != game.code:
            return None
        player_id = session.get("player_id")
        return player_id if isinstance(player_id, str) and player_id in game.players else None

    @application.get("/")
    def home() -> str:
        return render_template("home.html", csrf_token=csrf_token(), auto_refresh=False)

    @application.post("/create_game")
    def create_game() -> Response:
        try:
            game = rooms.create()
        except GameError as error:
            return rejected(error)
        preserved_csrf = session["csrf_token"]
        session.clear()
        session["csrf_token"] = preserved_csrf
        session["pending_host_game_code"] = game.code
        return redirect(url_for("join_game", game_code=game.code), code=303)

    @application.get("/join_game")
    def join_game() -> str | Response:
        game_code = request.args.get("game_code", "").strip().upper()
        if len(game_code) != 6 or not game_code.isalnum():
            return Response(status=400)
        game = rooms.snapshot(game_code)
        if game is None:
            return Response(status=404)
        if game.phase is not Phase.LOBBY:
            return Response(status=409)
        return render_template(
            "join.html", game_code=game_code, csrf_token=csrf_token(), auto_refresh=False
        )

    @application.post("/join_game/<game_code>")
    def join_game_post(game_code: str) -> Response:
        game_code = game_code.upper()
        player_name = request.form.get("player_name", "").strip()
        if not player_name or len(player_name) > 40:
            return Response(status=400)
        if session.get("game_code") == game_code and isinstance(session.get("player_id"), str):
            return Response(status=409)
        player_id = secrets.token_urlsafe(18)
        is_pending_host = session.get("pending_host_game_code") == game_code
        try:
            with rooms.locked(game_code) as game:
                game.add_player(
                    player_id,
                    player_name,
                    as_host=is_pending_host,
                    max_players=rooms.max_players,
                )
        except GameError as error:
            return rejected(error)
        session.pop("pending_host_game_code", None)
        session["game_code"] = game_code
        session["player_id"] = player_id
        return redirect(url_for("lobby", game_code=game_code), code=303)

    @application.get("/lobby/<game_code>")
    def lobby(game_code: str) -> str | Response:
        game = rooms.snapshot(game_code.upper())
        if game is None:
            return Response(status=404)
        player_id = player_id_for(game)
        if player_id is None:
            return Response(status=403)
        if game.phase is not Phase.LOBBY:
            return redirect(url_for("player_dashboard"), code=303)
        is_host = player_id == game.host_id
        return render_template(
            "lobby.html",
            game=game,
            is_host=is_host,
            csrf_token=csrf_token(),
            auto_refresh=not is_host,
        )

    @application.post("/start_game/<game_code>")
    def start_game(game_code: str) -> Response:
        try:
            with rooms.locked(game_code.upper()) as game:
                player_id = player_id_for(game)
                if player_id is None:
                    raise GameError(403)
                game.start(player_id)
        except GameError as error:
            return rejected(error)
        return redirect(url_for("player_dashboard"), code=303)

    @application.get("/dashboard")
    def player_dashboard() -> str | Response:
        game_code = session.get("game_code")
        if not isinstance(game_code, str):
            return Response(status=403)
        game = rooms.snapshot(game_code)
        if game is None:
            return Response(status=404)
        player_id = player_id_for(game)
        if player_id is None:
            return Response(status=403)
        player = game.players[player_id]
        waiting_for_task = (
            game.phase is Phase.TASKS
            and player.has_seen_role
            and game.assigned_order[game.task_index] != player_id
        )
        auto_refresh = (
            game.phase is Phase.LOBBY
            or waiting_for_task
            or (game.phase is Phase.VOTING and player_id in game.votes)
        )
        return render_template(
            "dashboard.html",
            game=game,
            player=player,
            player_id=player_id,
            has_voted=player_id in game.votes,
            csrf_token=csrf_token(),
            auto_refresh=auto_refresh,
        )

    @application.post("/reveal_role/<game_code>")
    def reveal_role(game_code: str) -> Response:
        try:
            with rooms.locked(game_code.upper()) as game:
                player_id = player_id_for(game)
                if player_id is None:
                    raise GameError(403)
                game.reveal_role(player_id)
        except GameError as error:
            return rejected(error)
        return redirect(url_for("player_dashboard"), code=303)

    @application.post("/do_task/<game_code>")
    def do_task(game_code: str) -> Response:
        try:
            with rooms.locked(game_code.upper()) as game:
                player_id = player_id_for(game)
                if player_id is None:
                    raise GameError(403)
                game.perform_task(player_id, request.form.get("action"))
        except GameError as error:
            return rejected(error)
        return redirect(url_for("player_dashboard"), code=303)

    @application.post("/cast_vote/<game_code>")
    def cast_vote(game_code: str) -> Response:
        try:
            with rooms.locked(game_code.upper()) as game:
                player_id = player_id_for(game)
                if player_id is None:
                    raise GameError(403)
                finished = game.cast_vote(player_id, request.form.get("vote"))
        except GameError as error:
            return rejected(error)
        destination = "display_results" if finished else "player_dashboard"
        values = {"game_code": game_code.upper()} if finished else {}
        return redirect(url_for(destination, **values), code=303)

    @application.get("/results/<game_code>")
    def display_results(game_code: str) -> str | Response:
        game = rooms.snapshot(game_code.upper())
        if game is None:
            return Response(status=404)
        if player_id_for(game) is None:
            return Response(status=403)
        if game.phase is not Phase.FINISHED:
            return Response(status=409)
        return render_template("results.html", game=game, auto_refresh=False)

    @application.get("/show_results/<game_code>")
    def show_results_redirect(game_code: str) -> Response:
        return redirect(url_for("display_results", game_code=game_code.upper()), code=303)

    return application


game_store = RoomStore(
    max_rooms=_positive_int("SABOTAGE_MAX_ROOMS", 64),
    max_players=_positive_int("SABOTAGE_MAX_PLAYERS", 16),
    room_ttl_seconds=_positive_int("SABOTAGE_ROOM_TTL_SECONDS", 6 * 60 * 60),
    finished_ttl_seconds=_positive_int("SABOTAGE_FINISHED_TTL_SECONDS", 60 * 60),
)
app = create_app(store=game_store)
