-- SQLite
CREATE TABLE resultstwo (id INTEGER, game_id INTEGER, home_team_results TEXT, away_team_results TEXT, home_team_score INTEGER, away_team_score INTEGER, results_date DATE, status BOOL, FOREIGN KEY (game_id) REFERENCES games (id), PRIMARY KEY (id)); 