-- SQLite
INSERT INTO historytwo (id, username_id, h_results_id, bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner) SELECT id, username_id, h_results_id, bet_name, bet_amount, transaction_date, odds, potential_payout, home_team_history, away_team_history, match_date, winner FROM history;