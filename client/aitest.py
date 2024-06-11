#based on gbspend/codenames/main/cngame.py

from random import randint, sample, shuffle, seed
from cnai import Spymaster, W2VAssoc
from sys import argv

row_col = 5
BOARD_SIZE = row_col ** 2

words = [
    "hollywood", "well", "foot", "new_york", "spring", "court", "tube", "point", "tablet", "slip", "date", "drill", "lemon", "bell", "screen",
    "fair", "torch", "state", "match", "iron", "block", "france", "australia", "limousine", "stream", "glove", "nurse", "leprechaun", "play",
    "tooth", "arm", "bermuda", "diamond", "whale", "comic", "mammoth", "green", "pass", "missile", "paste", "drop", "pheonix", "marble", "staff",
    "figure", "park", "centaur", "shadow", "fish", "cotton", "egypt", "theater", "scale", "fall", "track", "force", "dinosaur", "bill", "mine",
    "turkey", "march", "contract", "bridge", "robin", "line", "plate", "band", "fire", "bank", "boom", "cat", "shot", "suit", "chocolate",
    "roulette", "mercury", "moon", "net", "lawyer", "satellite", "angel", "spider", "germany", "fork", "pitch", "king", "crane", "trip", "dog",
    "conductor", "part", "bugle", "witch", "ketchup", "press", "spine", "worm", "alps", "bond", "pan", "beijing", "racket", "cross", "seal",
    "aztec", "maple", "parachute", "hotel", "berry", "soldier", "ray", "post", "greece", "square", "mass", "bat", "wave", "car", "smuggler",
    "england", "crash", "tail", "card", "horn", "capital", "fence", "deck", "buffalo", "microscope", "jet", "duck", "ring", "train", "field",
    "gold", "tick", "check", "queen", "strike", "kangaroo", "spike", "scientist", "engine", "shakespeare", "wind", "kid", "embassy", "robot",
    "note", "ground", "draft", "ham", "war", "mouse", "center", "chick", "china", "bolt", "spot", "piano", "pupil", "plot", "lion", "police",
    "head", "litter", "concert", "mug", "vacuum", "atlantis", "straw", "switch", "skyscraper", "laser", "scuba_diver", "africa", "plastic",
    "dwarf", "lap", "life", "honey", "horseshoe", "unicorn", "spy", "pants", "wall", "paper", "sound", "ice", "tag", "web", "fan", "orange",
    "temple", "canada", "scorpion", "undertaker", "mail", "europe", "soul", "apple", "pole", "tap", "mouth", "ambulance", "dress", "ice_cream",
    "rabbit", "buck", "agent", "sock", "nut", "boot", "ghost", "oil", "superhero", "code", "kiwi", "hospital", "saturn", "film", "button",
    "snowman", "helicopter", "loch_ness", "log", "princess", "time", "cook", "revolution", "shoe", "mole", "spell", "grass", "washer", "game",
    "beat", "hole", "horse", "pirate", "link", "dance", "fly", "pit", "server", "school", "lock", "brush", "pool", "star", "jam", "organ",
    "berlin", "face", "luck", "amazon", "cast", "gas", "club", "sink", "water", "chair", "shark", "jupiter", "copper", "jack", "platypus",
    "stick", "olive", "grace", "bear", "glass", "row", "pistol", "london", "rock", "van", "vet", "beach", "charge", "port", "disease", "palm",
    "moscow", "pin", "washington", "pyramid", "opera", "casino", "pilot", "string", "night", "chest", "yard", "teacher", "pumpkin", "thief",
    "bark", "bug", "mint", "cycle", "telescope", "calf", "air", "box", "mount", "thumb", "antarctica", "trunk", "snow", "penguin", "root", "bar",
    "file", "hawk", "battery", "compound", "slug", "octopus", "whip", "america", "ivory", "pound", "sub", "cliff", "lab", "eagle", "genius",
    "ship", "dice", "hood", "heart", "novel", "pipe", "himalayas", "crown", "round", "india", "needle", "shop", "watch", "lead", "tie", "table",
    "cell", "cover", "czech", "back", "bomb", "ruler", "forest", "bottle", "space", "hook", "doctor", "ball", "bow", "degree", "rome", "plane",
    "giant", "nail", "dragon", "stadium", "flute", "carrot", "wake", "fighter", "model", "tokyo", "eye", "mexico", "hand", "swing", "key",
    "alien", "tower", "poison", "cricket", "cold", "knife", "church", "board", "cloak", "ninja", "olympus", "belt", "light", "death", "stock",
    "millionaire", "day", "knight", "pie", "bed", "circle", "rose", "change", "cap", "triangle"
]
#longest word is 11 chars

#provide colors to capitalize blue words
def printBoard(selected,colors=None):
    max_width = len(sorted(selected,key=lambda s:len(s), reverse=True)[0])+1
    line = []
    for i in range(len(selected)):
        curr = selected[i]
        if colors and colors[i] == 'U':
            curr = curr.upper()
        line.append(f"{curr:{max_width}}")
        if len(line) % row_col == 0:
            print(" ".join(line))
            line = []

#===============================================

def runTrial():
    #blue first
    colors = ['U']*9 + ['R']*8 + ['N']*7 + ['A']

    shuffle(colors)

    selected = sample(words, BOARD_SIZE)
    covered = [False] * BOARD_SIZE

    board = {'U':[], 'R':[], 'N':[], 'A':[]}
    for i in range(BOARD_SIZE):
        if covered[i]:
            continue
        color = colors[i]
        word = selected[i]
        board[color].append(word)

    m = Spymaster(W2VAssoc())
    hint, combo = m.makeHint(board, True)
    return selected, colors, board, hint, combo

if __name__ == "__main__":
    s = randint(1,10000) #funny, but you can't GET seed from random
    if len(argv) > 1:
        try:
            s = int(argv[1])
        except ValueError:
            pass
    seed(s)
    print("Seed:",s)
    
    selected, colors, board, hint, combo = runTrial()
    print()
    printBoard(selected)

    print(hint)
    print()

    input("Press Enter to reveal answer(s)...\n")

    printBoard(selected, colors)

    print(", ".join(combo))

