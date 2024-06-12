CREATE TABLE IF NOT EXISTS "games" (
	id integer PRIMARY KEY,
	code text UNIQUE NOT NULL,
	colors text NOT NULL, -- URRRURUA...
	words text NOT NULL, -- space-sep string
	guessed text NOT NULL, -- string of 25 T/F
	guesses_left integer NOT NULL DEFAULT 0,
	curr_turn text NOT NULL DEFAULT 'blue',
	curr_clue text NOT NULL DEFAULT ';-1', -- clue;num (empty string and -1 means no clue yet)
	game_state text NOT NULL DEFAULT ''
);
-- get all history for given game id, they're sorted by asc id, but not necessarily seq
CREATE TABLE IF NOT EXISTS "history" (
	id integer PRIMARY KEY,
	game integer NOT NULL, -- keyed to games.id
	head text NOT NULL, -- head/entry are freeform key/value pair such as: "new clue": "(turtle, 2)"
	entry text NOT NULL	
);