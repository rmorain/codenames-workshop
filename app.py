import os
import secrets
import sqlite3
from pathlib import Path
from random import choice, randint, sample, shuffle
from string import punctuation

from flask import (
    Blueprint,
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from nltk.stem.snowball import SnowballStemmer

"""
logger = logging.getLogger('werkzeug')
handler = logging.FileHandler('codenames.log')
logger.addHandler(handler)

"""
app = Flask(__name__)
# Define allowed origins based on environment
print(os.environ.get("FLASK_ENV"))
app.config["FLASK_ENV"] = os.environ.get("FLASK_ENV")
if os.environ.get("FLASK_ENV") == "development":
    url_prefix = ""
    allowed_origins = ["http://127.0.0.1:5000", "http://localhost:5000"]
else:
    url_prefix = "/codenames"
    allowed_origins = ["https://mind.cs.byu.edu"]

codenames = Blueprint(
    "codenames",
    __name__,
    url_prefix=url_prefix,
    static_folder="static",
    template_folder="templates",
)
app.register_blueprint(codenames)

SECRET_FILE_PATH = Path(".flask_secret")
print(SECRET_FILE_PATH)

try:
    with SECRET_FILE_PATH.open("r") as secret_file:
        print("Reading secret key")
        app.secret_key = secret_file.read()
except FileNotFoundError:
    with SECRET_FILE_PATH.open("w") as secret_file:
        print("creating secret key")
        app.secret_key = secrets.token_hex(32)
        secret_file.write(app.secret_key)


# Apply CORS configuration
CORS(app, origins=allowed_origins)

# Configure Socket.IO
socketio = SocketIO(
    app,
    async_mode="gevent",
    cors_allowed_origins=allowed_origins,
    path="/socket.io",  # Match your blueprint URL prefix
)

print("Socketio", socketio)

stemmer = SnowballStemmer(language="english")

# = database ================

DATABASE = "cn.db"


def get_db():
    if "db" not in g:
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
    db.commit()  # if it's slow, maybe move this to teardown_appcontext instead?
    return id


@app.teardown_appcontext
def close_connection(e):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# ===========================


@app.route("/")
def index():
    print("Render index")
    return render_template("index.html")


# global consts
BOARD_SIZE = 25
CLUE_SEP = ";"
GAME_OVER_STATE = "GAME OVER"

words = [
    "hollywood",
    "well",
    "foot",
    "new_york",
    "spring",
    "court",
    "tube",
    "point",
    "tablet",
    "slip",
    "date",
    "drill",
    "lemon",
    "bell",
    "screen",
    "fair",
    "torch",
    "state",
    "match",
    "iron",
    "block",
    "france",
    "australia",
    "limousine",
    "stream",
    "glove",
    "nurse",
    "leprechaun",
    "play",
    "tooth",
    "arm",
    "bermuda",
    "diamond",
    "whale",
    "comic",
    "mammoth",
    "green",
    "pass",
    "missile",
    "paste",
    "drop",
    "pheonix",
    "marble",
    "staff",
    "figure",
    "park",
    "centaur",
    "shadow",
    "fish",
    "cotton",
    "egypt",
    "theater",
    "scale",
    "fall",
    "track",
    "force",
    "dinosaur",
    "bill",
    "mine",
    "turkey",
    "march",
    "contract",
    "bridge",
    "robin",
    "line",
    "plate",
    "band",
    "fire",
    "bank",
    "boom",
    "cat",
    "shot",
    "suit",
    "chocolate",
    "roulette",
    "mercury",
    "moon",
    "net",
    "lawyer",
    "satellite",
    "angel",
    "spider",
    "germany",
    "fork",
    "pitch",
    "king",
    "crane",
    "trip",
    "dog",
    "conductor",
    "part",
    "bugle",
    "witch",
    "ketchup",
    "press",
    "spine",
    "worm",
    "alps",
    "bond",
    "pan",
    "beijing",
    "racket",
    "cross",
    "seal",
    "aztec",
    "maple",
    "parachute",
    "hotel",
    "berry",
    "soldier",
    "ray",
    "post",
    "greece",
    "square",
    "mass",
    "bat",
    "wave",
    "car",
    "smuggler",
    "england",
    "crash",
    "tail",
    "card",
    "horn",
    "capital",
    "fence",
    "deck",
    "buffalo",
    "microscope",
    "jet",
    "duck",
    "ring",
    "train",
    "field",
    "gold",
    "tick",
    "check",
    "queen",
    "strike",
    "kangaroo",
    "spike",
    "scientist",
    "engine",
    "shakespeare",
    "wind",
    "kid",
    "embassy",
    "robot",
    "note",
    "ground",
    "draft",
    "ham",
    "war",
    "mouse",
    "center",
    "chick",
    "china",
    "bolt",
    "spot",
    "piano",
    "pupil",
    "plot",
    "lion",
    "police",
    "head",
    "litter",
    "concert",
    "mug",
    "vacuum",
    "atlantis",
    "straw",
    "switch",
    "skyscraper",
    "laser",
    "scuba_diver",
    "africa",
    "plastic",
    "dwarf",
    "lap",
    "life",
    "honey",
    "horseshoe",
    "unicorn",
    "spy",
    "pants",
    "wall",
    "paper",
    "sound",
    "ice",
    "tag",
    "web",
    "fan",
    "orange",
    "temple",
    "canada",
    "scorpion",
    "undertaker",
    "mail",
    "europe",
    "soul",
    "apple",
    "pole",
    "tap",
    "mouth",
    "ambulance",
    "dress",
    "ice_cream",
    "rabbit",
    "buck",
    "agent",
    "sock",
    "nut",
    "boot",
    "ghost",
    "oil",
    "superhero",
    "code",
    "kiwi",
    "hospital",
    "saturn",
    "film",
    "button",
    "snowman",
    "helicopter",
    "loch_ness",
    "log",
    "princess",
    "time",
    "cook",
    "revolution",
    "shoe",
    "mole",
    "spell",
    "grass",
    "washer",
    "game",
    "beat",
    "hole",
    "horse",
    "pirate",
    "link",
    "dance",
    "fly",
    "pit",
    "server",
    "school",
    "lock",
    "brush",
    "pool",
    "star",
    "jam",
    "organ",
    "berlin",
    "face",
    "luck",
    "amazon",
    "cast",
    "gas",
    "club",
    "sink",
    "water",
    "chair",
    "shark",
    "jupiter",
    "copper",
    "jack",
    "platypus",
    "stick",
    "olive",
    "grace",
    "bear",
    "glass",
    "row",
    "pistol",
    "london",
    "rock",
    "van",
    "vet",
    "beach",
    "charge",
    "port",
    "disease",
    "palm",
    "moscow",
    "pin",
    "washington",
    "pyramid",
    "opera",
    "casino",
    "pilot",
    "string",
    "night",
    "chest",
    "yard",
    "teacher",
    "pumpkin",
    "thief",
    "bark",
    "bug",
    "mint",
    "cycle",
    "telescope",
    "calf",
    "air",
    "box",
    "mount",
    "thumb",
    "antarctica",
    "trunk",
    "snow",
    "penguin",
    "root",
    "bar",
    "file",
    "hawk",
    "battery",
    "compound",
    "slug",
    "octopus",
    "whip",
    "america",
    "ivory",
    "pound",
    "sub",
    "cliff",
    "lab",
    "eagle",
    "genius",
    "ship",
    "dice",
    "hood",
    "heart",
    "novel",
    "pipe",
    "himalayas",
    "crown",
    "round",
    "india",
    "needle",
    "shop",
    "watch",
    "lead",
    "tie",
    "table",
    "cell",
    "cover",
    "czech",
    "back",
    "bomb",
    "ruler",
    "forest",
    "bottle",
    "space",
    "hook",
    "doctor",
    "ball",
    "bow",
    "degree",
    "rome",
    "plane",
    "giant",
    "nail",
    "dragon",
    "stadium",
    "flute",
    "carrot",
    "wake",
    "fighter",
    "model",
    "tokyo",
    "eye",
    "mexico",
    "hand",
    "swing",
    "key",
    "alien",
    "tower",
    "poison",
    "cricket",
    "cold",
    "knife",
    "church",
    "board",
    "cloak",
    "ninja",
    "olympus",
    "belt",
    "light",
    "death",
    "stock",
    "millionaire",
    "day",
    "knight",
    "pie",
    "bed",
    "circle",
    "rose",
    "change",
    "cap",
    "triangle",
]


def genCode(length=4):
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(choice(letters) for i in range(length))


def emptyClue():
    return {"word": "", "number": -1}


def loadState(code):
    values = query_db("SELECT * FROM games WHERE code=?", (code,), one=True)
    if not values:
        return None
    labels = [
        "id",
        "code",
        "colors",
        "words",
        "guessed",
        "guesses_left",
        "curr_turn",
        "curr_clue",
        "game_state",
    ]
    state = dict(zip(labels, values))

    # decode from DB format where necessary
    state["colors"] = list(state["colors"])
    state["words"] = state["words"].split(" ")
    state["guessed"] = [True if b == "T" else False for b in state["guessed"]]
    clue_word, clue_num = state["curr_clue"].split(CLUE_SEP)
    state["curr_clue"] = {"word": clue_word, "number": int(clue_num)}

    return state


# common function to convert guessed and clue parts of state for db upsert
def encodeGuessClue(state):
    guessed = "".join("T" if b else "F" for b in state["guessed"])
    curr_clue = state["curr_clue"]
    clue = curr_clue["word"] + CLUE_SEP + str(curr_clue["number"])
    return guessed, clue


# existing game
def updateState(state):
    guessed, clue = encodeGuessClue(state)
    args = (
        guessed,
        state["guesses_left"],
        state["curr_turn"],
        clue,
        state["game_state"],
        state["code"],
    )
    exec_db(
        "UPDATE games SET guessed=?, guesses_left=?, curr_turn=?, curr_clue=?, game_state=? WHERE code=?",
        args,
    )


# new game
def insertState(state):
    colors = "".join(state["colors"])
    words = " ".join(state["words"])
    guessed, clue = encodeGuessClue(state)
    args = (
        state["code"],
        colors,
        words,
        guessed,
        state["guesses_left"],
        state["curr_turn"],
        clue,
        state["game_state"],
    )
    id = exec_db(
        "INSERT INTO games (code,colors,words,guessed,guesses_left,curr_turn,curr_clue,game_state) VALUES(?,?,?,?,?,?,?,?)",
        args,
    )
    return id


# (not going to bother with the preset board layout cards)
def newBoard(blueFirst=True):
    # I don't know how many red/blue for anything other than 5x5

    colors = ["U"] * 8 + ["R"] * 8 + ["N"] * 7 + ["A"]
    colors += ["U"] if blueFirst else ["R"]
    shuffle(colors)

    selected = sample(words, BOARD_SIZE)

    return colors, selected


# writes key/value to history table
def writeHist(state, head, entry):
    exec_db(
        "INSERT INTO history (game,head,entry) VALUES(?,?,?)",
        (state["id"], head, entry),
    )


# Create new game and insert into DB
@app.route("/create")
def create_game():
    role = request.args.get("role")
    team = request.args.get("team")
    blueStarts = bool(randint(0, 1))
    colors, words = newBoard(blueStarts)
    while True:
        code = genCode()
        # make sure it's not already in the DB
        exists = query_db("SELECT id FROM games WHERE code=?", (code,), one=True)
        if not exists:
            break

    state = {
        "code": code,
        "colors": colors,
        "words": words,
        "guessed": [False] * BOARD_SIZE,
        "guesses_left": 0,
        "curr_turn": "blue" if blueStarts else "red",
        "curr_clue": emptyClue(),
        "game_state": "",  # only GAME OVER or INVALID
    }
    state["id"] = insertState(state)
    writeHist(state, "new game", "game started")
    game_url = url_for("game", code=state["code"], role=role, team=team)
    if url_prefix:
        game_url = url_prefix + game_url
    return redirect(game_url)


@app.route("/game")
def game():
    code = request.args.get("code")
    state = loadState(code)
    if not state:
        return errMsg("Game not found"), 404

    # Assign a role and team to the player
    role = request.args.get("role")
    team = request.args.get("team")

    return render_template(
        "game.html",
        game_state=state,
        player_role=role,
        player_team=team,
        game_code=state["code"],
    )


@app.route("/getgames")
def get_games():
    codes = query_db(
        "SELECT code FROM games WHERE game_state !=? OR game_state IS NULL",
        (GAME_OVER_STATE,),
    )
    return jsonify([c[0] for c in codes])  # one-item tuple to just item


@app.route("/get_game_state")
def get_game_state():
    code = request.args.get("code")
    state = loadState(code)
    if not state:
        return errMsg("Game not found"), 404
    return jsonify(state)


# =============================================
# function to submit clue
#   - This needs to support both HTML client from this app *and* python client! So...
#   - If any part of submission is malformed, will return simple error message.
#       `return "error message", 400`
#   - HTML client should display error message and then refresh current state
#       (nothing should have changed, but that's up to server)
#   - Python client needs to try again...


def isValid(word, board_words):
    word_stem = stemmer.stem(word)
    for w in board_words:
        curr_stem = stemmer.stem(w)
        if word == w or word_stem == curr_stem:
            return False
    return True


def isEmpty(clue):
    return clue["word"] == "" and clue["number"] < 0


def errMsg(msg):
    return jsonify({"error": msg})


# POST json should be {code:__, team:__, word:__, number:__}
@app.post("/make_clue")
def make_clue():
    data = request.get_json()
    # try:
    orig = ""  # origin: html (human) or py (AI)
    if "orig" in data:
        orig = data["orig"]
    code = data["code"]
    state = loadState(code)
    if not state:
        return errMsg("Game not found"), 404
    team = data["team"]
    if team != state["curr_turn"] or not isEmpty(state["curr_clue"]):
        return errMsg("Clue not needed"), 400
    word = data["word"].lower().strip()
    number = int(data["number"])
    if team == "blue":
        max_num = len([color for color in state["colors"] if color == "U"])
    else:
        max_num = len([color for color in state["colors"] if color == "R"])
    if number < 1 or number > max_num:
        return errMsg("Invalid clue number"), 400
    # validate word
    bad_word = any(p in word for p in punctuation + " \t\r\n")
    if bad_word or not isValid(word, state["words"]):
        m = errMsg("Invalid clue word")
        return m, 400
    # filling in clue changes game state
    state["curr_clue"]["word"] = word
    state["curr_clue"]["number"] = number
    state["guesses_left"] = number + 1
    updateState(state)
    writeHist(
        state, "new clue", orig + " " + team + ": (" + word + " " + str(number) + ")"
    )
    socketio.emit("update", state, room=code)
    return jsonify(state)

    # except:
    #    return errMsg("Error recording clue"), 400


# =============================================


def recordGameOver(state, winner):
    state["game_state"] = GAME_OVER_STATE
    updateState(state)
    writeHist(state, "game over", "game over: " + winner)


def switchTurn(state):
    state["curr_clue"] = emptyClue()
    state["guesses_left"] = 0
    if state["curr_turn"] == "blue":
        state["curr_turn"] = "red"
    else:
        state["curr_turn"] = "blue"


@app.post("/pass")
def make_pass():
    data = request.get_json()
    code = data["code"]
    state = loadState(code)
    if not state:
        return errMsg("Game not found"), 404

    team = data["team"]
    if team != state["curr_turn"] or state["guesses_left"] < 1:
        return errMsg("Can't pass now"), 400

    switchTurn(state)

    updateState(state)
    writeHist(state, "pass", team)

    socketio.emit("update", state, room=code)
    return jsonify(state)


@app.post("/make_guess")
def make_guess():
    data = request.get_json()
    code = data["code"]
    state = loadState(code)
    if not state:
        return errMsg("Game not found"), 404

    team = data["team"]
    if team != state["curr_turn"] or state["guesses_left"] < 1:
        return errMsg("Guess not needed"), 400

    current_guess = int(data["guess"])

    current_guess = data["guess"]
    state["guessed"][current_guess] = True
    state["guesses_left"] -= 1
    # Check if game is over
    winner = is_game_over(state, current_guess)
    if winner:
        recordGameOver(state, winner)
        output = {"game_state": state, "winner": winner}
        socketio.emit("game_end", output, room=code)
        socketio.emit("update", state, room=code)
        return jsonify(output)
    # Check if we need to change turn
    if should_change_turn(state, current_guess):
        switchTurn(state)

    updateState(state)
    guess_word = state["words"][current_guess]
    guess_color = state["colors"][current_guess]
    writeHist(
        state,
        "new guess",
        team + ": " + str(current_guess) + " " + guess_word + " " + guess_color,
    )

    socketio.emit("update", state, room=code)
    return jsonify(state)


def should_change_turn(state, current_guess):
    if (state["guesses_left"] == 0) or (guessed_wrong(state, current_guess)):
        return True
    else:
        return False


def guessed_wrong(state, current_guess):
    game_state_colors = state["colors"]
    current_turn = state["curr_turn"]
    if current_turn == "blue" and game_state_colors[current_guess] != "U":
        return True
    elif current_turn == "red" and game_state_colors[current_guess] != "R":
        return True
    else:
        return False


def is_game_over(state, current_guess):
    red_words_guessed = [
        color
        for color, guess in zip(state["colors"], state["guessed"])
        if guess and color == "R"
    ]
    blue_words_guessed = [
        color
        for color, guess in zip(state["colors"], state["guessed"])
        if guess and color == "U"
    ]
    red_words_total = [color for color in state["colors"] if color == "R"]
    blue_words_total = [color for color in state["colors"] if color == "U"]

    # Assassin is picked
    if state["colors"][current_guess] == "A":
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
    print("Client connected")
    pass


@socketio.on("join_room")
def handle_join_room(code):
    join_room(code)
    print(f"Joined room: {code}")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
