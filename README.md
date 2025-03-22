# SabotageGame
# Hidden Saboteur - Multiplayer Game

**Hidden Saboteur** is a Flask-based multiplayer game where players join a game room, receive secret roles, and complete tasks while one player (the Saboteur) works to disrupt the team. After task completion, players vote on who they believe is the Saboteur, and the final results are displayed.

> **Disclaimer:** This project is intended for educational and entertainment purposes only. Use responsibly and only with the consent of all participants.

## Overview

- **Game Room Creation:**  
  Generate a unique game code to host a new game room.

- **Player Join:**  
  Players can join an existing game by entering the game code and their name.

- **Role Assignment:**  
  One randomly chosen player becomes the Saboteur; all others are Innocents.

- **Task Phase:**  
  Players are assigned tasks in a random order. The Saboteur can choose to either complete or sabotage their task.

- **Voting Phase:**  
  After tasks are done, all players vote to identify the Saboteur.

- **Final Results:**  
  The game ends with a final results page showing the Saboteur, the number of sabotages, and points awarded.

- **Auto-Refresh UI:**  
  The inline HTML templates use meta refresh to update the game status periodically.

## Prerequisites

- Python 3.x
- [Flask](https://flask.palletsprojects.com/)

Install Flask using pip:

```bash
pip install flask
