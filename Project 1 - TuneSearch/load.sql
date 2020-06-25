DROP TABLE IF EXISTS artist CASCADE;
DROP TABLE IF EXISTS token CASCADE;
DROP TABLE IF EXISTS song CASCADE;
DROP TABLE IF EXISTS tfidf CASCADE;

CREATE TABLE artist (
	artist_id INTEGER PRIMARY KEY,
	artist_name VARCHAR(255)
);


CREATE TABLE token (
	song_id INTEGER,
	token VARCHAR(255),
	count INTEGER,
	PRIMARY KEY (song_id, token)
);

CREATE TABLE song (
	song_id INTEGER PRIMARY KEY,
	artist_id INTEGER REFERENCES artist(artist_id),
	song_name VARCHAR(255),
	page_link VARCHAR(1000)
	/* , FOREIGN KEY (artist_id) REFERENCES artist (artist_id) */
);

CREATE TABLE tfidf (
	song_id INTEGER,
	token VARCHAR(255),
	score FLOAT,
	PRIMARY KEY(song_id, token)
);

\copy artist FROM '/home/cs143/data/artist.csv' DELIMITER ',' QUOTE '"' CSV;
\copy song   FROM '/home/cs143/data/song.csv'   DELIMITER ',' QUOTE '"' CSV;
\copy token  FROM '/home/cs143/data/token.csv'  DELIMITER ',' QUOTE '"' CSV;

CREATE TABLE IF NOT EXISTS ranking AS (
	SELECT IDF, R.token,
		T.count AS TF,
		T.song_id,
		S.song_name,
		artist_name
		
			FROM (
			SELECT COUNT(*) AS IDF, token
				FROM token GROUP BY token
				ORDER BY IDF DESC
		) R JOIN token T ON R.token = T.token
		    JOIN Song S ON T.song_id = S.song_id
		    JOIN artist A ON S.artist_id = A.artist_id
		    	ORDER BY IDF DESC, TF DESC
);

ALTER TABLE ranking ADD IF NOT EXISTS tfidf float;
UPDATE ranking SET tfidf = TF * LOG((SELECT Count(*) FROM song) / CAST(IDF AS FLOAT)); 
