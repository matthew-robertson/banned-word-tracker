CREATE TABLE 'server_banned_word' (
	banned_word Varchar NOT NULL,
	server_id Varchar NOT NULL,
	infracted_at Varchar NOT NULL,
  	calledout_at Varchar NOT NULL,
	FOREIGN KEY(server_id) REFERENCES server(server_id)
);

INSERT INTO server_banned_word (server_id, banned_word, infracted_at, calledout_at)
SELECT server_id, 'vore' as banned_word, infracted_at, calledout_at from server;

