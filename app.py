from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import pudb

# from codenames.cnai import Spymaster, W2VAssoc, W2VGuesser
# from codenames.cngame import Codenames

app = Flask(__name__)

app.secret_key = "859c86bf1895e69b3c6dfc1c6092a3b3c45d9b55f22ac29aa816ed87793c00b8"
socketio = SocketIO(app)


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
@app.get("/create")
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
        "guesses_remaining": 0,
    }
    game()
    return redirect(url_for("game"))


@app.route("/game")
def game():
    if "game_state" not in app.config:
        create_game()
    return render_template("game.html", game_state=app.config["game_state"])


@app.post("/update_game_state")
def update_game_state():
    updated_state = request.get_json()
    app.config["game_state"].update(updated_state)

    socketio.emit("update", app.config["game_state"])

    # Return the updated game state back to the client
    return jsonify(app.config["game_state"])


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
