from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Codenames workshop!"

@app.route("/start")
def start_game():
    return "Starting game!"

@app.get("/state")
def get_game_state():
    return "Getting game state"

@app.post("/clue")
def post_clue():
    return "Posting clue"

@app.post("/guess")
def post_guess():
    return "Posting guess"

if __name__ == "__main__":
    app.run(host="0.0.0.0")