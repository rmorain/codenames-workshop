from flask import Flask, session, render_template

# from codenames.cnai import Spymaster, W2VAssoc, W2VGuesser
# from codenames.cngame import Codenames

app = Flask(__name__)

app.secret_key = "859c86bf1895e69b3c6dfc1c6092a3b3c45d9b55f22ac29aa816ed87793c00b8"


@app.route("/")
def index():
    return "Welcome to the Codenames workshop!"


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


@app.get("/state")
def get_game_state():
    print(app.config["codenames"])
    return "Getting game state"


@app.post("/clue")
def post_clue():
    return "Posting clue"


@app.post("/guess")
def post_guess():
    return "Posting guess"

@app.route("/game")
def game():
    return render_template("game.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0")
