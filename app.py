from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import pudb

# from codenames.cnai import Spymaster, W2VAssoc, W2VGuesser
# from codenames.cngame import Codenames

app = Flask(__name__)

app.secret_key = "859c86bf1895e69b3c6dfc1c6092a3b3c45d9b55f22ac29aa816ed87793c00b8"
socketio = SocketIO(app)

players = {}


@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/start")
# def start_game(
#     blue_spymaster=Spymaster(W2VAssoc()),
#     blue_guesser=W2VGuesser(),
#     red_spymaster=Spymaster(W2VAssoc()),
#     red_guesser=W2VGuesser(),
# ):
#     if "codenames" not in app.config:
#         app.config["codenames"] = Codenames(
#             blue_spymaster, blue_guesser, red_spymaster, red_guesser
#         )
#     return "Starting game!"


# Create new game
@app.route("/create")
def create_game():
    app.config["game_state"] = {
        "colors": [
            "U",
            "R",
            "N",
            "A",
            "U",
            "R",
            "N",
            "N",
            "R",
            "U",
            "N",
            "R",
            "U",
            "N",
            "N",
            "U",
            "R",
            "N",
            "U",
            "N",
            "N",
            "R",
            "U",
            "N",
            "R",
        ],
        "words": [
            "APPLE",
            "BOOK",
            "CAR",
            "DOG",
            "EGG",
            "FISH",
            "GAME",
            "HAT",
            "INK",
            "JURY",
            "KEY",
            "LAMP",
            "MAP",
            "NET",
            "ORANGE",
            "PEN",
            "QUEEN",
            "RAIN",
            "SUN",
            "TABLE",
            "UMBRELLA",
            "VIOLIN",
            "WATCH",
            "XRAY",
            "YACHT",
        ],
        "guessed": [
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
        ],
        "current_turn": "blue",
        "current_clue": {"word": "Red", "number": 1},
        "guesses_remaining": 1,
    }

    # Get the role and team parameters from the request
    role = request.args.get("role")
    team = request.args.get("team")

    # Construct the URL with the query parameters
    game_url = url_for("game", role=role, team=team)
    return redirect(game_url)


@app.route("/game")
def game():
    if "game_state" not in app.config:
        create_game()
    # Assign a role and team to the player
    role = request.args.get("role")
    team = request.args.get("team")
    player_id = session.get(
        "player_id", request.remote_addr
    )  # Use session or IP for simplicity
    players[player_id] = {"team": team, "role": role}
    print(role, team)
    return render_template(
        "game.html",
        game_state=app.config["game_state"],
        player_role=role,
        player_team=team,
    )


@app.post("/update_game_state")
def update_game_state():
    data = request.get_json()
    pu.db
    if "gameState" in data.keys():
        updated_state = data["gameState"]
        current_guess = data["currentGuess"]
        # Check if game is over
        if game_over(updated_state, current_guess):
            # TODO
            # End game
            pass
        # Check if we need to change turn
        if change_turn(updated_state, current_guess):
            if updated_state["current_turn"] == "blue":
                updated_state["current_turn"] = "red"
            else:
                updated_state["current_turn"] = "blue"
    else:
        updated_state = data

    app.config["game_state"].update(updated_state)

    socketio.emit("update", app.config["game_state"])

    # Return the updated game state back to the client
    return jsonify(app.config["game_state"])


def change_turn(game_state, current_guess):
    if (game_state["guesses_remaining"] == 0) or (guessed_wrong(current_guess)):
        return True
    else:
        return False


def guessed_wrong(current_guess):
    game_state_colors = app.config["game_state"]["colors"]
    current_turn = app.config["game_state"]["current_turn"]
    if current_turn == "blue" and game_state_colors[current_guess] == "R":
        return True
    elif current_turn == "red" and game_state_colors[current_guess] == "U":
        return True
    else:
        return False


def game_over(updated_state, current_guess):
    # TODO
    pass


@socketio.on("connect")
def handle_connect():
    player_id = session.get("player_id", request.remote_addr)
    if player_id in players:
        emit("player_info", players[player_id])


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
