from flask import Flask, render_template, jsonify, request, redirect, url_for, session, g
from flask_socketio import SocketIO, emit, join_room, leave_room
import pudb, sqlite3

# from codenames.cnai import Spymaster, W2VAssoc, W2VGuesser
# from codenames.cngame import Codenames
app = Flask(__name__)

app.secret_key = "859c86bf1895e69b3c6dfc1c6092a3b3c45d9b55f22ac29aa816ed87793c00b8"
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

players = {}

#= database ================
#copied from gbspend/hieros_human/p2hierosserver.py

DATABASE = 'cn.db'

def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(DATABASE)
	return g.db

def query_db(query, args=(), one=False):
	cur = get_db().cursor()
	cur.execute(query, args)
	rv = cur.fetchall()
	return (rv[0] if rv else None) if one else rv

def exec_db(query, args=()):
	db = get_db()
	c = db.cursor()
	c.execute(query, args)
	id = c.lastrowid
	db.commit() #if it's slow, maybe move this to teardown_appcontext instead?
	return id

@app.teardown_appcontext
def close_connection(e):
	db = g.pop('db', None)
	if db is not None:
		db.close()

#===========================

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error':'Not found'}), 404)


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
    if "gameState" in data.keys():
        updated_state = data["gameState"]
        current_guess = data["currentGuess"]
        # Check if game is over
        winner = game_over(updated_state, current_guess)
        if winner:
            socketio.emit("game_end", {"winner": winner})
            return jsonify({"game_state": updated_state, "winner": winner})
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


def game_over(game_state, current_guess):
    red_words_guessed = [
        color
        for color, guess in zip(game_state["colors"], game_state["guessed"])
        if guess and color == "R"
    ]
    blue_words_guessed = [
        color
        for color, guess in zip(game_state["colors"], game_state["guessed"])
        if guess and color == "U"
    ]
    red_words_total = [color for color in game_state["colors"] if color == "R"]
    blue_words_total = [color for color in game_state["colors"] if color == "U"]

    # Assassin is picked
    if game_state["colors"][current_guess] == "A":
        # Opposite team wins
        return "assassin"
    # Red team wins
    elif len(red_words_guessed) == len(red_words_total):
        return "red"
    # Blue team wins
    elif len(blue_words_guessed) == len(blue_words_total):
        return "blue"
    else:
        return None


@socketio.on("connect")
def handle_connect():
    player_id = session.get("player_id", request.remote_addr)
    if player_id in players:
        emit("player_info", players[player_id])


if __name__ == "__main__":
    socketio.run(app, host="", port=8000)
