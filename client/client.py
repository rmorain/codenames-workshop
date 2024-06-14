import requests
from sys import argv
import socketio
from socketio.exceptions import TimeoutError
from cnai import getAI

# == HELPERS ===============================


def isEmpty(clue):
    return clue["word"] == "" and clue["number"] < 0


# turn the game state into board dict
def makeBoard(state):
    board = {"U": [], "R": [], "N": [], "A": []}
    for i in range(BOARD_SIZE):
        if state["guessed"][i]:
            continue
        color = state["colors"][i]
        word = state["words"][i]
        board[color].append(word)
    return board


# == CONSTS ================================

BOARD_SIZE = 25

SERVER_URL = "http://localhost:5000"
GET_STATE_URL = SERVER_URL + "/get_game_state?code="  # get
MAKE_CLUE_URL = SERVER_URL + "/make_clue"  # post

USAGE = "Usage: <game code> <'red' | 'blue'>"


# run from command line: give code and team, then it plays the whole game :)
# client should run until game over, then terminate
if __name__ == "__main__":
    if len(argv) < 3:
        print(USAGE)
        exit(1)
    code = argv[1]
    team = argv[2].lower()
    if team not in ["red", "blue"]:
        print(USAGE)
        exit(1)

    ai = getAI()

    with socketio.SimpleClient() as sio:
        sio.connect(SERVER_URL)
        print("SID: ", sio.sid)

        sio.emit("join_room", code)
        print("Joined room:", code)

        print("Starting game loop. Use Ctrl+C to exit early")
        response = requests.get(GET_STATE_URL + code)
        state = response.json()
        # two ways to update state: direct response or socketio update event

        while True:
            curr_clue = state["curr_clue"]
            if state["curr_turn"] == team and isEmpty(curr_clue):
                print("making clue...")
                board = makeBoard(state)
                clue, intended_words = ai.makeClue(board, team == "blue")
                print("clue: " + str(clue))
                for w in intended_words:
                    print("\t", w)
                # POST json should be {code:__, team:__, word:__, number:__}
                args = {
                    "orig": "py",
                    "code": code,
                    "team": team,
                    "word": clue[0],
                    "number": clue[1],
                }
                r = requests.post(MAKE_CLUE_URL, json=args)
                state = r.json()
            try:
                # from the docs:
                # receive() only returns when an event is received from the server
                event = sio.receive(timeout=5)  # without timeout, user can't ctrl+c
                event_name = event[0]
                data = event[1]  # should only ever be one json object
                if event_name == "update":
                    state = data
                elif event_name == "game_end":
                    state = data["game_state"]
                    winner = data["winner"]
                    print(winner + " won!")
                    break
            except TimeoutError:
                pass
