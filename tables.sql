CREATE TABLE IF NOT EXISTS "games" (
	id integer PRIMARY KEY,
	colors text NOT NULL, -- just save as a space-sep string
	words text NOT NULL, -- ditto
	guessed integer NOT NULL DEFAULT 0, -- int as list of 25 bools (0/1)
	guess_remain integer NOT NULL DEFAULT 0,
	blue_turn BOOLEAN NOT NULL DEFAULT 0,
	curr_clue text NOT NULL
);
-- get all history for given game id, they're sorted by asc id, but not necessarily seq
CREATE TABLE IF NOT EXISTS "history" (
	id integer PRIMARY KEY,
	game integer NOT NULL, -- keyed to games.id
	action text NOT NULL, -- action/entry are freeform key/value pair such as: "new clue": "(turtle, 2)"
	entry text NOT NULL	
);