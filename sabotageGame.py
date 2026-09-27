"""Compatibility entry point for the Hidden Saboteur app."""

import os

from sabotage_game import app

if __name__ == "__main__":
    app.run(host=os.getenv("SABOTAGE_HOST", "127.0.0.1"), port=5000, debug=False)
